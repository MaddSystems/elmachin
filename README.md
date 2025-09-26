# GPS Control Enhanced Chatbot System

## 🤖 Overview

This is an enhanced multi-channel chatbot system for GPS Control by Machín, featuring advanced context management, intent recognition, and database integration. The system provides intelligent responses about GPS tracking services, security cameras, and fleet management solutions.

## ✨ Features

### 🔄 Multi-Channel Support
- **WhatsApp Business API**: Cloud API webhook integration
- **Facebook Messenger**: Page webhook integration  
- **Web Interface**: Real-time chat with Socket.IO
- **Unified Processing**: Same AI logic across all channels

### 🧠 Advanced AI Capabilities
- **GPS Control Dataset**: Pre-trained responses for GPS/security services
- **Context Management**: Conversation memory and user session tracking
- **Intent Recognition**: Advanced classification with confidence scoring
- **ChatGPT Fallback**: OpenAI integration for complex queries

### 💾 Database Integration
- **MySQL Database**: Conversation tracking and analytics
- **User Context**: Session management with expiration
- **Chat Reports**: Interaction statistics and intent analysis
- **Conversation History**: Full message logging with sentiment

### 📊 Admin Dashboard
- **Real-time Monitoring**: Live conversation tracking
- **Analytics**: Intent statistics and user engagement metrics
- **Conversation Management**: Browse and analyze chat history
- **Performance Metrics**: Response times and classification accuracy

## 🏗️ Architecture

```
├── main.py                 # Main Flask application with enhanced features
├── model/                  # Database models and configuration
│   ├── config.py          # Database and AI configuration
│   ├── models.py          # SQLAlchemy models for all entities
│   └── __init__.py
├── utilities/              # AI and processing utilities
│   ├── context_manager.py # Conversation context management
│   ├── classifier.py      # GPS Control intent classification
│   ├── dataset_gpscontrol.json # Training dataset
│   └── __init__.py
├── templates/              # HTML templates for web interface
│   ├── index.html         # Main chat interface
│   ├── dashboard.html     # Admin dashboard
│   └── base_dashboard.html # Dashboard layout
├── static/                 # Static assets (CSS, JS, images, videos)
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   ├── images/           # GPS Control branding
│   ├── videos/           # Product demonstration videos
│   └── sounds/           # Audio notifications
├── setup_database.sql     # Database initialization script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- OpenAI API Key
- Meta Developer Account (for WhatsApp/Messenger)

### 1. Clone and Setup Environment
```bash
cd /home/marketing/elmachin
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create database
mysql -u root -p < setup_database.sql

# Verify tables created
mysql -u root -p -D chatbot_armaddia -e "SHOW TABLES;"
```

### 3. Environment Configuration
Create `.env` file:
```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:GPSc0ntr0l&1@localhost/chatbot_armaddia

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Meta API Configuration  
VERIFY_TOKEN=your_verify_token_here
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
MESSENGER_PAGE_ACCESS_TOKEN=your_messenger_token_here

# Security
SECRET_KEY=gps_control_secret_key_2024

# Server Configuration
PORT=5001
HOST=0.0.0.0
```

### 4. Start the Application
```bash
python main.py
```

The server will start on `http://localhost:5001`

## 🌐 Endpoints

### Web Interface
- **Main Chat**: `http://localhost:5001/`
- **Admin Dashboard**: `http://localhost:5001/dashboard`
- **API Status**: `http://localhost:5001/status`
- **Health Check**: `http://localhost:5001/health`

### Webhook Endpoints  
- **WhatsApp**: `https://yourdomain.com/webhook-whatsapp`
- **Messenger**: `https://yourdomain.com/webhook-messenger`

### API Endpoints
- **Conversations**: `GET /api/conversations?page=1&per_page=50`
- **Statistics**: `GET /api/stats`

## 🔧 Configuration

### Database Models
The system includes several key models:
- **User**: System users and authentication
- **Seller**: GPS Control sales representatives
- **Conversation**: All chat interactions with metadata
- **ChatReport**: User interaction summaries
- **UserContext**: Session and context management
- **QuoteService**: Quote request tracking

### AI Configuration
Located in `model/config.py`:
```python
OPENAI_CONFIG = {
    'model': 'gpt-4o-mini-2024-07-18',
    'max_tokens': 500,
    'temperature': 0.7
}

CONTEXT_CONFIG = {
    'max_context_length': 10,
    'context_timeout': 1800,  # 30 minutes
    'intent_confidence_threshold': 0.6
}
```

### GPS Control Dataset
The system includes a comprehensive dataset (`utilities/dataset_gpscontrol.json`) with:
- 4,800+ pre-trained responses
- Intent classification examples
- GPS Control specific terminology
- Video content integration

## 🎯 GPS Control Services

The chatbot specializes in:

### 📍 GPS Satellite Tracking
- Real-time vehicle location
- Route history and optimization  
- Geofences and alerts
- Fleet management solutions

### 📹 Security Cameras
- Cloud recording and storage
- Night vision capabilities
- Remote access via mobile app
- Motion detection alerts

### 🛡️ 24/7 Monitoring Center
- Dedicated security team
- Emergency response coordination
- Technical support
- Incident management

### ⚡ Advanced Features  
- ADAS/DMS camera systems
- Fuel consumption monitoring
- Cold chain temperature control
- Preventive maintenance alerts

## 📊 Dashboard Features

### Real-time Monitoring
- Live conversation feed
- Active user sessions
- Response time metrics
- System health status

### Analytics & Reports
- Intent distribution charts
- User engagement metrics
- Conversion tracking
- Performance analytics

### Conversation Management
- Message history browser
- Context visualization
- Intent confidence scoring
- Response quality assessment

## 🔒 Security Features

- **Input Validation**: All user inputs sanitized
- **Rate Limiting**: API request throttling
- **Session Management**: Secure user contexts
- **Database Security**: Parameterized queries
- **Environment Variables**: Sensitive data protection

## 📱 Mobile Integration

### WhatsApp Business
```
Webhook URL: https://yourdomain.com/webhook-whatsapp  
Verify Token: your_verify_token_here
```

### Facebook Messenger
```
Webhook URL: https://yourdomain.com/webhook-messenger
Verify Token: your_verify_token_here  
```

## 🧪 Testing

### Test Webhook Endpoints
```bash
# WhatsApp verification
curl -X GET "https://yourdomain.com/webhook-whatsapp?hub.mode=subscribe&hub.challenge=test&hub.verify_token=your_verify_token"

# Messenger verification  
curl -X GET "https://yourdomain.com/webhook-messenger?hub.mode=subscribe&hub.challenge=test&hub.verify_token=your_verify_token"
```

### Test AI Responses
```python
from utilities.classifier import classify_message
from utilities.context_manager import get_contextual_response

# Test GPS Control classification
response, intent, confidence = classify_message("Quiero cotizar GPS para mi auto")
print(f"Response: {response}")
print(f"Intent: {intent} (confidence: {confidence})")

# Test contextual response
response, intent, confidence = get_contextual_response("Hola", "test_user", "web")
print(f"Contextual response: {response}")
```

## 📈 Performance Optimization

### Database Indexing
```sql
-- Add indexes for better performance
CREATE INDEX idx_conversations_user_channel ON conversations(user_id, channel);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_chat_reports_user_channel ON chat_reports(user_id, channel);
```

### Caching Strategy
- **Context Caching**: User sessions cached in memory
- **Response Caching**: Common responses cached for faster delivery
- **Database Connection Pooling**: Optimized database connections

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check MySQL service
   sudo systemctl status mysql
   
   # Test connection
   mysql -u root -p -h localhost -D chatbot_armaddia
   ```

2. **WhatsApp Webhook Not Working**
   ```bash
   # Check webhook URL accessibility
   curl -X GET "https://yourdomain.com/webhook-whatsapp"
   
   # Verify SSL certificate
   curl -I "https://yourdomain.com/webhook-whatsapp"
   ```

3. **OpenAI API Errors**
   ```bash
   # Test API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

### Logs and Debugging
```bash
# View application logs
tail -f logs/chatbot.log

# Check database queries
tail -f /var/log/mysql/mysql.log

# Monitor system resources
htop
```

## 📋 Deployment

### Production Deployment with Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL Configuration  
```bash
# Install SSL certificate (Let's Encrypt)
sudo certbot --nginx -d yourdomain.com
```

### Process Management with Systemd
```ini
# /etc/systemd/system/gps-chatbot.service
[Unit]
Description=GPS Control Chatbot
After=network.target

[Service]
Type=simple
User=marketing
WorkingDirectory=/home/marketing/elmachin
Environment=PATH=/home/marketing/elmachin/venv/bin
ExecStart=/home/marketing/elmachin/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add enhancement'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

## 📞 Support

For technical support or GPS Control services:
- **Phone**: +52 55 1234 5678
- **Email**: soporte@gpscontrol.mx  
- **Website**: https://gpscontrol.mx
- **Dashboard**: https://elmachin.armaddia.lat/dashboard

## 📄 License

This project is proprietary software developed for GPS Control by Armaddia Systems.

## 🏆 Credits

**Development Team:**
- Enhanced system architecture and AI integration
- Database optimization and security implementations  
- Multi-channel webhook management
- GPS Control domain expertise integration

**Original GPS Control System:**
- Base chatbot logic and dataset
- Video content and branding assets
- Business logic and service definitions

---

**Version**: 2.0.0  
**Last Updated**: September 25, 2025  
**Status**: Production Ready ✅