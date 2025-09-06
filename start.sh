#!/bin/bash

# Set default port if not specified
PORT=${PORT:-8080}
WORKERS=${WORKERS:-4}
TIMEOUT=${TIMEOUT:-120}

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers $WORKERS --timeout $TIMEOUT app:app
