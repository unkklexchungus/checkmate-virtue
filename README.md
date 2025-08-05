# CheckMate Virtue

[![CI](https://github.com/your-org/checkmate-virtue/workflows/CI/badge.svg)](https://github.com/your-org/checkmate-virtue/actions)
[![Deploy](https://github.com/your-org/checkmate-virtue/workflows/Deploy/badge.svg)](https://github.com/your-org/checkmate-virtue/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> Professional Multi-Industry Inspection System

CheckMate Virtue is a comprehensive web application for professional inspections across multiple industries including automotive, construction, healthcare, manufacturing, and more. Built with FastAPI and modern Python practices.

## 🚀 Features

- **Multi-Industry Support**: Automotive, Construction, Healthcare, Manufacturing, Real Estate, IT/Data Centers, Environmental, Food Safety
- **VIN Decoding**: Advanced vehicle identification number decoding with comprehensive vehicle data
- **Photo Management**: Upload and organize inspection photos
- **PDF Reports**: Generate professional PDF inspection reports
- **Invoice System**: Complete invoicing and client management
- **RESTful API**: Modern API with automatic documentation
- **Responsive UI**: Mobile-friendly web interface
- **Docker Support**: Containerized deployment
- **CI/CD Ready**: Automated testing and deployment

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ⚡ Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/checkmate-virtue.git
cd checkmate-virtue

# Start the application
docker-compose up --build

# Access the application
open http://localhost:8000
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-org/checkmate-virtue.git
cd checkmate-virtue

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the application
python -m app.main
```

## 🛠 Installation

### Prerequisites

- Python 3.9+
- pip
- Docker (optional, for containerized deployment)

### Dependencies

The application uses the following key dependencies:

- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation and settings management
- **Jinja2**: Template engine for HTML rendering
- **ReportLab**: PDF generation for reports
- **Uvicorn**: ASGI server for running the application

See [requirements.txt](requirements.txt) for the complete list.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Server Configuration
PORT=8000
HOST=0.0.0.0

# Environment
RAILWAY_ENVIRONMENT=development

# Security
SESSION_SECRET_KEY=your-secret-key-change-in-production

# Database (for future expansion)
DATABASE_URL=

# Email (for future expansion)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# File Storage
STORAGE_TYPE=local
CLOUD_STORAGE_URL=
```

### Configuration Files

- `app/config.py`: Main application configuration
- `config/dev/config.py`: Development-specific settings
- `config/prod/config.py`: Production-specific settings

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Inspections
```
GET    /api/v1/inspections          # List all inspections
POST   /api/v1/inspections          # Create new inspection
GET    /api/v1/inspections/{id}     # Get inspection by ID
PUT    /api/v1/inspections/{id}     # Update inspection
POST   /api/v1/inspections/{id}/photos  # Upload photos
POST   /api/v1/inspections/{id}/submit   # Submit inspection
GET    /api/v1/inspections/{id}/report   # Generate report
GET    /api/v1/inspections/{id}/report/pdf  # Generate PDF report
```

#### Vehicles
```
GET    /api/v1/vehicles/decode/{vin}  # Decode VIN
GET    /api/v1/vehicles/test-vin      # VIN test page
```

#### Invoices
```
GET    /api/v1/invoices              # List all invoices
POST   /api/v1/invoices              # Create new invoice
GET    /api/v1/invoices/{id}         # Get invoice by ID
PUT    /api/v1/invoices/{id}         # Update invoice
GET    /api/v1/invoices/clients      # List all clients
POST   /api/v1/invoices/clients      # Create new client
```

## 🏗 Development

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
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── .github/              # CI/CD workflows
├── Dockerfile            # Container configuration
└── docker-compose.yml    # Local development setup
```

### Code Quality

This project follows modern Python development practices:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **pytest**: Testing framework

### Development Commands

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Install pre-commit hooks
pre-commit install
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with coverage report
pytest --cov=app --cov-report=xml --cov-report=html

# Run with verbose output
pytest -v
```

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and workflows
- **Fixtures**: Reusable test data and setup

## 🚀 Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Docker Deployment

```bash
# Build the Docker image
docker build -t checkmate-virtue .

# Run the container
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

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests and quality checks
6. Commit your changes: `git commit -m "feat: add your feature"`
7. Push to your fork: `git push origin feature/your-feature`
8. Create a Pull Request

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [ReportLab](https://www.reportlab.com/) for PDF generation
- [Railway](https://railway.app/) for hosting and deployment

## 📞 Support

- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/checkmate-virtue/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/checkmate-virtue/discussions)

---

**CheckMate Virtue** - Professional Multi-Industry Inspection System 