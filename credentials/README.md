# Credentials Directory

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
