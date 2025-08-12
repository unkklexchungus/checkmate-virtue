# Automotive Service-Based Architecture

A modern, microservices-based automotive management system built with FastAPI, SQLModel, PostgreSQL, and Docker Compose.

## 🏗️ Architecture Overview

This system is built as a collection of focused microservices, each handling a specific domain:

- **API Gateway**: Single entry point for all client requests
- **Customer Service**: Customer and contact management
- **Vehicle Service**: Vehicle data and VIN decoding
- **Appointment Service**: Appointment scheduling and calendar management
- **Workshop Service**: Estimates, work orders, and invoice lifecycle
- **Inventory Service**: Parts catalog and supplier management
- **Notification Service**: Email/SMS notifications and templating

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Lexicon-Re-clone
cp env.example .env
```

### 2. Configure Base URL

The application uses `APP_BASE_URL` as a single source of truth for all service URLs:

**For Local Development:**
```bash
export APP_BASE_URL=http://127.0.0.1:8000
```

**For Docker Compose:**
```bash
export APP_BASE_URL=http://api-gateway:8000
```

**For Individual Services:**
```bash
export APP_BASE_URL=http://customer-service:8000  # For customer service
export APP_BASE_URL=http://vehicle-service:8000   # For vehicle service
# etc.
```

This configuration ensures consistent URL handling across all environments and prevents IPv6/IPv4 connection issues.

### 3. Start the System

```bash
# Start all services
docker compose up --build

# Or start in background
docker compose up -d --build
```

### 4. Verify Services

Check that all services are running:

```bash
docker compose ps
```

You can also check the health of individual services:

```bash
# Check API Gateway health
curl http://localhost:8080/healthz

# Check individual service health
curl http://localhost:8002/healthz  # Customer Service
curl http://localhost:8003/healthz  # Vehicle Service
# etc.
```

### 5. Access Services

- **API Gateway**: http://localhost:8080
- **Customer Service**: http://localhost:8002
- **Vehicle Service**: http://localhost:8003
- **Appointment Service**: http://localhost:8004
- **Workshop Service**: http://localhost:8005
- **Inventory Service**: http://localhost:8006
- **Notification Service**: http://localhost:8007
- **pgAdmin**: http://localhost:5050 (admin@automotive.com / admin123)

## 📋 Service Details

### API Gateway (Port 8080)
- Routes requests to appropriate services
- Handles authentication and authorization
- Provides unified API documentation
- Manages CORS and rate limiting



### Customer Service (Port 8002)
- Customer management
- Contact information
- Address management
- Search and pagination

**Key Endpoints:**
- `GET /v1/customers` - List customers
- `POST /v1/customers` - Create customer
- `GET /v1/customers/{id}` - Get customer details
- `PUT /v1/customers/{id}` - Update customer
- `DELETE /v1/customers/{id}` - Delete customer

### Vehicle Service (Port 8003)
- Vehicle data management
- VIN decoding
- Vehicle specifications
- Trim and engine data

**Key Endpoints:**
- `GET /v1/vehicles` - List vehicles
- `POST /v1/vehicles` - Create vehicle
- `GET /v1/vehicles/decode/{vin}` - Decode VIN
- `GET /v1/vehicles/{id}` - Get vehicle details

### Workshop Service (Port 8005)
- Estimate creation and management
- Work order lifecycle
- Invoice generation
- Payment tracking

**Key Endpoints:**
- `GET /v1/workshop/estimates` - List estimates
- `POST /v1/workshop/estimates` - Create estimate
- `POST /v1/workshop/estimates/{id}/convert` - Convert to work order
- `GET /v1/workshop/work-orders` - List work orders
- `POST /v1/workshop/work-orders/{id}/convert` - Convert to invoice
- `GET /v1/workshop/invoices` - List invoices

## 🔧 Development

### Local Development Setup

1. **Install Dependencies**
```bash
# For each service
cd services/auth-service
pip install poetry
poetry install
```

2. **Database Migrations**
```bash
# Run migrations for each service
cd services/auth-service
alembic upgrade head
```

3. **Environment Variables**
```bash
# Copy and customize environment variables
cp env.example .env
# Edit .env with your local settings
```

### Testing

The project includes comprehensive testing with health checks and browser automation:

#### Health Check System
All services include a `/healthz` endpoint that returns `{"status": "ok"}` when healthy.

#### Browser Testing
```bash
# Run browser tests with health check
python qa/run_browser_tests.py

# Run custom test example
python qa/test_example.py

# Run health check unit tests
python qa/test_health_check.py
```

#### CI Pipeline
```bash
# Run complete CI pipeline (starts server, waits for health, runs tests)
./qa/ci_test.sh
```

#### Manual Health Check
```bash
# Check if service is healthy
curl http://127.0.0.1:8000/healthz

# Wait for service to become healthy (with timeout)
python qa/health_check.py
```

#### Service-Specific Tests
```bash
# Run tests for a specific service
cd services/auth-service
pytest

# Run all tests
pytest services/*/tests/
```

### Code Quality

```bash
# Format code
black services/
ruff check services/

# Type checking
mypy services/
```

## 📊 Database Schema

Each service has its own schema in the shared PostgreSQL database:

- `auth` - Authentication and user management
- `customers` - Customer and contact data
- `vehicles` - Vehicle information and VIN data
- `appointments` - Appointment scheduling
- `workshop` - Estimates, work orders, invoices
- `inventory` - Parts and supplier data
- `notifications` - Notification queue and templates

## 🔐 Authentication

The system uses JWT tokens for authentication:

1. **Register/Login** to get access and refresh tokens
2. **Include Bearer token** in Authorization header
3. **Refresh tokens** when access tokens expire

Example:
```bash
# Login
curl -X POST http://localhost:8080/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token
curl -X GET http://localhost:8080/v1/customers \
  -H "Authorization: Bearer <access_token>"
```

## 🚗 Example Workflow

### 1. Create Customer
```bash
curl -X POST http://localhost:8080/v1/customers \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "company": "ABC Corp",
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "90210"
    },
    "contact": {
      "phone": "555-123-4567",
      "email": "john@abc.com"
    }
  }'
```

### 2. Add Vehicle
```bash
curl -X POST http://localhost:8080/v1/vehicles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1HGBH41JXMN109186",
    "year": "2021",
    "make": "Honda",
    "model": "Civic"
  }'
```

### 3. Create Appointment
```bash
curl -X POST http://localhost:8080/v1/appointments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "vehicle_id": 1,
    "appointment_date": "2024-01-15T10:00:00Z",
    "service_type": "oil_change"
  }'
```

### 4. Create Estimate
```bash
curl -X POST http://localhost:8080/v1/workshop/estimates \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "vehicle_id": 1,
    "appointment_id": 1,
    "items": [
      {
        "description": "Oil Change",
        "quantity": 1,
        "unit_price": 29.99
      }
    ]
  }'
```

## 🛠️ Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check logs
   docker compose logs <service-name>
   
   # Restart specific service
   docker compose restart <service-name>
   ```

2. **Database connection issues**
   ```bash
   # Check PostgreSQL logs
   docker compose logs postgres
   
   # Access database directly
   docker compose exec postgres psql -U appuser -d appdb
   ```

3. **Port conflicts**
   ```bash
   # Check what's using a port
   lsof -i :8080
   
   # Change ports in docker-compose.yml
   ```

### Health Checks

All services provide health check endpoints:
- `GET /health` - Basic health status
- `GET /ready` - Readiness check (includes database)

## 📈 Monitoring

### Service Health
```bash
# Check all services
curl http://localhost:8080/health
curl http://localhost:8001/health
# ... etc for each service
```

### Database Monitoring
- Access pgAdmin at http://localhost:5050
- Connect to PostgreSQL using:
  - Host: `postgres`
  - Port: `5432`
  - Username: `appuser`
  - Password: `apppass`
  - Database: `appdb`

## 🔄 Deployment

### Production Considerations

1. **Environment Variables**
   - Change default passwords
   - Use strong JWT secrets
   - Configure proper CORS origins

2. **Security**
   - Enable HTTPS
   - Use proper SSL certificates
   - Configure firewall rules

3. **Scaling**
   - Use load balancers
   - Configure database replication
   - Set up monitoring and alerting

### Docker Production Build

```bash
# Build production images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🧪 Testing

### Browser Testing Suite

The project includes a comprehensive browser testing system using Playwright for end-to-end testing:

```bash
# Install testing dependencies
pip install playwright
playwright install

# Run browser tests (headless)
python qa/run_browser_tests.py

# Run with visible browser
HEADLESS=false python qa/run_browser_tests.py

# Run custom test scenarios
python qa/test_example.py
```

**Features:**
- **End-to-end browser testing** of all public and authenticated routes
- **Error logging by service and type** (JS errors, network errors, HTTP errors, etc.)
- **Automatic screenshot capture** for first error per page
- **Service detection** from API request URLs
- **Retry logic** with exponential backoff
- **Comprehensive reporting** in JSON and human-readable formats

**Test Coverage:**
- Public routes (home, industries, inspections, invoices)
- API endpoints (VIN decoding, inspection creation, invoice creation)
- Form submissions and interactions
- Authentication flows (if available)

**Output:**
- `qa/logs/error-log.json` - Structured JSON format
- `qa/logs/error-log.txt` - Human-readable format
- `qa/logs/screenshots/` - Error screenshots

For detailed testing documentation, see [qa/README.md](qa/README.md).

## 📚 API Documentation

Each service provides its own OpenAPI documentation:

- **API Gateway**: http://localhost:8080/docs
- **Auth Service**: http://localhost:8001/docs
- **Customer Service**: http://localhost:8002/docs
- **Vehicle Service**: http://localhost:8003/docs
- **Workshop Service**: http://localhost:8005/docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting section

---

**Note**: This is a development setup. For production deployment, ensure proper security configurations, monitoring, and backup strategies are in place. 