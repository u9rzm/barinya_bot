#!/bin/bash

# Docker and System Logs Cleanup Script
# This script cleans up Docker container logs and system journal logs

set -e

echo "=== Docker and System Logs Cleanup ==="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Clean Docker container logs
clean_docker_logs() {
    echo ">>> Cleaning Docker container logs..."
    
    if ! command_exists docker; then
        echo "Docker is not installed. Skipping Docker logs cleanup."
        return
    fi
    
    # Get size of Docker logs before cleanup
    local before_size=$(docker system df -v 2>/dev/null | grep -i "logs" | awk '{sum += $NF} END {print sum}' || echo "0")
    
    # Truncate all Docker container log files
    for container_log in $(docker inspect --format='{{.LogPath}}' $(docker ps -aq) 2>/dev/null); do
        if [ -f "$container_log" ]; then
            truncate -s 0 "$container_log" 2>/dev/null || true
        fi
    done
    
    # Clean Docker system (optional - removes stopped containers, unused networks, dangling images)
    # Uncomment the following line if you want to clean more aggressively
    # docker system prune -f
    
    echo "Docker container logs cleaned."
}

# Clean Docker daemon logs (if applicable)
clean_docker_daemon_logs() {
    echo ">>> Cleaning Docker daemon logs..."
    
    local docker_log_paths=(
        "/var/log/docker.log"
        "/var/log/docker"
        "/var/log/containers"
        "/var/log/pods"
    )
    
    for log_path in "${docker_log_paths[@]}"; do
        if [ -d "$log_path" ]; then
            find "$log_path" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
        elif [ -f "$log_path" ]; then
            truncate -s 0 "$log_path" 2>/dev/null || true
        fi
    done
    
    echo "Docker daemon logs cleaned."
}

# Clean system journal logs
clean_system_logs() {
    echo ">>> Cleaning system journal logs..."
    
    if ! command_exists journalctl; then
        echo "journalctl is not available. Skipping system logs cleanup."
        return
    fi
    
    # Get journal size before cleanup
    local before_size=$(journalctl --disk-usage 2>/dev/null | awk '{print $NF}' || echo "unknown")
    echo "Journal size before cleanup: $before_size"
    
    # Vacuum journal logs, keeping only last 3 days
    journalctl --vacuum-time=3d 2>/dev/null || true
    
    # Alternative: keep only last 500MB
    # journalctl --vacuum-size=500M 2>/dev/null || true
    
    local after_size=$(journalctl --disk-usage 2>/dev/null | awk '{print $NF}' || echo "unknown")
    echo "Journal size after cleanup: $after_size"
    
    echo "System journal logs cleaned."
}

# Clean common system log files
clean_var_logs() {
    echo ">>> Cleaning /var/log files..."
    
    local log_files=(
        "/var/log/syslog"
        "/var/log/messages"
        "/var/log/auth.log"
        "/var/log/kern.log"
        "/var/log/daemon.log"
        "/var/log/debug"
        "/var/log/user.log"
    )
    
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            # Rotate and truncate logs older than 7 days
            find /var/log -name "*.log" -mtime +7 -exec truncate -s 0 {} \; 2>/dev/null || true
        fi
    done
    
    # Clean rotated logs (old compressed logs)
    find /var/log -name "*.gz" -mtime +7 -delete 2>/dev/null || true
    find /var/log -name "*.1" -mtime +7 -delete 2>/dev/null || true
    
    echo "/var/log files cleaned."
}

# Main execution
main() {
    echo "Starting cleanup process..."
    echo ""
    
    # Check if running as root (needed for some operations)
    if [ "$EUID" -ne 0 ]; then
        echo "Warning: Not running as root. Some operations may fail."
        echo "Consider running with: sudo $0"
        echo ""
    fi
    
    clean_docker_logs
    echo ""
    
    clean_docker_daemon_logs
    echo ""
    
    clean_system_logs
    echo ""
    
    clean_var_logs
    echo ""
    
    echo "=== Cleanup Complete ==="
    
    # Show disk usage summary
    echo ""
    echo "Disk usage summary:"
    if command_exists docker; then
        echo "Docker disk usage:"
        docker system df 2>/dev/null || true
        echo ""
    fi
    
    if command_exists du; then
        echo "Log directory sizes:"
        du -sh /var/log 2>/dev/null || echo "/var/log: not accessible"
    fi
}

# Run main function
main "$@"
