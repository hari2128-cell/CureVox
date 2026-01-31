#!/bin/bash

# Deployment script for CureVox

set -e  # Exit on error

echo "🚀 Starting CureVox deployment..."

# Load environment variables
source ../backend/.env

# Pull latest code
echo "📦 Pulling latest code..."
git pull origin main

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
flask db upgrade

# Collect static files
echo "📁 Collecting static files..."
# Add any static collection commands here

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart curevox-backend
sudo systemctl restart nginx

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo "✅ Deployment completed successfully!"