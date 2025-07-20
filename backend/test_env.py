import os
from dotenv import load_dotenv

print("🔍 Testing Environment Variable Loading...")

# Load environment variables the same way as main.py
load_dotenv()
load_dotenv('.env.local')

print("\n📧 SMTP Configuration:")
print(f"SMTP_HOST: {os.getenv('SMTP_HOST')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"SMTP_USER: {os.getenv('SMTP_USER')}")
print(f"SMTP_PASSWORD: {'***' if os.getenv('SMTP_PASSWORD') else 'None'}")

print("\n📧 Alternative Email Configuration:")
print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST')}")
print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT')}")
print(f"EMAIL_USER: {os.getenv('EMAIL_USER')}")
print(f"EMAIL_PASS: {'***' if os.getenv('EMAIL_PASS') else 'None'}")
