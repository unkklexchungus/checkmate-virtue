#!/bin/bash

# Docker Test Runner Script for CheckMate Virtue
# This script runs all tests exclusively in Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all              Run all tests (browser, API, health checks)"
    echo "  --browser          Run only browser tests"
    echo "  --api              Run only API tests"
    echo "  --health           Run only health checks"
    echo "  --playwright       Run Playwright tests"
    echo "  --headed           Run browser tests in headed mode (visible browser)"
    echo "  --debug            Run tests in debug mode with longer timeouts"
    echo "  --clean            Clean up containers and volumes before running"
    echo "  --logs             Show logs from all containers"
    echo "  --stop             Stop all test containers"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all                    # Run all tests"
    echo "  $0 --browser --headed       # Run browser tests with visible browser"
    echo "  $0 --clean --all            # Clean and run all tests"
    echo "  $0 --stop                   # Stop all test containers"
}

# Function to clean up containers and volumes
cleanup() {
    print_status "Cleaning up test containers and volumes..."
    docker-compose -f docker-compose.test.yml down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping test containers..."
    docker-compose -f docker-compose.test.yml down
    print_success "Test containers stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing logs from all test containers..."
    docker-compose -f docker-compose.test.yml logs -f
}

# Function to wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for database
    print_status "Waiting for test database..."
    timeout 60 bash -c 'until docker exec test_postgres pg_isready -U testuser -d testdb 2>/dev/null; do sleep 2; done'
    
    # Wait for Redis
    print_status "Waiting for test Redis..."
    timeout 30 bash -c 'until docker exec test_redis redis-cli ping 2>/dev/null; do sleep 2; done'
    
    # Wait for application to be ready
    print_status "Waiting for test application..."
    timeout 120 bash -c 'until docker exec test_app curl -f http://localhost:8000/healthz 2>/dev/null; do sleep 5; done'
    
    # Additional wait for port mapping to be available
    print_status "Waiting for port mapping to be available..."
    timeout 30 bash -c 'until curl -f http://localhost:8001/healthz 2>/dev/null; do sleep 2; done'
    
    print_success "All services are healthy"
}

# Function to run browser tests
run_browser_tests() {
    print_status "Running browser tests..."
    
    if [[ "$HEADED" == "true" ]]; then
        print_status "Running in headed mode (browser will be visible)"
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            bash -c "export HEADLESS=false && python3 qa/run_browser_tests.py"
    elif [[ "$DEBUG" == "true" ]]; then
        print_status "Running in debug mode with extended timeouts"
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            bash -c "export TIMEOUT=60000 && export WAIT_FOR_IDLE=5000 && python3 qa/run_browser_tests.py"
    else
        docker-compose -f docker-compose.test.yml run --rm test-runner
    fi
}

# Function to run API tests
run_api_tests() {
    print_status "Running API tests..."
    docker-compose -f docker-compose.test.yml run --rm api-test-runner
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    docker-compose -f docker-compose.test.yml run --rm health-monitor
}

# Function to run Playwright tests
run_playwright_tests() {
    print_status "Running Playwright tests..."
    docker-compose -f docker-compose.test.yml run --rm playwright-runner
}

# Function to run all tests
run_all_tests() {
    print_status "Starting test environment..."
    
    # Start the test environment
    docker-compose -f docker-compose.test.yml up -d test-postgres test-redis test-app
    
    # Wait for services to be ready
    wait_for_services
    
    # Run different test types
    print_status "Running all test suites..."
    
    # Run health checks first
    run_health_checks
    
    # Run API tests
    run_api_tests
    
    # Run browser tests
    run_browser_tests
    
    # Run Playwright tests
    run_playwright_tests
    
    print_success "All tests completed"
}

# Main script logic
main() {
    # Parse command line arguments
    RUN_ALL=false
    RUN_BROWSER=false
    RUN_API=false
    RUN_HEALTH=false
    RUN_PLAYWRIGHT=false
    HEADED=false
    DEBUG=false
    CLEAN=false
    SHOW_LOGS=false
    STOP_CONTAINERS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                RUN_ALL=true
                shift
                ;;
            --browser)
                RUN_BROWSER=true
                shift
                ;;
            --api)
                RUN_API=true
                shift
                ;;
            --health)
                RUN_HEALTH=true
                shift
                ;;
            --playwright)
                RUN_PLAYWRIGHT=true
                shift
                ;;
            --headed)
                HEADED=true
                shift
                ;;
            --debug)
                DEBUG=true
                shift
                ;;
            --clean)
                CLEAN=true
                shift
                ;;
            --logs)
                SHOW_LOGS=true
                shift
                ;;
            --stop)
                STOP_CONTAINERS=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Handle special cases
    if [[ "$STOP_CONTAINERS" == "true" ]]; then
        stop_containers
        exit 0
    fi
    
    if [[ "$SHOW_LOGS" == "true" ]]; then
        show_logs
        exit 0
    fi
    
    # Clean up if requested
    if [[ "$CLEAN" == "true" ]]; then
        cleanup
    fi
    
    # Run tests based on flags
    if [[ "$RUN_ALL" == "true" ]]; then
        run_all_tests
    elif [[ "$RUN_BROWSER" == "true" ]]; then
        docker-compose -f docker-compose.test.yml up -d test-postgres test-redis test-app
        wait_for_services
        run_browser_tests
    elif [[ "$RUN_API" == "true" ]]; then
        docker-compose -f docker-compose.test.yml up -d test-postgres test-redis test-app
        wait_for_services
        run_api_tests
    elif [[ "$RUN_HEALTH" == "true" ]]; then
        docker-compose -f docker-compose.test.yml up -d test-postgres test-redis test-app
        wait_for_services
        run_health_checks
    elif [[ "$RUN_PLAYWRIGHT" == "true" ]]; then
        docker-compose -f docker-compose.test.yml up -d test-postgres test-redis test-app
        wait_for_services
        run_playwright_tests
    else
        print_warning "No test type specified. Running all tests..."
        run_all_tests
    fi
    
    print_success "Test execution completed"
}

# Run main function with all arguments
main "$@"
