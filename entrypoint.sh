#!/bin/bash

# Wait for database to be ready
python -c "import time; time.sleep(10)"

# Run migrations
python migrations.py

# Start the application
exec gunicorn --bind 0.0.0.0:5000 run:app
