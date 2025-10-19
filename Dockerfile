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

# Build SQLite database into the image with sample data
RUN python database/init_db.py --with-data

# Create necessary directories
RUN mkdir -p /tmp/uploads /tmp/logs

# Set working directory to backend for the application
WORKDIR /app/backend

# Expose port
EXPOSE $PORT

# Start command - use shell form to expand PORT environment variable
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 