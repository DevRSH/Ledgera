# Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*




# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code only
COPY . .


# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Start command
RUN chmod +x start.sh
CMD ["./start.sh"]

