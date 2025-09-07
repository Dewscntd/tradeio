#!/bin/bash

# Production deployment script for AI Trading Bot

set -e

echo "🚀 Starting deployment..."

# Environment setup
export COMPOSE_PROJECT_NAME=trading_bot
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Create necessary directories
mkdir -p ssl logs data

# Generate SSL certificates (Let's Encrypt)
if [ ! -f ssl/fullchain.pem ]; then
    echo "📜 Generating SSL certificates..."
    certbot certonly --standalone -d yourdomain.com --email your@email.com --agree-tos
    cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
    cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🗄️ Starting database..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 10

echo "🔄 Running database migrations..."
docker-compose exec backend alembic upgrade head

echo "🌱 Seeding initial data..."
docker-compose exec backend python -m app.scripts.seed_data

echo "🚀 Starting all services..."
docker-compose up -d

echo "✅ Deployment complete!"
echo "📊 Dashboard: https://yourdomain.com"
echo "📚 API Docs: https://yourdomain.com/docs"
echo "🔍 Logs: docker-compose logs -f"
