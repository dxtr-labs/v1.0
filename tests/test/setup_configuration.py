#!/usr/bin/env python3
"""
DXTR AutoFlow - Configuration Setup Script
Helps configure API keys, credentials, and webhook endpoints
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

def create_env_template():
    """Create a .env template file with all required configuration"""
    env_template = """# DXTR AutoFlow Configuration Template
# Copy this file to .env and fill in your actual values

# ===== OPENAI CONFIGURATION =====
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORGANIZATION=your_openai_org_id_here  # Optional
OPENAI_DEFAULT_MODEL=gpt-4

# ===== TELEGRAM CONFIGURATION =====
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook/telegram

# ===== SLACK CONFIGURATION =====
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here
SLACK_DEFAULT_CHANNEL=#general
SLACK_WEBHOOK_URL=https://your-domain.com/webhook/slack

# ===== EMAIL CONFIGURATION =====
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_FROM_NAME=DXTR AutoFlow
EMAIL_USE_TLS=true

# ===== GOOGLE SERVICES CONFIGURATION =====
GOOGLE_CREDENTIALS_PATH=./credentials/google_credentials.json
GOOGLE_SHEETS_SCOPE=https://www.googleapis.com/auth/spreadsheets
GOOGLE_DRIVE_SCOPE=https://www.googleapis.com/auth/drive

# ===== PHASE 3 DRIVERS - PROJECT MANAGEMENT =====
ASANA_ACCESS_TOKEN=your_asana_access_token_here
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here

# ===== PHASE 3 DRIVERS - SOCIAL MEDIA =====
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here

# ===== PHASE 3 DRIVERS - PAYMENT PROCESSING =====
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret_here

# ===== PHASE 3 DRIVERS - ANALYTICS =====
GOOGLE_ANALYTICS_VIEW_ID=your_ga_view_id_here
GOOGLE_ANALYTICS_CREDENTIALS_PATH=./credentials/ga_credentials.json

# ===== DATABASE CONFIGURATION =====
DATABASE_URL=postgresql://user:password@localhost:5432/dxtr_autoflow
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=dxtr_autoflow
DATABASE_USER=dxtr_user
DATABASE_PASSWORD=your_database_password_here

# ===== WEBHOOK CONFIGURATION =====
WEBHOOK_BASE_URL=https://your-domain.com
WEBHOOK_SECRET=your_webhook_secret_key_here
WEBHOOK_VERIFY_SSL=true

# ===== LOGGING CONFIGURATION =====
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/dxtr_autoflow.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# ===== SECURITY CONFIGURATION =====
SECRET_KEY=your_secret_key_for_jwt_and_sessions
ENCRYPTION_KEY=your_encryption_key_for_sensitive_data
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000

# ===== MONITORING CONFIGURATION =====
MONITORING_ENABLED=true
METRICS_ENDPOINT=/metrics
HEALTH_CHECK_ENDPOINT=/health
PERFORMANCE_TRACKING=true
"""
    
    with open(".env.template", "w") as f:
        f.write(env_template)
    
    print("✅ Created .env.template file")
    print("📝 Please copy this file to .env and fill in your actual values")

def create_credentials_directory():
    """Create credentials directory structure"""
    credentials_dir = Path("credentials")
    credentials_dir.mkdir(exist_ok=True)
    
    # Create README for credentials
    readme_content = """# Credentials Directory

This directory contains sensitive credential files. **Never commit these files to version control.**

## Required Files:

### Google Services
- `google_credentials.json` - Google API service account credentials
- `ga_credentials.json` - Google Analytics API credentials

### SSL Certificates (if using HTTPS)
- `cert.pem` - SSL certificate
- `key.pem` - SSL private key

## Setup Instructions:

1. **Google Credentials**:
   - Go to Google Cloud Console
   - Create a service account
   - Download the JSON credentials file
   - Place it as `google_credentials.json`

2. **Google Analytics**:
   - Enable Google Analytics Reporting API
   - Create credentials for your application
   - Download and place as `ga_credentials.json`

3. **SSL Certificates**:
   - Obtain SSL certificates from your provider
   - Place certificate files in this directory

## Security Notes:
- All files in this directory are included in .gitignore
- Never share these files publicly
- Rotate credentials regularly
- Use environment variables for production
"""
    
    with open(credentials_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created credentials directory with README")

def create_gitignore():
    """Create/update .gitignore file"""
    gitignore_content = """# DXTR AutoFlow - Security and Configuration

# Environment files
.env
.env.local
.env.production

# Credentials
credentials/
*.json
*.pem
*.key
*.crt

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test results
test_*_results.json
coverage/
.coverage

# Temporary files
tmp/
temp/
*.tmp

# Build artifacts
build/
dist/
*.egg-info/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ Created/updated .gitignore file")

def create_webhook_config():
    """Create webhook configuration template"""
    webhook_config = {
        "webhook_endpoints": {
            "telegram": {
                "url": "/webhook/telegram",
                "method": "POST",
                "secret_token": "your_telegram_webhook_secret",
                "allowed_updates": ["message", "edited_message", "callback_query"]
            },
            "slack": {
                "url": "/webhook/slack",
                "method": "POST",
                "signing_secret": "your_slack_signing_secret",
                "event_types": ["message.channels", "app_mention"]
            },
            "stripe": {
                "url": "/webhook/stripe",
                "method": "POST",
                "webhook_secret": "whsec_your_stripe_webhook_secret",
                "events": ["payment_intent.succeeded", "invoice.payment_succeeded"]
            },
            "asana": {
                "url": "/webhook/asana",
                "method": "POST",
                "secret": "your_asana_webhook_secret",
                "events": ["task_added", "task_updated", "project_updated"]
            },
            "trello": {
                "url": "/webhook/trello",
                "method": "POST",
                "secret": "your_trello_webhook_secret",
                "events": ["createCard", "updateCard", "addMemberToCard"]
            }
        },
        "webhook_security": {
            "verify_signatures": True,
            "rate_limiting": {
                "enabled": True,
                "max_requests_per_minute": 100
            },
            "ip_whitelist": {
                "enabled": False,
                "allowed_ips": []
            }
        },
        "webhook_logging": {
            "log_all_requests": True,
            "log_payloads": False,
            "log_responses": True
        }
    }
    
    with open("webhook_config.json", "w") as f:
        json.dump(webhook_config, f, indent=2)
    
    print("✅ Created webhook_config.json")

def create_docker_compose():
    """Create Docker Compose configuration"""
    docker_compose = """version: '3.8'

services:
  dxtr-autoflow:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://dxtr_user:password@postgres:5432/dxtr_autoflow
    depends_on:
      - postgres
      - redis
    volumes:
      - ./credentials:/app/credentials
      - ./logs:/app/logs
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
    networks:
      - dxtr-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - dxtr-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./credentials:/etc/nginx/ssl
    depends_on:
      - dxtr-autoflow
    networks:
      - dxtr-network

volumes:
  postgres_data:
  redis_data:

networks:
  dxtr-network:
    driver: bridge
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ Created docker-compose.yml")

def create_nginx_config():
    """Create Nginx configuration"""
    nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream dxtr_autoflow {
        server dxtr-autoflow:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://dxtr_autoflow;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /webhook/ {
            proxy_pass http://dxtr_autoflow;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 30s;
        }
    }
}
"""
    
    with open("nginx.conf", "w") as f:
        f.write(nginx_config)
    
    print("✅ Created nginx.conf")

def create_systemd_service():
    """Create systemd service file"""
    service_config = """[Unit]
Description=DXTR AutoFlow - Workflow Automation Platform
After=network.target postgresql.service

[Service]
Type=simple
User=dxtr
Group=dxtr
WorkingDirectory=/opt/dxtr-autoflow
Environment=PATH=/opt/dxtr-autoflow/venv/bin
ExecStart=/opt/dxtr-autoflow/venv/bin/python main.py
Restart=always
RestartSec=10

# Environment file
EnvironmentFile=/opt/dxtr-autoflow/.env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dxtr-autoflow

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/dxtr-autoflow/logs

[Install]
WantedBy=multi-user.target
"""
    
    with open("dxtr-autoflow.service", "w") as f:
        f.write(service_config)
    
    print("✅ Created dxtr-autoflow.service")
    print("📝 To install: sudo cp dxtr-autoflow.service /etc/systemd/system/")

def create_logging_config():
    """Create logging configuration"""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
            },
            "json": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "logs/dxtr_autoflow.log",
                "maxBytes": 10485760,
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/dxtr_autoflow_errors.log",
                "maxBytes": 10485760,
                "backupCount": 5
            }
        },
        "loggers": {
            "dxtr_autoflow": {
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
    
    with open("logging_config.json", "w") as f:
        json.dump(logging_config, f, indent=2)
    
    print("✅ Created logging_config.json")

def create_monitoring_config():
    """Create monitoring configuration"""
    monitoring_config = {
        "metrics": {
            "enabled": True,
            "endpoint": "/metrics",
            "port": 8001,
            "collect_interval": 60
        },
        "health_checks": {
            "enabled": True,
            "endpoint": "/health",
            "checks": [
                {
                    "name": "database",
                    "type": "database_connection",
                    "timeout": 5
                },
                {
                    "name": "openai_api",
                    "type": "api_endpoint",
                    "url": "https://api.openai.com/v1/models",
                    "timeout": 10
                },
                {
                    "name": "disk_space",
                    "type": "disk_usage",
                    "path": "/",
                    "threshold": 90
                }
            ]
        },
        "alerts": {
            "enabled": True,
            "channels": ["email", "slack", "telegram"],
            "rules": [
                {
                    "name": "high_error_rate",
                    "metric": "error_rate",
                    "threshold": 0.05,
                    "duration": "5m",
                    "severity": "critical"
                },
                {
                    "name": "slow_response_time",
                    "metric": "response_time_p95",
                    "threshold": 5000,
                    "duration": "10m",
                    "severity": "warning"
                }
            ]
        },
        "dashboards": {
            "grafana": {
                "enabled": True,
                "url": "http://localhost:3000",
                "datasource": "prometheus"
            }
        }
    }
    
    with open("monitoring_config.json", "w") as f:
        json.dump(monitoring_config, f, indent=2)
    
    print("✅ Created monitoring_config.json")

def main():
    """Main configuration setup function"""
    print("🔧 DXTR AutoFlow - Configuration Setup")
    print("=" * 50)
    print(f"Setup started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create all configuration files
    create_env_template()
    create_credentials_directory()
    create_gitignore()
    create_webhook_config()
    create_docker_compose()
    create_nginx_config()
    create_systemd_service()
    create_logging_config()
    create_monitoring_config()
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✅ Created logs directory")
    
    print()
    print("=" * 50)
    print("📋 SETUP COMPLETE")
    print("=" * 50)
    print()
    print("📁 Files created:")
    print("  - .env.template (copy to .env and configure)")
    print("  - credentials/README.md (setup instructions)")
    print("  - .gitignore (security configurations)")
    print("  - webhook_config.json (webhook endpoints)")
    print("  - docker-compose.yml (containerized deployment)")
    print("  - nginx.conf (reverse proxy configuration)")
    print("  - dxtr-autoflow.service (systemd service)")
    print("  - logging_config.json (logging configuration)")
    print("  - monitoring_config.json (monitoring setup)")
    print()
    print("🎯 NEXT STEPS:")
    print("  1. Copy .env.template to .env")
    print("  2. Fill in your API keys and credentials")
    print("  3. Set up Google credentials in credentials/")
    print("  4. Configure your domain in nginx.conf")
    print("  5. Run: docker-compose up -d")
    print()
    print("🔐 SECURITY REMINDERS:")
    print("  - Never commit .env or credentials/ to version control")
    print("  - Use strong passwords and secret keys")
    print("  - Enable SSL/TLS in production")
    print("  - Regularly rotate API keys and credentials")

if __name__ == "__main__":
    main()
