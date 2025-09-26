#!/usr/bin/env python3
"""
Enhanced GPS Control Chatbot with Multi-Channel Support

This enhanced version integrates the GPS Control chatbot system with:
- Advanced context management and intent recognition
- Database integration for conversation tracking  
- Multi-channel support (WhatsApp, Messenger, Web)
- GPS Control specific responses and workflows
- Dashboard and admin interface

Features:
- WhatsApp Cloud API webhook handling
- Facebook Messenger webhook handling  
- Advanced chatbot AI with context awareness
- Database conversation tracking
- Admin dashboard for chat management
- GPS Control specific intent classification

Author: Enhanced for GPS Control by Armaddia
"""

import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import aiohttp
import openai
from asgiref.wsgi import WsgiToAsgi
import uvicorn
import eventlet

# Import our enhanced modules
from model.config import DB_CONFIG, OPENAI_CONFIG, CONTEXT_CONFIG, GPSCONTROL_CONFIG
from model.models import (
    db, User, Seller, Conversation, ChatReport, UserContext, 
    QuoteService, get_or_create_chat_report, get_or_create_user_context
)
from utilities.context_manager import get_contextual_response, analyze_intent
from utilities.classifier import classify_message, get_suggested_responses

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Utility function
def get_env_var(key, default=None):
    """Get environment variable and strip whitespace"""
    value = os.getenv(key, default)
    if value is not None:
        value = value.strip()
    return value

# Initialize Flask app with Socket.IO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
asgi_app = WsgiToAsgi(app)

# Configure Flask app with database settings
app.config.update(DB_CONFIG)
app.config['SECRET_KEY'] = get_env_var('SECRET_KEY', 'gps_control_secret_key_2024')

# Initialize database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Meta API Configuration
VERIFY_TOKEN = get_env_var("VERIFY_TOKEN", "your_verify_token_here")
MESSENGER_PAGE_ACCESS_TOKEN = get_env_var("MESSENGER_PAGE_ACCESS_TOKEN")
WHATSAPP_ACCESS_TOKEN = get_env_var("WHATSAPP_ACCESS_TOKEN") 
WHATSAPP_PHONE_NUMBER_ID = get_env_var("WHATSAPP_PHONE_NUMBER_ID")

# OpenAI Configuration
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Server Configuration  
PORT = int(os.environ.get("PORT", 5001))  # Changed to avoid conflict with existing server
HOST = os.environ.get("HOST", "0.0.0.0")

logger.info(f"""
=== CHATGPT WEBHOOK SERVER CONFIGURATION ===
VERIFY_TOKEN: {VERIFY_TOKEN}
MESSENGER_TOKEN: {'SET' if MESSENGER_PAGE_ACCESS_TOKEN else 'NOT SET'}
WHATSAPP_TOKEN: {'SET' if WHATSAPP_ACCESS_TOKEN else 'NOT SET'}  
WHATSAPP_PHONE_ID: {WHATSAPP_PHONE_NUMBER_ID}
OPENAI_KEY: {'SET' if OPENAI_API_KEY else 'NOT SET'}
Server: {HOST}:{PORT}
=============================================""")

# =============================================================================
# OPENAI CHATGPT INTEGRATION
# =============================================================================

async def get_enhanced_chatbot_response(user_message: str, user_id: str, channel: str = "web") -> str:
    """
    Enhanced chatbot response using context management and GPS Control classification
    """
    try:
        logger.info(f"Processing message from user {user_id} via {channel}: {user_message}")
        
        # First, try GPS Control specific classification
        gps_response, gps_intent, gps_confidence = classify_message(user_message)
        
        if gps_confidence > 0.4:  # Use GPS Control response if confident
            logger.info(f"Using GPS Control response (confidence: {gps_confidence:.2f})")
            
            # Save conversation to database
            await save_conversation(user_id, channel, user_message, gps_response, gps_intent, gps_confidence)
            
            return gps_response
        
        # If GPS Control classifier isn't confident, use context manager
        context_response, context_intent, context_confidence = get_contextual_response(
            user_message, user_id, channel
        )
        
        if context_confidence > 0.3:
            logger.info(f"Using context response (confidence: {context_confidence:.2f})")
            
            # Save conversation to database
            await save_conversation(user_id, channel, user_message, context_response, context_intent, context_confidence)
            
            return context_response
        
        # Fallback to enhanced ChatGPT with GPS Control context
        chatgpt_response = await get_chatgpt_with_gps_context(user_message, user_id, channel)
        
        # Save conversation to database
        await save_conversation(user_id, channel, user_message, chatgpt_response, "chatgpt_fallback", 0.8)
        
        return chatgpt_response
        
    except Exception as e:
        logger.error(f"Error in enhanced chatbot response: {e}")
        return "Disculpa, tuve un problema técnico. ¿Podrías repetir tu mensaje? 🤔"

async def get_chatgpt_with_gps_context(user_message: str, user_id: str, channel: str) -> str:
    """
    Send user message to ChatGPT with GPS Control context
    """
    try:
        # Get conversation context
        recent_conversations = await get_recent_conversations(user_id, channel)
        
        # Build context-aware prompt
        system_prompt = f"""Eres Machín, el asistente virtual de GPS Control, una empresa mexicana líder en rastreo satelital y seguridad vehicular.

INFORMACIÓN DE LA EMPRESA:
- Nombre: GPS Control by Machín
- Servicios: Rastreo GPS satelital, cámaras de seguridad, monitoreo 24/7
- Especialidades: Soluciones para particulares y empresas
- Ubicación: México
- Teléfono: {GPSCONTROL_CONFIG['support_phone']}
- Email: {GPSCONTROL_CONFIG['support_email']}

PERSONALIDAD:
- Amigable y profesional
- Conocedor de tecnología GPS y seguridad
- Enfocado en ayudar al cliente
- Usa emojis moderadamente
- Responde en español mexicano

SERVICIOS PRINCIPALES:
1. GPS Satelital: Rastreo en tiempo real, geocercas, reportes
2. Cámaras de Seguridad: Grabación en nube, visión nocturna, acceso remoto
3. Monitoreo 24/7: Centro de control dedicado
4. Soluciones Empresariales: Gestión de flotas, optimización de rutas

INSTRUCCIONES:
- Si preguntan por precios, solicita detalles (tipo de vehículo, cantidad, uso)
- Ofrece videos explicativos cuando sea relevante
- Menciona beneficios específicos de GPS Control
- Deriva a cotización cuando sea apropiado
- Mantén respuestas concisas pero completas"""

        # Add conversation history if available
        messages = [{"role": "system", "content": system_prompt}]
        
        if recent_conversations:
            for conv in recent_conversations[-3:]:  # Last 3 conversations
                messages.append({"role": "user", "content": conv['message']})
                messages.append({"role": "assistant", "content": conv['response']})
        
        messages.append({"role": "user", "content": user_message})
        
        # Create the chat completion request
        response = openai.ChatCompletion.create(
            model=OPENAI_CONFIG['model'],
            messages=messages,
            max_tokens=OPENAI_CONFIG['max_tokens'],
            temperature=OPENAI_CONFIG['temperature']
        )
        
        chatgpt_response = response.choices[0].message.content.strip()
        logger.info(f"ChatGPT response generated for user {user_id}")
        
        return chatgpt_response
        
    except openai.error.RateLimitError:
        logger.warning("OpenAI rate limit exceeded")
        return "Estoy recibiendo muchas consultas. Por favor intenta en unos momentos. 🕒"
        
    except openai.error.InvalidRequestError as e:
        logger.error(f"OpenAI invalid request: {e}")
        return "Disculpa, hubo un problema con tu consulta. ¿Podrías reformularla? 🤔"
        
    except Exception as e:
        logger.error(f"Error calling ChatGPT API: {e}")
        return "Disculpa, tengo un problema técnico temporal. ¿Podrías intentar de nuevo? ⚠️"

# =============================================================================
# DATABASE HELPER FUNCTIONS
# =============================================================================

async def save_conversation(user_id: str, channel: str, message: str, response: str, intent: str, confidence: float):
    """Save conversation to database"""
    try:
        # Create new conversation record
        conversation = Conversation(
            user_id=user_id,
            channel=channel,
            message=message,
            response=response,
            intent=intent,
            confidence=confidence,
            session_id=f"{user_id}_{channel}_{datetime.now().strftime('%Y%m%d')}"
        )
        
        db.session.add(conversation)
        
        # Update or create chat report
        chat_report = get_or_create_chat_report(user_id, channel)
        chat_report.message_count += 1
        chat_report.last_interaction = datetime.now()
        
        # Update intent summary
        if chat_report.intent_summary is None:
            chat_report.intent_summary = {}
        
        if intent in chat_report.intent_summary:
            chat_report.intent_summary[intent] += 1
        else:
            chat_report.intent_summary[intent] = 1
        
        db.session.commit()
        logger.info(f"Conversation saved for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        db.session.rollback()

async def get_recent_conversations(user_id: str, channel: str, limit: int = 5):
    """Get recent conversations for context"""
    try:
        conversations = Conversation.query.filter_by(
            user_id=user_id,
            channel=channel
        ).order_by(
            Conversation.created_at.desc()
        ).limit(limit).all()
        
        return [conv.to_dict() for conv in conversations]
        
    except Exception as e:
        logger.error(f"Error getting recent conversations: {e}")
        return []

# =============================================================================
# UNIFIED MESSAGE PROCESSING
# =============================================================================

async def process_message_unified(message_text: str, sender_id: str, channel: str):
    """
    Unified message processor for all channels (WhatsApp, Messenger, Web)
    """
    try:
        logger.info(f"Processing message from {channel} user {sender_id}: '{message_text}'")
        
        # Get enhanced chatbot response with GPS Control context
        bot_response = await get_enhanced_chatbot_response(message_text, sender_id, channel)
        
        # Send response based on channel
        if channel == 'web':
            # Emit response to web interface via Socket.IO
            socketio.emit('bot_response', {
                'message': bot_response,
                'sender_id': sender_id,
                'timestamp': datetime.now().isoformat()
            })
            return True
        else:
            # Try to send to WhatsApp or Messenger
            success = await send_message_async(channel, sender_id, bot_response)
            
            # If WhatsApp fails, try template message for re-engagement
            if not success and channel == 'whatsapp':
                logger.info(f"Attempting template message for WhatsApp re-engagement to {sender_id}")
                template_success = await send_whatsapp_template_message(sender_id)
                if template_success:
                    logger.info(f"Template message sent successfully to {sender_id}")
                    return True
            
            return success
            
    except Exception as e:
        logger.error(f"Error in unified message processing: {e}", exc_info=True)
        
        if channel == 'web':
            socketio.emit('error_response', {
                'error': 'Failed to process message',
                'sender_id': sender_id
            })
        return False

# =============================================================================
# MESSAGE SENDING FUNCTIONS
# =============================================================================

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number for WhatsApp API - remove leading country code duplication"""
    # Remove any non-digit characters first
    phone = ''.join(filter(str.isdigit, phone))
    
    # Handle Mexican numbers: if starts with 5215, convert to 525 (keep the 5)
    if phone.startswith('5215'):
        phone = '525' + phone[4:]  # Remove only the '1', keep the '5'
        logger.info(f"Normalized Mexican number: {phone}")
    
    return phone

async def send_whatsapp_template_message(recipient_id: str, template_name: str = "hello_world") -> bool:
    """Send a WhatsApp template message for re-engagement"""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        logger.error("WhatsApp configuration not set")
        return False
    
    # Normalize phone number
    normalized_recipient = normalize_phone_number(recipient_id)
    
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": normalized_recipient,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"}  # Match your working curl
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=15) as response:
                if response.status == 200:
                    response_json = await response.json()
                    logger.info(f"WhatsApp template sent to {recipient_id}: {response_json}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"WhatsApp template error {response.status}: {error_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"WhatsApp template send error: {e}")
        return False

async def send_whatsapp_message(recipient_id: str, message: str) -> bool:
    """Send a WhatsApp message using the WhatsApp Cloud API"""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        logger.error("WhatsApp configuration not set")
        return False
    
    # Normalize phone number
    normalized_recipient = normalize_phone_number(recipient_id)
    
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": normalized_recipient,
        "type": "text", 
        "text": {"body": message}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=15) as response:
                if response.status == 200:
                    response_json = await response.json()
                    logger.info(f"WhatsApp message sent to {recipient_id}: {response_json}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"WhatsApp API error {response.status}: {error_text}")
                    
                    # Parse error and provide specific solutions
                    try:
                        error_data = json.loads(error_text)
                        error_code = error_data.get('error', {}).get('code')
                        
                        if error_code == 131030:
                            logger.error(f"⚠️  SOLUTION: Add {recipient_id} to WhatsApp Business allowed recipients list in Meta Developer Console")
                        elif error_code == 131047:
                            logger.error(f"⚠️  SOLUTION: Use a template message to re-engage {recipient_id} (24hr+ window)")
                        elif error_code == 100:
                            logger.error(f"⚠️  SOLUTION: Check WhatsApp access token or phone number ID")
                            
                    except json.JSONDecodeError:
                        pass
                    
                    return False
                    
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return False

async def send_messenger_message(recipient_id: str, message: str) -> bool:
    """Send a Facebook Messenger message using the Messenger Platform API"""
    if not MESSENGER_PAGE_ACCESS_TOKEN:
        logger.error("Messenger configuration not set")
        return False
    
    url = "https://graph.facebook.com/v22.0/me/messages"
    params = {"access_token": MESSENGER_PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, json=payload, timeout=15) as response:
                if response.status == 200:
                    response_json = await response.json()
                    logger.info(f"Messenger message sent to {recipient_id}: {response_json}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Messenger API error {response.status}: {error_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"Messenger send error: {e}")
        return False

async def send_message_async(channel: str, recipient_id: str, message: str) -> bool:
    """Dispatch message to correct platform"""
    if channel == 'whatsapp':
        return await send_whatsapp_message(recipient_id, message)
    elif channel == 'messenger':
        return await send_messenger_message(recipient_id, message)
    else:
        logger.error(f"Unsupported channel: {channel}")
        return False

# =============================================================================
# WEBSOCKET EVENTS FOR WEB INTERFACE
# =============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection to web interface"""
    logger.info("Web client connected")
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection from web interface"""
    logger.info("Web client disconnected")

@socketio.on('user_message')
def handle_user_message(data):
    """Handle incoming message from web interface"""
    try:
        message_text = data.get('message', '').strip()
        session_id = data.get('session_id', 'unknown')
        channel = data.get('channel', 'web')
        
        if message_text:
            # Process message asynchronously
            eventlet.spawn(asyncio_wrapper, process_message_unified, message_text, session_id, channel)
        else:
            emit('error_response', {'error': 'Empty message'})
            
    except Exception as e:
        logger.error(f"Error handling web message: {e}", exc_info=True)
        emit('error_response', {'error': 'Failed to process message'})

def asyncio_wrapper(func, *args, **kwargs):
    """Wrapper to run async functions in eventlet"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(func(*args, **kwargs))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in asyncio wrapper: {e}")
        return None

# =============================================================================
# WEBHOOK ENDPOINTS
# =============================================================================

@app.route("/webhook-messenger", methods=["GET", "POST"])
async def webhook_messenger():
    """Handle webhook requests from Facebook Messenger"""
    
    if request.method == "GET":
        # Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token") 
        challenge = request.args.get("hub.challenge")
        
        if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Messenger webhook verified successfully")
            return challenge, 200
        else:
            logger.warning("Messenger webhook verification failed")
            return "Verification failed", 403
    
    elif request.method == "POST":
        # Process incoming messages
        data = request.json
        logger.info(f"Received Messenger webhook: {json.dumps(data, indent=2)}")
        
        try:
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    # Extract sender ID and message text
                    sender_id = messaging_event.get("sender", {}).get("id")
                    if not sender_id:
                        continue
                    
                    message_data = messaging_event.get("message", {})
                    message_text = message_data.get("text", "")
                    
                    if message_text:
                        # Use unified message processor
                        await process_message_unified(message_text, sender_id, "messenger")
                    
                    else:
                        logger.info(f"Received non-text message from {sender_id}, ignoring")
            
            return "EVENT_RECEIVED", 200
            
        except Exception as e:
            logger.error(f"Error processing Messenger webhook: {e}", exc_info=True)
            return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@app.route("/webhook-whatsapp", methods=["GET", "POST"])  
async def webhook_whatsapp():
    """Handle webhook requests from WhatsApp Cloud API"""
    
    if request.method == "GET":
        # Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("WhatsApp webhook verified successfully")
            return challenge, 200
        else:
            logger.warning("WhatsApp webhook verification failed")
            return "Verification failed", 403
    
    elif request.method == "POST":
        # Process incoming messages
        data = request.json
        logger.info(f"Received WhatsApp webhook: {json.dumps(data, indent=2)}")
        
        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message_event in value["messages"]:
                            # Extract sender ID and message text
                            sender_id = message_event["from"]
                            message_text = message_event.get("text", {}).get("body", "")
                            
                            if message_text:
                                # Use unified message processor
                                await process_message_unified(message_text, sender_id, "whatsapp")
                            
                            else:
                                logger.info(f"Received non-text WhatsApp message from {sender_id}, ignoring")
            
            return "EVENT_RECEIVED", 200
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {e}", exc_info=True)
            return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# =============================================================================
# DASHBOARD AND ADMIN ROUTES
# =============================================================================

@app.route("/dashboard")
def dashboard():
    """Admin dashboard for conversation monitoring"""
    try:
        # Get conversation statistics
        total_conversations = Conversation.query.count()
        total_users = db.session.query(Conversation.user_id).distinct().count()
        
        # Get recent conversations
        recent_conversations = Conversation.query.order_by(
            Conversation.created_at.desc()
        ).limit(10).all()
        
        # Get intent statistics
        intent_stats = {}
        conversations_with_intent = Conversation.query.filter(
            Conversation.intent.isnot(None)
        ).all()
        
        for conv in conversations_with_intent:
            intent = conv.intent
            if intent in intent_stats:
                intent_stats[intent] += 1
            else:
                intent_stats[intent] = 1
        
        return render_template('dashboard.html', 
                             total_conversations=total_conversations,
                             total_users=total_users,
                             recent_conversations=recent_conversations,
                             intent_stats=intent_stats)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return f"Error loading dashboard: {e}", 500

@app.route("/api/conversations")
def api_conversations():
    """API endpoint for conversation data"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        conversations = Conversation.query.order_by(
            Conversation.created_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations.items],
            'total': conversations.total,
            'pages': conversations.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/stats")
def api_stats():
    """API endpoint for statistics"""
    try:
        stats = {
            'total_conversations': Conversation.query.count(),
            'total_users': db.session.query(Conversation.user_id).distinct().count(),
            'conversations_today': Conversation.query.filter(
                Conversation.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count(),
            'top_intents': {}
        }
        
        # Get top intents
        intents = db.session.query(
            Conversation.intent, 
            db.func.count(Conversation.intent)
        ).filter(
            Conversation.intent.isnot(None)
        ).group_by(Conversation.intent).order_by(
            db.func.count(Conversation.intent).desc()
        ).limit(10).all()
        
        stats['top_intents'] = {intent: count for intent, count in intents}
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# WEB CHAT ENDPOINT
# =============================================================================

@app.route("/chat", methods=["POST"])
def chat():
    """Handle web chat messages via HTTP POST"""
    try:
        data = request.get_json()
        message_text = data.get('message', '').strip()
        chat_id = data.get('chat_id', '')
        who_is_connected = data.get('who_is_conected', '')
        
        if not message_text:
            return jsonify({'error': 'Empty message'}), 400
        
        # Use chat_id as session_id if available, otherwise generate one
        session_id = chat_id if chat_id else f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Process message asynchronously using our unified processor
        def process_and_respond():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    get_enhanced_chatbot_response(message_text, session_id, "web")
                )
                loop.close()
                return result
            except Exception as e:
                logger.error(f"Error in chat processing: {e}")
                return "¡Ups! Lo siento, algo salió mal. Por favor, intenta nuevamente más tarde o contacta a uno de nuestros asesores para obtener ayuda. ¡Gracias por tu paciencia!"
        
        bot_response = process_and_respond()
        
        # Return response in the format expected by the frontend
        return jsonify({
            'response': bot_response,
            'status': 'success',
            'chat_id': session_id,
            'quick_responses': []  # Can add quick responses here later
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return jsonify({
            'response': '¡Ups! Lo siento, algo salió mal. Por favor, intenta nuevamente más tarde o contacta a uno de nuestros asesores para obtener ayuda. ¡Gracias por tu paciencia!',
            'error': 'Processing failed'
        }), 500

# =============================================================================
# BASIC ROUTES
# =============================================================================

@app.route("/")
def index():
    """Serve the web chat interface"""
    return render_template('index.html')

@app.route("/status")
def status():
    """API status endpoint"""
    return jsonify({
        "status": "running",
        "service": "ChatGPT Multi-Channel Bot (Web + WhatsApp + Messenger)",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "web_interface": "/",
            "whatsapp": "/webhook-whatsapp",
            "messenger": "/webhook-messenger",
            "status": "/status",
            "health": "/health"
        },
        "channels": ["web", "whatsapp", "messenger"]
    })

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# =============================================================================
# SERVER STARTUP
# =============================================================================

def main():
    """Start the multi-channel ChatGPT server"""
    print("🤖 Starting Multi-Channel ChatGPT Bot Server...")
    print(f"🌐 Web Interface: http://{HOST}:{PORT}/")
    print(f"📱 WhatsApp Webhook: http://{HOST}:{PORT}/webhook-whatsapp")
    print(f"💬 Messenger Webhook: http://{HOST}:{PORT}/webhook-messenger") 
    print(f"� Status API: http://{HOST}:{PORT}/status")
    print(f"❤️  Health Check: http://{HOST}:{PORT}/health")
    print("=" * 70)
    print("✨ All channels (Web, WhatsApp, Messenger) use the same ChatGPT bot!")
    print("=" * 70)
    
    # Use SocketIO server instead of uvicorn for WebSocket support
    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    main()