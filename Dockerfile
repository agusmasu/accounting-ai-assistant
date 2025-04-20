FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg (PostgreSQL client)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port for the application
EXPOSE 8080

# Command to run the application using uvicorn
CMD uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8080} 