# Use the official slim Python image
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set Python path to include the src directory
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/src"

# Install system dependencies for building Python packages and libraries required by pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Set the working directory in the container
WORKDIR /app

# Copy the entire project first to ensure all files are available
COPY . /app

# Install dependencies with development dependencies excluded
RUN poetry install --no-interaction --no-ansi --no-root

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser --uid 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# Set the FLASK_APP environment variable
ENV FLASK_APP=run.py

# Set up entrypoint scripts
RUN chmod +x /app/entrypoint.sh 

# Switch to the non-root user
USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]