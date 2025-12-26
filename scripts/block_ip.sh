#!/bin/bash

# Script to manage IP blocking in nginx
# Usage: ./block_ip.sh [add|remove|list] [IP]

NGINX_CONF="nginx.conf"
BACKUP_CONF="nginx.conf.backup"

case "$1" in
    "add")
        if [ -z "$2" ]; then
            echo "Usage: $0 add <IP_ADDRESS>"
            exit 1
        fi
        
        IP="$2"
        echo "Adding IP $IP to blocklist..."
        
        # Create backup
        cp "$NGINX_CONF" "$BACKUP_CONF"
        
        # Add IP to geo block
        sed -i "/# Add specific IPs that should be blocked/a\\        $IP 1;  # Blocked $(date)" "$NGINX_CONF"
        
        # Reload nginx
        docker-compose -f docker-compose.yml exec nginx nginx -s reload
        
        echo "IP $IP blocked successfully"
        ;;
        
    "remove")
        if [ -z "$2" ]; then
            echo "Usage: $0 remove <IP_ADDRESS>"
            exit 1
        fi
        
        IP="$2"
        echo "Removing IP $IP from blocklist..."
        
        # Create backup
        cp "$NGINX_CONF" "$BACKUP_CONF"
        
        # Remove IP from geo block
        sed -i "/$IP 1;/d" "$NGINX_CONF"
        
        # Reload nginx
        docker-compose -f docker-compose.yml exec nginx nginx -s reload
        
        echo "IP $IP unblocked successfully"
        ;;
        
    "list")
        echo "Currently blocked IPs:"
        grep -E "^\s+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\s+1;" "$NGINX_CONF" | sed 's/^[[:space:]]*//' | sed 's/ 1;.*//'
        ;;
        
    "auto-block")
        echo "Analyzing nginx logs for suspicious IPs..."
        
        # Get IPs with high request rates or attack patterns
        SUSPICIOUS_IPS=$(docker-compose -f docker-compose.yml logs nginx 2>/dev/null | \
            grep -E "(404|400|403|444)" | \
            grep -oE "([0-9]{1,3}\.){3}[0-9]{1,3}" | \
            sort | uniq -c | sort -nr | \
            awk '$1 > 10 {print $2}' | head -10)
        
        if [ -n "$SUSPICIOUS_IPS" ]; then
            echo "Found suspicious IPs with high error rates:"
            echo "$SUSPICIOUS_IPS"
            
            read -p "Block these IPs? (y/N): " confirm
            if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
                for ip in $SUSPICIOUS_IPS; do
                    $0 add "$ip"
                done
            fi
        else
            echo "No suspicious IPs found"
        fi
        ;;
        
    *)
        echo "Usage: $0 [add|remove|list|auto-block] [IP]"
        echo ""
        echo "Commands:"
        echo "  add <IP>      - Block specific IP address"
        echo "  remove <IP>   - Unblock specific IP address"
        echo "  list          - List all blocked IPs"
        echo "  auto-block    - Analyze logs and suggest IPs to block"
        echo ""
        echo "Examples:"
        echo "  $0 add 1.2.3.4"
        echo "  $0 remove 1.2.3.4"
        echo "  $0 list"
        echo "  $0 auto-block"
        exit 1
        ;;
esac