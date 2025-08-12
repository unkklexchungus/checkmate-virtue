#!/bin/bash

# CheckMate Virtue Browser Testing Demo
# This script demonstrates the browser testing system capabilities

set -e

echo "🚀 CheckMate Virtue Browser Testing Demo"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Playwright is installed
if ! python -c "import playwright" 2>/dev/null; then
    echo "📦 Installing Playwright..."
    pip install playwright
    playwright install
fi

# Check if server is running
echo "🔍 Checking if server is running..."
APP_BASE_URL=${APP_BASE_URL:-http://127.0.0.1:8000}
if ! curl -s $APP_BASE_URL > /dev/null; then
    echo "⚠️  Server not running at $APP_BASE_URL. Starting server..."
    echo "   (This will run in the background)"
    python3 main.py &
    SERVER_PID=$!
    sleep 5
    
    # Check if server started successfully
    if ! curl -s $APP_BASE_URL > /dev/null; then
        echo "❌ Failed to start server. Please start it manually:"
        echo "   python3 main.py"
        exit 1
    fi
    echo "✅ Server started successfully"
else
    echo "✅ Server is already running"
fi

echo
echo "🧪 Running Browser Tests..."
echo "=========================="

# Run the main browser tests
python qa/run_browser_tests.py

echo
echo "📊 Test Results Summary"
echo "======================"

# Show error log summary
if [ -f "qa/logs/error-log.txt" ]; then
    echo "📋 Error Log Summary:"
    echo "-------------------"
    grep -A 5 "SERVICE:" qa/logs/error-log.txt | head -20
    echo
    echo "📁 Full logs available at:"
    echo "   JSON: qa/logs/error-log.json"
    echo "   Text: qa/logs/error-log.txt"
    echo "   Screenshots: qa/logs/screenshots/"
else
    echo "❌ No error logs found"
fi

echo
echo "🎯 Running Custom Test Example..."
echo "================================"

# Run the custom test example
python qa/test_example.py

echo
echo "🎉 Demo Complete!"
echo "================"
echo
echo "💡 Next Steps:"
echo "   - Review the error logs to identify issues"
echo "   - Fix any broken routes or API endpoints"
echo "   - Run tests again to verify fixes"
echo "   - Add more custom test scenarios as needed"
echo
echo "📚 Documentation:"
echo "   - Main testing guide: qa/README.md"
echo "   - Example tests: qa/test_example.py"
echo "   - Configuration: qa/playwright.config.js"

# Cleanup if we started the server
if [ ! -z "$SERVER_PID" ]; then
    echo
    echo "🧹 Cleaning up..."
    kill $SERVER_PID 2>/dev/null || true
    echo "✅ Demo cleanup complete"
fi
