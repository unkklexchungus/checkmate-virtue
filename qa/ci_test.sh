#!/bin/bash
set -e

echo "🚀 CheckMate Virtue CI Test Pipeline"
echo "===================================="
echo

# Configuration
APP_BASE_URL=${APP_BASE_URL:-http://127.0.0.1:8000}
HEALTH_TIMEOUT=${HEALTH_TIMEOUT:-60}
TEST_TIMEOUT=${TEST_TIMEOUT:-300}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to cleanup on exit
cleanup() {
    if [ ! -z "$SERVER_PID" ]; then
        print_status $YELLOW "🧹 Cleaning up server process..."
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
}

# Set up cleanup trap
trap cleanup EXIT

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status $RED "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status $YELLOW "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status $YELLOW "📦 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright if not already installed
if ! python -c "import playwright" 2>/dev/null; then
    print_status $YELLOW "📦 Installing Playwright..."
    pip install playwright
    playwright install
fi

# Step 1: Start the backend server
print_status $YELLOW "🔧 Starting backend server..."
print_status $YELLOW "   Base URL: $APP_BASE_URL"

# Kill any existing server process
pkill -f "python3 main.py" 2>/dev/null || true
sleep 2

# Start the server in background
python3 main.py &
SERVER_PID=$!

# Give the server a moment to start
sleep 3

# Step 2: Wait for health check
print_status $YELLOW "🏥 Waiting for service to become healthy..."
print_status $YELLOW "   Health endpoint: $APP_BASE_URL/healthz"
print_status $YELLOW "   Timeout: ${HEALTH_TIMEOUT}s"

# Use the health check utility
if python qa/health_check.py "$APP_BASE_URL"; then
    print_status $GREEN "✅ Service is healthy!"
else
    print_status $RED "❌ Service failed to become healthy within ${HEALTH_TIMEOUT}s"
    print_status $RED "   Check server logs for errors"
    exit 1
fi

# Step 3: Run browser tests
print_status $YELLOW "🧪 Running browser tests..."
print_status $YELLOW "   Test timeout: ${TEST_TIMEOUT}s"

# Set environment variables for tests
export APP_BASE_URL="$APP_BASE_URL"
export HEADLESS="true"
export TIMEOUT="30000"

# Run the browser tests with timeout
if timeout $TEST_TIMEOUT python qa/run_browser_tests.py; then
    print_status $GREEN "✅ Browser tests completed successfully!"
else
    TEST_EXIT_CODE=$?
    if [ $TEST_EXIT_CODE -eq 124 ]; then
        print_status $RED "❌ Browser tests timed out after ${TEST_TIMEOUT}s"
    else
        print_status $RED "❌ Browser tests failed with exit code $TEST_EXIT_CODE"
    fi
    
    # Show error logs if they exist
    if [ -f "qa/logs/error-log.txt" ]; then
        print_status $YELLOW "📋 Recent error logs:"
        tail -20 qa/logs/error-log.txt
    fi
    
    exit $TEST_EXIT_CODE
fi

# Step 4: Run unit tests
print_status $YELLOW "🧪 Running unit tests..."

if python qa/test_health_check.py; then
    print_status $GREEN "✅ Unit tests passed!"
else
    print_status $RED "❌ Unit tests failed"
    exit 1
fi

# Step 5: Run custom test example
print_status $YELLOW "🧪 Running custom test example..."

if python qa/test_example.py; then
    print_status $GREEN "✅ Custom tests passed!"
else
    print_status $RED "❌ Custom tests failed"
    exit 1
fi

# Success!
print_status $GREEN "🎉 All tests completed successfully!"
print_status $GREEN "===================================="

# Show test summary
if [ -f "qa/logs/error-log.txt" ]; then
    ERROR_COUNT=$(grep -c "SERVICE:" qa/logs/error-log.txt || echo "0")
    print_status $YELLOW "📊 Test Summary:"
    print_status $YELLOW "   Errors captured: $ERROR_COUNT"
    print_status $YELLOW "   Logs available at: qa/logs/"
fi

print_status $GREEN "✅ CI pipeline completed successfully!"
