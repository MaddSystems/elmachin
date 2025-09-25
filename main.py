#!/usr/bin/env python3
"""
Simplified WhatsApp & Messenger Webhook with ChatGPT Integration

This is a clean, simplified version extracted from the main.py file,
focusing only on Meta's webhook endpoints (WhatsApp & Messenger) 
with ChatGPT responses instead of the Google A2A SDK.

Key Features:
- WhatsApp Cloud API webhook handling
- Facebook Messenger webhook handling  
- OpenAI ChatGPT integration for responses
- Async message processing with aiohttp
- Basic error handling and logging

Author: Extracted from chambella-docs/main.py
"""

import asyncio
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import aiohttp
import openai
from asgiref.wsgi import WsgiToAsgi
import uvicorn
import eventlet

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app with Socket.IO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
asgi_app = WsgiToAsgi(app)

# =============================================================================
# CONFIGURATION
# =============================================================================

def get_env_var(key, default=None):
    """Get environment variable and strip whitespace"""
    value = os.getenv(key, default)
    if value is not None:
        value = value.strip()
    return value

# Set Flask secret key after function is defined
app.config['SECRET_KEY'] = get_env_var('SECRET_KEY', 'your_secret_key_here')

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

async def get_chatgpt_response(user_message: str, user_id: str = None) -> str:
    """
    Send user message to ChatGPT and get response
    """
    try:
        logger.info(f"Sending message to ChatGPT from user {user_id}: {user_message}")
        
        # Create the chat completion request
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-2024-07-18",  # switched to 4-mini
            messages=[
            {
                "role": "system", 
                "content": "You are a helpful assistant. Respond in a friendly and concise manner. If the user writes in Spanish, respond in Spanish. If in English, respond in English."
            },
            {
                "role": "user", 
                "content": user_message
            }
            ],
            max_tokens=500,  # Limit response length for messaging apps
            temperature=0.7
        )
        
        chatgpt_reply = response.choices[0].message.content.strip()
        logger.info(f"ChatGPT response for {user_id}: {chatgpt_reply}")
        return chatgpt_reply
        
    except openai.error.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        return "Lo siento, he alcanzado mi límite de uso por el momento. Intenta más tarde. / Sorry, I've reached my usage limit. Please try again later."
        
    except openai.error.InvalidRequestError as e:
        logger.error(f"OpenAI invalid request: {e}")
        return "Hubo un problema procesando tu mensaje. / There was a problem processing your message."
        
    except Exception as e:
        logger.error(f"Error getting ChatGPT response: {e}", exc_info=True)
        return "Disculpa, ocurrió un error. Intenta de nuevo. / Sorry, an error occurred. Please try again."

# =============================================================================
# UNIFIED MESSAGE PROCESSING
# =============================================================================

async def process_message_unified(message_text: str, sender_id: str, channel: str):
    """
    Unified message processor for all channels (WhatsApp, Messenger, Web)
    """
    try:
        logger.info(f"Processing message from {channel} user {sender_id}: '{message_text}'")
        
        # Get ChatGPT response
        chatgpt_response = await get_chatgpt_response(message_text, f"{channel}_{sender_id}")
        
        # Send response based on channel
        if channel == 'web':
            # Emit response to web interface via Socket.IO
            socketio.emit('bot_response', {
                'message': chatgpt_response,
                'sender_id': sender_id,
                'timestamp': datetime.now().isoformat()
            })
            return True
        else:
            # Try to send to WhatsApp or Messenger
            success = await send_message_async(channel, sender_id, chatgpt_response)
            
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