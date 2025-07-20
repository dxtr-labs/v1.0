# AutoFlow Database Migration Guide

## 🎯 Overview

Your AutoFlow platform has been successfully migrated from SQLite to a modern PostgreSQL database with UUID-based primary keys. This provides better scalability, security, and enterprise features.

## 📊 New Database Schema

### ✅ **Tables Created:**

1. **`waitlist`** - Pre-registration interest tracking
2. **`users`** - Core user accounts with UUID primary keys
3. **`credit_logs`** - Credit transaction history
4. **`ai_workflow_requests`** - AI workflow generation requests
5. **`chat_sessions`** - Conversational history
6. **`automations`** - Automation status tracking
7. **`agents`** - Custom AI agent definitions

### 🔑 **Key Features:**

- **UUID Primary Keys** - Better scalability and security
- **Row-Level Security (RLS)** - Users can only access their own agents
- **JSONB Support** - Flexible data storage for configurations
- **Comprehensive Indexing** - Optimized query performance
- **Audit Trails** - Automatic timestamp tracking

## 🔧 **Updated Configuration**

### Environment Variables (`.env.local`)

```bash
# Database Configuration - Updated for PostgreSQL
DATABASE_URL="postgresql://postgres:devhouse@localhost:5432/postgres"
PGUSER=postgres
PGPASSWORD=devhouse
PGDATABASE=postgres
PGPORT=5432
PGHOST=localhost
```

### New Backend Dependencies

```txt
asyncpg          # PostgreSQL async driver
bcrypt           # Password hashing
psycopg2-binary  # PostgreSQL adapter
```

## 🚀 **Getting Started**

### 1. **Initialize Database**

```bash
# Run the setup script
node scripts/init-database.js

# Or use PowerShell on Windows
.\setup-database.ps1
```

### 2. **Install Python Dependencies**

```bash
cd backend
pip install -r requirement.txt
```

### 3. **Start Backend Server**

```bash
cd backend
python main.py
```

### 4. **Test the System**

```bash
# Health check
curl http://localhost:8000/health

# Create a user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","firstName":"Test","lastName":"User"}'
```

## 📋 **API Endpoints**

### Authentication

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Agent Management

- `POST /api/agents` - Create new agent
- `GET /api/agents` - List user's agents
- `GET /api/agents/{id}` - Get specific agent
- `DELETE /api/agents/{id}` - Delete agent

### Credit System

- `GET /api/credits` - Get credit balance
- `GET /api/credits/history` - Get transaction history

### Legacy/Simplified

- `POST /chat` - Basic chat (simplified)
- `POST /send-email` - Direct email sending

## 🔒 **Security Features**

### Row-Level Security (RLS)

- Agents table has RLS enabled
- Users can only access their own agents
- Automatic user context filtering

### Password Security

- bcrypt hashing with salt
- Secure session token generation
- Session expiration management

## 📈 **Database Schema Details**

### Users Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(50) UNIQUE,
    organization BOOLEAN DEFAULT FALSE,
    session_token TEXT,
    session_expires TIMESTAMP,
    memory_context TEXT,
    service_keys JSONB DEFAULT '{}',
    credits INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Agents Table

```sql
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    agent_name VARCHAR(255) NOT NULL,
    agent_role TEXT,
    agent_personality TEXT,
    agent_expectations TEXT,
    agent_memory_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 **Migration Benefits**

### Before (SQLite)

- Integer primary keys
- Single-file database
- Limited concurrency
- No advanced security features

### After (PostgreSQL)

- UUID primary keys
- Enterprise-grade database
- High concurrency support
- Row-level security
- JSONB data types
- Advanced indexing

## 🧪 **Testing Your Setup**

### 1. **Database Connection Test**

```javascript
node scripts/init-database.js
```

### 2. **Backend API Test**

```bash
# Health check
curl http://localhost:8000/health

# Should return:
{
  "status": "ok",
  "message": "AutoFlow Platform is running",
  "database": "PostgreSQL with UUIDs",
  "timestamp": "2025-01-14T..."
}
```

### 3. **User Registration Test**

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "firstName": "Test",
    "lastName": "User"
  }'
```

### 4. **Agent Creation Test**

```bash
# First get session token from signup/login, then:
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=YOUR_SESSION_TOKEN" \
  -d '{
    "name": "Test Agent",
    "role": "Assistant",
    "description": "A test agent"
  }'
```

## 🚨 **Troubleshooting**

### Database Connection Issues

1. **Check PostgreSQL is running**

   ```bash
   # Windows: Check services
   # macOS: brew services start postgresql
   # Linux: sudo systemctl start postgresql
   ```

2. **Verify credentials in `.env.local`**

   ```bash
   PGUSER=postgres
   PGPASSWORD=devhouse
   PGHOST=localhost
   PGPORT=5432
   ```

3. **Test connection manually**
   ```bash
   psql -h localhost -U postgres -d postgres
   ```

### Common Errors

- **"relation does not exist"** → Run database initialization
- **"authentication failed"** → Check credentials
- **"connection refused"** → Start PostgreSQL service

## 📚 **Next Steps**

1. **Frontend Integration** - Update frontend to work with new UUID-based IDs
2. **Agent Enhancement** - Implement advanced agent features
3. **Credit System** - Add payment integration
4. **Workflow Engine** - Restore workflow automation features
5. **Monitoring** - Add database monitoring and logging

## 🎉 **Success Indicators**

✅ Database schema created with all tables  
✅ UUID extension enabled  
✅ Indexes created for performance  
✅ Row-level security configured  
✅ Backend server starts without errors  
✅ User registration works  
✅ Agent creation/management works  
✅ Credit system operational

Your AutoFlow platform is now running on a modern, scalable PostgreSQL database!
