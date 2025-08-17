# Docker Test Environment for CheckMate Virtue

This document describes how to run all tests exclusively in Docker containers for the CheckMate Virtue inspection system.

## 🐳 Overview

The Docker test environment provides a completely isolated testing environment that includes:
- **Test Database**: PostgreSQL for test data
- **Test Cache**: Redis for caching
- **Test Application**: Main application running in test mode
- **Test Runners**: Separate containers for different test types
- **Browser Automation**: Playwright with all browsers installed

## 📋 Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM
- 10GB of available disk space

## 🚀 Quick Start

### Run All Tests
```bash
# Run all tests (browser, API, health checks, Playwright)
./scripts/run-tests-docker.sh --all
```

### Run Specific Test Types
```bash
# Browser tests only
./scripts/run-tests-docker.sh --browser

# API tests only
./scripts/run-tests-docker.sh --api

# Health checks only
./scripts/run-tests-docker.sh --health

# Playwright tests only
./scripts/run-tests-docker.sh --playwright
```

### Debug Mode
```bash
# Run with visible browser (headed mode)
./scripts/run-tests-docker.sh --browser --headed

# Run with extended timeouts for debugging
./scripts/run-tests-docker.sh --browser --debug
```

## 🛠️ Manual Docker Commands

### Start Test Environment
```bash
# Start all test services
docker-compose -f docker-compose.test.yml up -d

# Start only infrastructure (database, redis)
docker-compose -f docker-compose.test.yml up -d test-postgres test-redis
```

### Run Tests Manually
```bash
# Run browser tests
docker-compose -f docker-compose.test.yml run --rm test-runner

# Run API tests
docker-compose -f docker-compose.test.yml run --rm api-test-runner

# Run health checks
docker-compose -f docker-compose.test.yml run --rm health-monitor

# Run Playwright tests
docker-compose -f docker-compose.test.yml run --rm playwright-runner
```

### View Logs
```bash
# View all container logs
./scripts/run-tests-docker.sh --logs

# View specific service logs
docker-compose -f docker-compose.test.yml logs -f test-app
docker-compose -f docker-compose.test.yml logs -f test-runner
```

### Clean Up
```bash
# Stop all containers
./scripts/run-tests-docker.sh --stop

# Clean up containers and volumes
./scripts/run-tests-docker.sh --clean

# Manual cleanup
docker-compose -f docker-compose.test.yml down -v --remove-orphans
docker system prune -f
```

## 🏗️ Architecture

### Test Services

| Service | Port | Description |
|---------|------|-------------|
| `test-postgres` | 5433 | Test database |
| `test-redis` | 6380 | Test cache |
| `test-app` | 8001 | Main application in test mode |
| `test-runner` | - | Browser test runner |
| `playwright-runner` | - | Playwright test runner |
| `api-test-runner` | - | API test runner |
| `health-monitor` | - | Health check monitor |

### Network Configuration
- **Internal Network**: `test_net` for inter-service communication
- **Service Discovery**: Services communicate using container names
- **Port Mapping**: External ports mapped to avoid conflicts with development

## 🔧 Configuration

### Environment Variables

The test environment uses these environment variables:

```bash
# Application
APP_BASE_URL=http://test-app:8000
TESTING=true
HEADLESS=true
TIMEOUT=30000
WAIT_FOR_IDLE=2000
RETRY_ATTEMPTS=2

# Database
DATABASE_URL=postgresql://testuser:testpass@test-postgres:5432/testdb

# Cache
REDIS_URL=redis://test-redis:6379/0

# Test URLs
FRONTEND_URL=http://test-app:8000
BACKEND_URL=http://test-app:8000
```

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./static/uploads` | `/app/static/uploads` | Photo uploads |
| `./qa/artifacts` | `/app/qa/artifacts` | Test artifacts |
| `./qa/logs` | `/app/qa/logs` | Test logs |
| `./temp` | `/app/temp` | Temporary files |
| `./test-results` | `/app/test-results` | Test results |

## 📊 Test Results

### Artifacts Location
- **Screenshots**: `qa/artifacts/`
- **Logs**: `qa/logs/`
- **Test Results**: `test-results/`
- **Playwright Reports**: `playwright-report/`

### Viewing Results
```bash
# View test artifacts
ls -la qa/artifacts/

# View test logs
ls -la qa/logs/

# View Playwright report
open playwright-report/index.html
```

## 🔍 Debugging

### Debug Mode
```bash
# Run with debug settings
./scripts/run-tests-docker.sh --debug

# This sets:
# - TIMEOUT=60000 (60 seconds)
# - WAIT_FOR_IDLE=5000 (5 seconds)
# - Extended logging
```

### Headed Mode
```bash
# Run with visible browser
./scripts/run-tests-docker.sh --headed

# This sets:
# - HEADLESS=false
# - Browser will be visible during tests
```

### Container Access
```bash
# Access test application container
docker exec -it test_app bash

# Access test runner container
docker exec -it test_runner bash

# View real-time logs
docker logs -f test_app
```

## 🧹 Maintenance

### Regular Cleanup
```bash
# Weekly cleanup
./scripts/run-tests-docker.sh --clean

# Remove unused images
docker image prune -f

# Remove unused volumes
docker volume prune -f
```

### Update Dependencies
```bash
# Rebuild test image
docker-compose -f docker-compose.test.yml build --no-cache

# No npm packages - Python only
```

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check if ports are in use
netstat -tulpn | grep :8001
netstat -tulpn | grep :5433

# Kill processes using ports
sudo kill -9 <PID>
```

#### Container Health Issues
```bash
# Check container health
docker-compose -f docker-compose.test.yml ps

# Restart unhealthy containers
docker-compose -f docker-compose.test.yml restart test-app
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER qa/artifacts qa/logs temp

# Fix script permissions
chmod +x scripts/run-tests-docker.sh
```

#### Memory Issues
```bash
# Check Docker memory usage
docker stats

# Increase Docker memory limit in Docker Desktop
# Settings > Resources > Memory: 4GB+
```

### Performance Optimization

#### Parallel Execution
```bash
# Run tests in parallel (if supported)
docker-compose -f docker-compose.test.yml run --rm test-runner \
    python3 -m pytest -n auto
```

#### Resource Limits
```bash
# Limit container resources
docker-compose -f docker-compose.test.yml run --rm \
    --memory=2g --cpus=2 test-runner
```

## 📝 CI/CD Integration

### GitHub Actions Example
```yaml
name: Docker Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Docker Tests
        run: |
          ./scripts/run-tests-docker.sh --clean --all
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: qa/artifacts/
```

### Local CI Simulation
```bash
# Simulate CI environment
export CI=true
./scripts/run-tests-docker.sh --clean --all
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Playwright Docker Guide](https://playwright.dev/docker)
- [Python Testing in Docker](https://docs.pytest.org/en/stable/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

## 🤝 Contributing

When adding new tests:

1. **Update Dockerfile.test** if new dependencies are needed
2. **Update docker-compose.test.yml** if new services are required
3. **Update run-tests-docker.sh** if new test types are added
4. **Test the Docker setup** before committing changes

## 📞 Support

For issues with the Docker test environment:

1. Check the troubleshooting section above
2. Review container logs: `./scripts/run-tests-docker.sh --logs`
3. Verify Docker and Docker Compose versions
4. Check system resources (memory, disk space)
