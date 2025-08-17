#!/bin/bash

# Run E2E tests and generate unified error log
echo "🚀 Running E2E tests..."

# Build and start the environment
echo "📦 Building containers..."
docker compose -f docker-compose.e2e.yml build

echo "🚀 Starting app service..."
docker compose -f docker-compose.e2e.yml up -d app

# Wait for app to be healthy
echo "⏳ Waiting for app to be ready..."
sleep 10

# Run the tests
echo " Running tests..."
docker compose -f docker-compose.e2e.yml run --rm tests "npm ci && npx playwright test --grep '(S[0-6])'"

# Check if unified error log was created
if [ -f "artifacts/e2e/unified-error-log.txt" ]; then
    echo ""
    echo "📋 Unified error log generated:"
    echo "   artifacts/e2e/unified-error-log.txt"
    echo ""
    echo "📋 Copy this file to share with ChatGPT:"
    echo "   cat artifacts/e2e/unified-error-log.txt"
    echo ""
    
    # Try to copy to clipboard
    if command -v pbcopy >/dev/null 2>&1; then
        cat artifacts/e2e/unified-error-log.txt | pbcopy
        echo "📋 Error log copied to clipboard (macOS)"
    elif command -v xclip >/dev/null 2>&1; then
        cat artifacts/e2e/unified-error-log.txt | xclip -selection clipboard
        echo "📋 Error log copied to clipboard (Linux)"
    else
        echo " Error log content:"
        cat artifacts/e2e/unified-error-log.txt
    fi
else
    echo "✅ No errors found - all tests passed!"
fi

# Clean up
echo "🧹 Cleaning up..."
docker compose -f docker-compose.e2e.yml down
