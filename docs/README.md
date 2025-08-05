# CheckMate Virtue Documentation

## Overview

CheckMate Virtue is a professional multi-industry inspection system built with FastAPI. This application provides comprehensive inspection capabilities across various industries including automotive, construction, healthcare, and more.

## Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Architecture

### Project Structure

```
CheckMate-Virtue/
├── app/                    # Main application package
│   ├── api/               # API routes and endpoints
│   ├── models/            # Pydantic data models
│   ├── services/          # Business logic services
│   ├── utils/             # Utility functions
│   ├── config.py          # Application configuration
│   └── main.py            # Application entry point
├── config/                # Environment-specific configs
│   ├── dev/              # Development configuration
│   └── prod/             # Production configuration
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── .github/              # CI/CD workflows
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Local development setup
└── requirements.txt      # Python dependencies
```

### Key Components

- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation and settings management
- **Jinja2**: Template engine for HTML rendering
- **ReportLab**: PDF generation for reports
- **Uvicorn**: ASGI server for running the application

## Installation

### Prerequisites

- Python 3.9+
- pip
- Docker (optional)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-org/checkmate-virtue.git
cd checkmate-virtue
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python -m app.main
```

### Docker Development

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the application at `http://localhost:8000`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8000 |
| `RAILWAY_ENVIRONMENT` | Environment type | development |
| `SESSION_SECRET_KEY` | Session encryption key | auto-generated |
| `DATABASE_URL` | Database connection string | None |
| `SMTP_HOST` | Email server host | None |
| `SMTP_PORT` | Email server port | 587 |
| `SMTP_USERNAME` | Email username | None |
| `SMTP_PASSWORD` | Email password | None |

### Configuration Files

- `app/config.py`: Main configuration with Pydantic settings
- `config/dev/config.py`: Development-specific settings
- `config/prod/config.py`: Production-specific settings

## API Documentation

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

### Endpoints

#### Inspections
- `GET /api/v1/inspections` - List all inspections
- `POST /api/v1/inspections` - Create new inspection
- `GET /api/v1/inspections/{id}` - Get inspection by ID
- `PUT /api/v1/inspections/{id}` - Update inspection
- `POST /api/v1/inspections/{id}/photos` - Upload photos
- `POST /api/v1/inspections/{id}/submit` - Submit inspection
- `GET /api/v1/inspections/{id}/report` - Generate report
- `GET /api/v1/inspections/{id}/report/pdf` - Generate PDF report

#### Vehicles
- `GET /api/v1/vehicles/decode/{vin}` - Decode VIN
- `GET /api/v1/vehicles/test-vin` - VIN test page

#### Invoices
- `GET /api/v1/invoices` - List all invoices
- `POST /api/v1/invoices` - Create new invoice
- `GET /api/v1/invoices/{id}` - Get invoice by ID
- `PUT /api/v1/invoices/{id}` - Update invoice
- `GET /api/v1/invoices/clients` - List all clients
- `POST /api/v1/invoices/clients` - Create new client

### Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Code Style

This project follows PEP 8 with the following tools:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_inspection_service.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/
```

## Testing

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and workflows
- **Fixtures**: Reusable test data and setup

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with coverage report
pytest --cov=app --cov-report=xml --cov-report=html
```

## Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t checkmate-virtue .
```

2. Run the container:
```bash
docker run -p 8000:8000 checkmate-virtue
```

### Environment Variables for Production

```bash
RAILWAY_ENVIRONMENT=production
SESSION_SECRET_KEY=your-secure-secret-key
DATABASE_URL=your-database-url
SMTP_HOST=your-smtp-host
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
```

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests and quality checks
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature`
8. Create a Pull Request

### Commit Message Convention

Use conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

### Branch Naming Convention

- `main`: Production-ready code
- `develop`: Development branch
- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `hotfix/urgent-fix`: Critical fixes

## License

This project is licensed under the MIT License - see the LICENSE file for details. 