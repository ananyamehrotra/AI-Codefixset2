import os

# Configuration settings
class Config:
    # Database configuration
    DATABASE_URI = 'sqlite:///data/data.db'
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'provided@event.com')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'will_be_provided')
    
    # Report settings
    REPORT_TEMPLATE_PATH = 'src/templates/report_template.html'
    OUTPUT_DIR = 'output/reports'