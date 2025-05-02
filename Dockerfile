FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg (PostgreSQL client), libsndfile, and ffmpeg
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV POSTGRES_HOST=ep-delicate-moon-a4dnrer6-pooler.us-east-1.aws.neon.tech
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=neondb
ENV POSTGRES_USER=neondb_owner
ENV POSTGRES_CONNECT_OPTIONS=endpoint=ep-delicate-moon-a4dnrer6
ENV ADMIN_API_KEY=admin

# Expose the port for the application
EXPOSE 8080

# Command to run the application using uvicorn
CMD uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8080} 