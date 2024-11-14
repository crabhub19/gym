#!/bin/bash

# Exit on any error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Compile messages if you're using Django translations
# python manage.py compilemessages

# Start the server
gunicorn gym.wsgi:application --bind 0.0.0.0:$PORT
