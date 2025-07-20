# Database Setup Script for AutoFlow Platform (Windows PowerShell)
# This script initializes the PostgreSQL database with the new UUID-based schema

Write-Host "🚀 AutoFlow Database Setup" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

# Check if Node.js is available
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is required but not installed" -ForegroundColor Red
    Write-Host "Please install Node.js and try again" -ForegroundColor Red
    exit 1
}

# Check if PostgreSQL dependencies are installed
Write-Host "📦 Checking PostgreSQL dependencies..." -ForegroundColor Blue
try {
    npm list pg 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing pg dependency..." -ForegroundColor Yellow
        npm install pg
    }
} catch {
    Write-Host "Installing pg dependency..." -ForegroundColor Yellow
    npm install pg
}

# Run database initialization
Write-Host "🏗️  Initializing PostgreSQL database..." -ForegroundColor Blue
node scripts/init-database.js

# Check if initialization was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Database setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Install Python dependencies: pip install -r backend/requirement.txt" -ForegroundColor White
    Write-Host "2. Start the backend server: cd backend && python main.py" -ForegroundColor White
    Write-Host "3. Start the frontend: npm run dev" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Database Info:" -ForegroundColor Cyan
    Write-Host "   - Type: PostgreSQL with UUID primary keys" -ForegroundColor White
    Write-Host "   - Tables: users, agents, waitlist, credit_logs, automations, chat_sessions, ai_workflow_requests" -ForegroundColor White
    Write-Host "   - Features: Row-level security, credit system, agent management" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Endpoints:" -ForegroundColor Cyan
    Write-Host "   - http://localhost:8000/health (Backend health check)" -ForegroundColor White
    Write-Host "   - http://localhost:3000 (Frontend)" -ForegroundColor White
    Write-Host "   - http://localhost:8000/api/auth/signup (User registration)" -ForegroundColor White
    Write-Host "   - http://localhost:8000/api/agents (Agent management)" -ForegroundColor White
} else {
    Write-Host "❌ Database setup failed" -ForegroundColor Red
    Write-Host "Please check the error messages above and try again" -ForegroundColor Red
    exit 1
}
