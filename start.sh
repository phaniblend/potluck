#!/bin/bash
# Startup script for Railway deployment
# Ensures database exists and is seeded

set -e

cd /app/backend

# Check if database exists, if not create it
if [ ! -f "potluck.db" ]; then
    echo "Database not found, creating and seeding..."
    cd /app
    python database/init_db.py
    python database/seed_test_data.py
    cd /app/backend
fi

# Start the application
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120

