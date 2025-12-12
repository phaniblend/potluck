# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build SQLite database into the image with test data
RUN python database/init_db.py && python database/seed_test_data.py

# Create necessary directories
RUN mkdir -p /tmp/uploads /tmp/logs

# Create startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set working directory to backend for the application
WORKDIR /app/backend

# Expose port
EXPOSE $PORT

# Start command - use startup script to ensure database exists
CMD ["/app/start.sh"] 