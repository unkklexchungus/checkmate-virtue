#!/bin/bash

# Automotive Service-Based Architecture Quick Start Script

set -e

echo "🚀 Starting Automotive Service-Based Architecture Setup"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Build and start services
echo "🔨 Building and starting services..."
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
services=(
    "postgres:5432"
    "redis:6379"
    "auth-service:8001"
    "customer-service:8002"
    "vehicle-service:8003"
    "appointment-service:8004"
    "workshop-service:8005"
    "inventory-service:8006"
    "notification-service:8007"
    "api-gateway:8080"
)

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    echo -n "Checking $service_name... "
    
    # Wait for service to be ready
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            echo "✅"
            break
        fi
        
        if [ $timeout -eq 60 ]; then
            echo -n "⏳"
        fi
        
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌"
        echo "Service $service_name failed to start"
        exit 1
    fi
done

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "🌐 Access Points:"
echo "  • API Gateway:     http://localhost:8080"
echo "  • API Documentation: http://localhost:8080/docs"
echo "  • Auth Service:    http://localhost:8001"
echo "  • Customer Service: http://localhost:8002"
echo "  • Vehicle Service: http://localhost:8003"
echo "  • Workshop Service: http://localhost:8005"
echo "  • pgAdmin:         http://localhost:5050"
echo ""
echo "🔧 Management Commands:"
echo "  • View logs:       docker compose logs -f"
echo "  • Stop services:   docker compose down"
echo "  • Restart:         docker compose restart"
echo "  • Update:          docker compose pull && docker compose up -d"
echo ""
echo "🧪 Test the system:"
echo "  • Run tests:       python test_system.py"
echo ""
echo "📚 Next Steps:"
echo "  1. Open http://localhost:8080/docs to explore the API"
echo "  2. Register a user at http://localhost:8080/v1/auth/register"
echo "  3. Create customers and vehicles"
echo "  4. Generate estimates and invoices"
echo ""
echo "💡 Tips:"
echo "  • Check logs with: docker compose logs <service-name>"
echo "  • Access database: docker compose exec postgres psql -U appuser -d appdb"
echo "  • Monitor resources: docker stats"
echo ""
echo "🚀 System is ready for development!"
