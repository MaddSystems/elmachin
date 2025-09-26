"""
Database models for the enhanced chatbot system
Based on the original elmachin.custodiayvigilancia.mx models but adapted for chatbot_armaddia
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

# Create SQLAlchemy instance
db = SQLAlchemy()

# Core Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Seller(db.Model):
    __tablename__ = 'sellers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    territory = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "territory": self.territory,
            "status": self.status
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(20), nullable=False)  # whatsapp, messenger, web
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    intent = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    context_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    session_id = db.Column(db.String(100), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=True)

    # Relationship
    seller = db.relationship('Seller', backref=db.backref('conversations', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "message": self.message,
            "response": self.response,
            "intent": self.intent,
            "confidence": self.confidence,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "session_id": self.session_id,
            "seller": self.seller.to_dict() if self.seller else None
        }

class ChatReport(db.Model):
    __tablename__ = 'chat_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    message_count = db.Column(db.Integer, default=0)
    last_interaction = db.Column(db.DateTime, nullable=True)
    intent_summary = db.Column(db.JSON, nullable=True)
    satisfaction_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "message_count": self.message_count,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "intent_summary": self.intent_summary,
            "satisfaction_score": self.satisfaction_score,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Process and Context Management Models
class Process(db.Model):
    __tablename__ = 'processes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    intention = db.Column(db.String(100), nullable=True)
    tag = db.Column(db.String(20), nullable=True)
    steps = db.Column(db.JSON, nullable=True)  # List of steps/questions
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class UserContext(db.Model):
    __tablename__ = 'user_context'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    current_intent = db.Column(db.String(100), nullable=True)
    context_data = db.Column(db.JSON, default={})
    last_message = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def is_expired(self):
        return self.expires_at and datetime.now() > self.expires_at

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "current_intent": self.current_intent,
            "context_data": self.context_data,
            "last_message": self.last_message,
            "session_id": self.session_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

# Quote and Service Models
class QuoteService(db.Model):
    __tablename__ = 'quote_service'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    service_type = db.Column(db.String(50), nullable=True)  # GPS tracking, cameras, etc.
    quantity_units = db.Column(db.String(20), nullable=True)
    client_type = db.Column(db.String(20), nullable=True)  # empresarial, particular
    location = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='pending')  # pending, in_progress, completed, cancelled
    contact_info = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

# Training and Classification Models
class DataClass(db.Model):
    __tablename__ = 'data_classifications'
    id = db.Column(db.Integer, primary_key=True)
    classification = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class DataIntent(db.Model):
    __tablename__ = 'data_intents'
    id = db.Column(db.Integer, primary_key=True)
    intent = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    classification_id = db.Column(db.Integer, db.ForeignKey('data_classifications.id'), nullable=True)
    examples = db.Column(db.JSON, nullable=True)  # Example phrases
    response_template = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    classification = db.relationship('DataClass', backref=db.backref('intents', lazy=True))

# Dashboard Management
class DashboardChat(db.Model):
    __tablename__ = 'dashboard_chats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default='active')  # active, waiting, attended, closed
    assigned_seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    assigned_seller = db.relationship('Seller', backref=db.backref('assigned_chats', lazy=True))

# Helper functions
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_or_create_chat_report(user_id, channel):
    """Get existing chat report or create new one"""
    chat_report = ChatReport.query.filter_by(user_id=user_id, channel=channel).first()
    if not chat_report:
        chat_report = ChatReport(
            user_id=user_id,
            channel=channel,
            message_count=0,
            intent_summary={}
        )
        db.session.add(chat_report)
        db.session.commit()
    return chat_report

def get_or_create_user_context(user_id, channel, session_id=None):
    """Get existing user context or create new one"""
    context = UserContext.query.filter_by(
        user_id=user_id, 
        channel=channel
    ).first()
    
    if not context or context.is_expired():
        if context:
            db.session.delete(context)
        
        context = UserContext(
            user_id=user_id,
            channel=channel,
            session_id=session_id,
            context_data={},
            expires_at=datetime.now().replace(
                hour=datetime.now().hour + 1  # 1 hour expiry
            )
        )
        db.session.add(context)
        db.session.commit()
    
    return context