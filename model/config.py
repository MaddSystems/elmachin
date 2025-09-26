# Database configuration for chatbot_armaddia
import os
from dotenv import load_dotenv

# Load environment variables from the correct .env file
load_dotenv('/home/marketing/elmachin/.env', override=True)

# Database Configuration
DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL', 'mysql+pymysql://root:GPSc0ntr0l&1@localhost/chatbot_armaddia'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False  # Set to True for SQL debugging
    }
}

# OpenAI Configuration
OPENAI_CONFIG = {
    'model': 'gpt-4o-mini-2024-07-18',
    'max_tokens': 500,
    'temperature': 0.7
}

# Context Management Configuration
CONTEXT_CONFIG = {
    'max_context_length': 10,  # Number of previous messages to keep in context
    'context_timeout': 1800,   # Context timeout in seconds (30 minutes)
    'intent_confidence_threshold': 0.6
}

# GPS Control Specific Configuration
GPSCONTROL_CONFIG = {
    'company_name': 'GPScontrol by Machín',
    'support_phone': '+52 55 1234 5678',
    'support_email': 'soporte@gpscontrol.mx',
    'website': 'https://gpscontrol.mx'
}