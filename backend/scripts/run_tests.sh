#!/bin/bash
set -e

PYTHON=".venv/Scripts/python.exe"
TEST_COMPOSE="docker compose -f ../docker-compose.test.yml"

echo "🚀 Starting test database..."
 $TEST_COMPOSE up -d --wait

echo "🧪 Running tests..."
 $PYTHON -m pytest "$@"

EXIT_CODE=$?

echo "🧹 Stopping test database..."
 $TEST_COMPOSE down

exit $EXIT_CODE