#!/bin/bash

# SSL Certificate Setup Script for Telegram Bar Bot
# This script helps set up SSL certificates using Let's Encrypt

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}
SSL_DIR="./ssl"

print_usage() {
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 mybot.example.com admin@example.com"
    echo ""
    echo "This script will:"
    echo "1. Create SSL directory structure"
    echo "2. Generate self-signed certificates for development"
    echo "3. Provide instructions for Let's Encrypt certificates"
}

create_ssl_directory() {
    echo -e "${YELLOW}Creating SSL directory structure...${NC}"
    mkdir -p "$SSL_DIR"
    chmod 700 "$SSL_DIR"
}

generate_self_signed_cert() {
    echo -e "${YELLOW}Generating self-signed certificate for development...${NC}"
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/key.pem" 2048
    
    # Generate certificate
    openssl req -new -x509 -key "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem" -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    # Set proper permissions
    chmod 600 "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    
    echo -e "${GREEN}✅ Self-signed certificate generated successfully!${NC}"
    echo -e "${YELLOW}⚠️  Note: Self-signed certificates are for development only!${NC}"
}

print_letsencrypt_instructions() {
    echo -e "\n${YELLOW}📋 For production, use Let's Encrypt certificates:${NC}"
    echo ""
    echo "1. Install certbot:"
    echo "   sudo apt-get update"
    echo "   sudo apt-get install certbot"
    echo ""
    echo "2. Stop nginx if running:"
    echo "   docker-compose stop nginx"
    echo ""
    echo "3. Generate Let's Encrypt certificate:"
    echo "   sudo certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive"
    echo ""
    echo "4. Copy certificates to SSL directory:"
    echo "   sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/cert.pem"
    echo "   sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/key.pem"
    echo "   sudo chown \$(whoami):\$(whoami) $SSL_DIR/*.pem"
    echo ""
    echo "5. Set up auto-renewal:"
    echo "   sudo crontab -e"
    echo "   # Add this line:"
    echo "   0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook \"docker-compose restart nginx\""
    echo ""
    echo "6. Start nginx:"
    echo "   docker-compose up -d nginx"
}

print_webhook_setup() {
    echo -e "\n${YELLOW}📋 After SSL setup, configure webhook:${NC}"
    echo ""
    echo "1. Update .env file with your domain:"
    echo "   TELEGRAM_WEBHOOK_URL=https://$DOMAIN/webhook"
    echo ""
    echo "2. Set up webhook:"
    echo "   python scripts/setup_webhook.py set"
    echo ""
    echo "3. Verify webhook:"
    echo "   python scripts/setup_webhook.py info"
}

main() {
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        print_usage
        exit 0
    fi
    
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo -e "${RED}❌ Error: Domain and email are required${NC}"
        print_usage
        exit 1
    fi
    
    echo -e "${GREEN}🔐 Setting up SSL certificates for domain: $DOMAIN${NC}"
    echo -e "${GREEN}📧 Email: $EMAIL${NC}"
    echo ""
    
    create_ssl_directory
    generate_self_signed_cert
    print_letsencrypt_instructions
    print_webhook_setup
    
    echo -e "\n${GREEN}✅ SSL setup completed!${NC}"
    echo -e "${YELLOW}⚠️  Remember to update your .env file with the correct domain${NC}"
}

main "$@"