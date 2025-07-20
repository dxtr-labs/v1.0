#!/usr/bin/env python3
"""
DXTR AutoFlow - Production Deployment Script
Automates deployment, monitoring, and logging setup
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🚀 {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def check_prerequisites():
    """Check if prerequisites are installed"""
    print("🔍 Checking Prerequisites")
    print("=" * 50)
    
    prerequisites = [
        ("python", "Python 3.8+"),
        ("pip", "Python Package Manager"),
        ("docker", "Docker Engine"),
        ("docker-compose", "Docker Compose"),
        ("git", "Git Version Control")
    ]
    
    all_good = True
    for command, description in prerequisites:
        if run_command(f"{command} --version", f"Check {description}"):
            continue
        else:
            all_good = False
            print(f"❌ {description} not found - Please install it first")
    
    return all_good

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Dependencies")
    print("=" * 50)
    
    # Create requirements.txt if it doesn't exist
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
httpx==0.25.2
openai==1.3.7
telegram-bot-api==0.1.1
slackclient==2.9.4
google-auth==2.25.2
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.2.0
google-api-python-client==2.110.0
stripe==7.8.0
prometheus-client==0.19.0
python-json-logger==2.0.7
alembic==1.13.0
pytest==7.4.3
pytest-asyncio==0.21.1
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt")
    
    # Install dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrade pip"),
        ("pip install -r requirements.txt", "Install Python packages"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def setup_database():
    """Set up database"""
    print("\n🗄️ Setting up Database")
    print("=" * 50)
    
    # Check if PostgreSQL is running
    if not run_command("docker-compose ps postgres", "Check PostgreSQL container"):
        print("🚀 Starting PostgreSQL container...")
        if not run_command("docker-compose up -d postgres", "Start PostgreSQL"):
            return False
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(10)
    
    # Run database migrations (if you have them)
    migration_commands = [
        ("alembic upgrade head", "Run database migrations"),
    ]
    
    for command, description in migration_commands:
        run_command(command, description)
    
    return True

def setup_logging():
    """Set up logging system"""
    print("\n📝 Setting up Logging")
    print("=" * 50)
    
    # Create log directories
    log_dirs = ["logs", "logs/archived"]
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created log directories")
    
    # Set up log rotation
    logrotate_config = """/opt/dxtr-autoflow/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 dxtr dxtr
    postrotate
        systemctl reload dxtr-autoflow
    endscript
}
"""
    
    with open("dxtr-autoflow.logrotate", "w") as f:
        f.write(logrotate_config)
    
    print("✅ Created logrotate configuration")
    
    return True

def setup_monitoring():
    """Set up monitoring system"""
    print("\n📊 Setting up Monitoring")
    print("=" * 50)
    
    # Create monitoring directories
    monitoring_dirs = ["monitoring", "monitoring/prometheus", "monitoring/grafana"]
    for monitoring_dir in monitoring_dirs:
        Path(monitoring_dir).mkdir(parents=True, exist_ok=True)
    
    # Create Prometheus configuration
    prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'dxtr-autoflow'
    static_configs:
      - targets: ['localhost:8001']
    scrape_interval: 30s
    metrics_path: '/metrics'

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
"""
    
    with open("monitoring/prometheus/prometheus.yml", "w") as f:
        f.write(prometheus_config)
    
    # Create alert rules
    alert_rules = """groups:
  - name: dxtr-autoflow
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for 5 minutes"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time detected"
          description: "95th percentile response time is above 5 seconds"

      - alert: DatabaseConnectionFailed
        expr: up{job="postgresql"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failed"
          description: "Cannot connect to PostgreSQL database"
"""
    
    with open("monitoring/prometheus/alert_rules.yml", "w") as f:
        f.write(alert_rules)
    
    print("✅ Created monitoring configuration")
    
    return True

def create_deployment_docker_compose():
    """Create production Docker Compose configuration"""
    print("\n🐳 Creating Production Docker Compose")
    print("=" * 50)
    
    docker_compose_prod = """version: '3.8'

services:
  dxtr-autoflow:
    build: .
    ports:
      - "8000:8000"
      - "8001:8001"  # Metrics endpoint
    environment:
      - DATABASE_URL=postgresql://dxtr_user:password@postgres:5432/dxtr_autoflow
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    volumes:
      - ./credentials:/app/credentials:ro
      - ./logs:/app/logs
      - ./monitoring:/app/monitoring
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - dxtr-network

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dxtr_autoflow
      POSTGRES_USER: dxtr_user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./monitoring/postgres:/var/lib/postgresql/monitoring
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dxtr_user -d dxtr_autoflow"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - dxtr-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - dxtr-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./credentials:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - dxtr-autoflow
    restart: unless-stopped
    networks:
      - dxtr-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped
    networks:
      - dxtr-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped
    networks:
      - dxtr-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  dxtr-network:
    driver: bridge
"""
    
    with open("docker-compose.prod.yml", "w") as f:
        f.write(docker_compose_prod)
    
    print("✅ Created production Docker Compose configuration")
    
    return True

def create_dockerfile():
    """Create Dockerfile for production"""
    print("\n🏗️ Creating Dockerfile")
    print("=" * 50)
    
    dockerfile = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 dxtr && chown -R dxtr:dxtr /app
USER dxtr

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    print("✅ Created Dockerfile")
    
    return True

def deploy_application():
    """Deploy the application"""
    print("\n🚀 Deploying Application")
    print("=" * 50)
    
    deployment_commands = [
        ("docker-compose -f docker-compose.prod.yml build", "Build Docker images"),
        ("docker-compose -f docker-compose.prod.yml up -d", "Start all services"),
        ("docker-compose -f docker-compose.prod.yml ps", "Check service status"),
    ]
    
    for command, description in deployment_commands:
        if not run_command(command, description):
            return False
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(30)
    
    # Run health checks
    health_checks = [
        ("curl -f http://localhost:8000/health", "Application health check"),
        ("curl -f http://localhost:8001/metrics", "Metrics endpoint check"),
        ("curl -f http://localhost:9090/-/healthy", "Prometheus health check"),
    ]
    
    for command, description in health_checks:
        run_command(command, description)
    
    return True

def create_backup_script():
    """Create backup script"""
    print("\n💾 Creating Backup Script")
    print("=" * 50)
    
    backup_script = """#!/bin/bash
# DXTR AutoFlow Backup Script

BACKUP_DIR="/opt/backups/dxtr-autoflow"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="dxtr_autoflow_backup_$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec postgres pg_dump -U dxtr_user dxtr_autoflow > $BACKUP_DIR/database_$DATE.sql

# Application backup
tar -czf $BACKUP_DIR/$BACKUP_FILE \\
    --exclude='logs/*' \\
    --exclude='__pycache__' \\
    --exclude='.git' \\
    .

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE"
"""
    
    with open("backup.sh", "w") as f:
        f.write(backup_script)
    
    # Make executable
    os.chmod("backup.sh", 0o755)
    
    print("✅ Created backup script")
    
    return True

def main():
    """Main deployment function"""
    print("🚀 DXTR AutoFlow - Production Deployment")
    print("=" * 60)
    print(f"Deployment started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please install missing components.")
        sys.exit(1)
    
    # Setup steps
    setup_steps = [
        (install_dependencies, "Install Dependencies"),
        (create_dockerfile, "Create Dockerfile"),
        (create_deployment_docker_compose, "Create Production Docker Compose"),
        (setup_database, "Set up Database"),
        (setup_logging, "Set up Logging"),
        (setup_monitoring, "Set up Monitoring"),
        (create_backup_script, "Create Backup Script"),
        (deploy_application, "Deploy Application"),
    ]
    
    failed_steps = []
    
    for step_func, step_name in setup_steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {str(e)}")
            failed_steps.append(step_name)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    if not failed_steps:
        print("✅ All deployment steps completed successfully!")
        print("\n🎉 DXTR AutoFlow is now running in production!")
        print("\n🔗 Access URLs:")
        print("  - Application: http://localhost:8000")
        print("  - Metrics: http://localhost:8001/metrics")
        print("  - Grafana: http://localhost:3000 (admin/admin)")
        print("  - Prometheus: http://localhost:9090")
        print("\n📋 Next Steps:")
        print("  - Configure your domain and SSL certificates")
        print("  - Set up monitoring alerts")
        print("  - Schedule regular backups")
        print("  - Configure log rotation")
    else:
        print(f"❌ {len(failed_steps)} deployment steps failed:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\n🔧 Please check the errors above and retry the failed steps.")

if __name__ == "__main__":
    main()
