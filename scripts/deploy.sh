#!/bin/bash

# Deployment script for Telegram Bar Bot
# This script handles the complete deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-""}
EMAIL=${2:-""}
ENV_FILE=".env"

print_usage() {
    echo "Usage: $0 <domain> <email> [--dev]"
    echo "Example: $0 mybot.example.com admin@example.com"
    echo "         $0 localhost admin@localhost.com --dev"
    echo ""
    echo "Options:"
    echo "  --dev    Development deployment (self-signed certificates)"
    echo ""
    echo "This script will:"
    echo "1. Check prerequisites"
    echo "2. Set up SSL certificates"
    echo "3. Build and start services"
    echo "4. Run database migrations"
    echo "5. Set up Telegram webhook"
}

check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠️  .env file not found, creating from template...${NC}"
        cp .env.production .env
        echo -e "${RED}❌ Please edit .env file with your configuration and run again${NC}"
        exit 1
    fi
    
    # Check if TELEGRAM_BOT_TOKEN is set
    if ! grep -q "TELEGRAM_BOT_TOKEN=" "$ENV_FILE" || grep -q "your_.*_token_here" "$ENV_FILE"; then
        echo -e "${RED}❌ Please set TELEGRAM_BOT_TOKEN in .env file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

setup_ssl() {
    local domain=$1
    local email=$2
    local dev_mode=$3
    
    echo -e "${BLUE}🔐 Setting up SSL certificates...${NC}"
    
    if [ "$dev_mode" = "true" ]; then
        echo -e "${YELLOW}📝 Development mode: using self-signed certificates${NC}"
        ./scripts/setup_ssl.sh "$domain" "$email"
    else
        echo -e "${YELLOW}📝 Production mode: follow Let's Encrypt instructions${NC}"
        ./scripts/setup_ssl.sh "$domain" "$email"
        
        echo -e "${YELLOW}⚠️  Please set up Let's Encrypt certificates manually and press Enter to continue...${NC}"
        read -r
    fi
}

build_and_start() {
    echo -e "${BLUE}🏗️  Building and starting services...${NC}"
    
    # Build the application
    docker-compose build --no-cache
    
    # Start database first
    docker-compose up -d postgres
    
    # Wait for database to be ready
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
    sleep 10
    
    # Run database migrations
    echo -e "${BLUE}🗄️  Running database migrations...${NC}"
    docker-compose run --rm webapp alembic upgrade head
    
    # Start all services
    docker-compose up -d
    
    # Wait for services to be ready
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 15
}

setup_webhook() {
    local domain=$1
    
    echo -e "${BLUE}🔗 Setting up Telegram webhook...${NC}"
    
    # Update webhook URL in environment
    sed -i "s|TELEGRAM_WEBHOOK_URL=.*|TELEGRAM_WEBHOOK_URL=https://$domain/webhook|" "$ENV_FILE"
    
    # Restart webapp to pick up new environment
    docker-compose restart webapp
    sleep 5
    
    # Set up webhook
    docker-compose exec webapp python scripts/setup_webhook.py set
    
    # Verify webhook
    docker-compose exec webapp python scripts/setup_webhook.py info
}

show_status() {
    echo -e "\n${GREEN}🎉 Deployment completed!${NC}"
    echo -e "\n${BLUE}📊 Service Status:${NC}"
    docker-compose ps
    
    echo -e "\n${BLUE}📋 Useful Commands:${NC}"
    echo "  View logs:           docker-compose logs -f"
    echo "  Restart services:    docker-compose restart"
    echo "  Stop services:       docker-compose down"
    echo "  Update webhook:      docker-compose exec webapp python scripts/setup_webhook.py set"
    echo "  Check webhook:       docker-compose exec webapp python scripts/setup_webhook.py info"
    echo "  Database shell:      docker-compose exec postgres psql -U barbot -d telegram_bar_bot"
    echo "  App shell:           docker-compose exec webapp bash"
    
    echo -e "\n${BLUE}🌐 Access Points:${NC}"
    echo "  Mini App:            https://$1/"
    echo "  API Docs:            https://$1/docs"
    echo "  Health Check:        https://$1/health"
    echo "  Webhook URL:         https://$1/webhook"
}

main() {
    local dev_mode=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                dev_mode=true
                shift
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            *)
                if [ -z "$DOMAIN" ]; then
                    DOMAIN=$1
                elif [ -z "$EMAIL" ]; then
                    EMAIL=$1
                fi
                shift
                ;;
        esac
    done
    
    if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
        echo -e "${RED}❌ Error: Domain and email are required${NC}"
        print_usage
        exit 1
    fi
    
    echo -e "${GREEN}🚀 Starting deployment for Telegram Bar Bot${NC}"
    echo -e "${GREEN}🌐 Domain: $DOMAIN${NC}"
    echo -e "${GREEN}📧 Email: $EMAIL${NC}"
    echo -e "${GREEN}🔧 Mode: $([ "$dev_mode" = "true" ] && echo "Development" || echo "Production")${NC}"
    echo ""
    
    check_prerequisites
    setup_ssl "$DOMAIN" "$EMAIL" "$dev_mode"
    build_and_start
    setup_webhook "$DOMAIN"
    show_status "$DOMAIN"
}

main "$@"