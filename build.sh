#!/usr/bin/env bash
# Build script for Render deployment
# Builds React frontend, copies into backend for Flask to serve

set -o errexit

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies and build
cd ../frontend
npm install
REACT_APP_API_URL="/api" npm run build

# Copy frontend build to backend for Flask to serve
cd ..
rm -rf backend/frontend_build
cp -r frontend/build backend/frontend_build

echo "Build complete — Flask will serve the React app."