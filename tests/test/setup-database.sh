#!/bin/bash

# Database Setup Script for AutoFlow Platform
# This script initializes the PostgreSQL database with the new UUID-based schema

echo "🚀 AutoFlow Database Setup"
echo "=========================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "Please install Node.js and try again"
    exit 1
fi

# Check if PostgreSQL dependencies are installed
if ! npm list pg &> /dev/null; then
    echo "📦 Installing PostgreSQL dependencies..."
    npm install pg
fi

# Run database initialization
echo "🏗️  Initializing PostgreSQL database..."
node scripts/init-database.js

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database setup completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Install Python dependencies: pip install -r backend/requirement.txt"
    echo "2. Start the backend server: cd backend && python main.py"
    echo "3. Start the frontend: npm run dev"
    echo ""
    echo "🔧 Database Info:"
    echo "   - Type: PostgreSQL with UUID primary keys"
    echo "   - Tables: users, agents, waitlist, credit_logs, automations, chat_sessions, ai_workflow_requests"
    echo "   - Features: Row-level security, credit system, agent management"
    echo ""
    echo "🌐 Endpoints:"
    echo "   - http://localhost:8000/health (Backend health check)"
    echo "   - http://localhost:3000 (Frontend)"
    echo "   - http://localhost:8000/api/auth/signup (User registration)"
    echo "   - http://localhost:8000/api/agents (Agent management)"
else
    echo "❌ Database setup failed"
    echo "Please check the error messages above and try again"
    exit 1
fi
