# ChatGPT WhatsApp & Messenger Webhook

A simplified Flask application that integrates **WhatsApp Business API** and **Facebook Messenger** webhooks with **OpenAI's ChatGPT**, providing AI-powered responses to incoming messages from both platforms.

## 🚀 Features

- ✅ **WhatsApp Business Cloud API** webhook handling
- ✅ **Facebook Messenger** webhook handling  
- ✅ **OpenAI ChatGPT** integration for intelligent responses
- ✅ **Async message processing** with aiohttp
- ✅ **Multi-language support** (auto-detects Spanish/English)
- ✅ **Error handling and logging**
- ✅ **Health check endpoints**

## 📋 Prerequisites

1. **Meta Developer Account** - [developers.facebook.com](https://developers.facebook.com)
2. **OpenAI API Key** - [platform.openai.com](https://platform.openai.com)
3. **Python 3.8+**
4. **Public HTTPS URL** (for webhook endpoints)

## 🛠️ Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements-app.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys and tokens
nano .env
```

Fill in these required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `MESSENGER_PAGE_ACCESS_TOKEN` - Meta Messenger page access token  
- `WHATSAPP_ACCESS_TOKEN` - Meta WhatsApp Business access token
- `WHATSAPP_PHONE_NUMBER_ID` - Your WhatsApp Business phone number ID
- `VERIFY_TOKEN` - A random string for webhook verification

### 3. Run the Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000` by default.

### 4. Configure Meta Webhooks

#### For WhatsApp:
1. Go to **Meta Developers Console** → Your App → **WhatsApp** → **Configuration**
2. Set **Webhook URL**: `https://yourdomain.com/webhook-whatsapp`
3. Set **Verify Token**: Same value as `VERIFY_TOKEN` in your `.env`
4. Subscribe to **messages** webhook fields

#### For Messenger:
1. Go to **Meta Developers Console** → Your App → **Messenger** → **Settings**  
2. Set **Webhook URL**: `https://yourdomain.com/webhook-messenger`
3. Set **Verify Token**: Same value as `VERIFY_TOKEN` in your `.env`
4. Subscribe to **messages** webhook events

## 📱 How It Works

### Message Flow:
1. **User sends message** → WhatsApp/Messenger
2. **Meta sends webhook** → Your server (`/webhook-whatsapp` or `/webhook-messenger`)
3. **Server extracts message** → Sends to ChatGPT API
4. **ChatGPT responds** → Server sends reply back to user via Meta APIs

### Supported Message Types:
- ✅ **Text messages** (automatically processed)
- ❌ **Media messages** (ignored, but logged)
- ❌ **Interactive messages** (ignored, but logged)

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Status page with service info |
| `/health` | GET | Health check endpoint |
| `/webhook-whatsapp` | GET/POST | WhatsApp webhook handler |
| `/webhook-messenger` | GET/POST | Messenger webhook handler |

## 🐛 Debugging

### Check Logs
The application uses Python's logging module. All webhook events and errors are logged to console.

### Test Webhooks Locally
Use tools like [ngrok](https://ngrok.com/) to expose your local server:

```bash
# Install ngrok first, then:
ngrok http 5000

# Use the HTTPS URL (e.g., https://abc123.ngrok.io) as your webhook URL
```

### Verify Configuration
Visit `http://localhost:5000/` to see the status page and check if all tokens are configured.

## 🔐 Security Notes

- **Never commit** your `.env` file to version control
- **Use HTTPS** for production webhook URLs
- **Rotate API keys** regularly  
- **Validate webhook signatures** in production (not implemented in this simple version)

## 🌍 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 5000) |
| `VERIFY_TOKEN` | Yes | Meta webhook verification token |
| `MESSENGER_PAGE_ACCESS_TOKEN` | Yes* | Facebook Messenger access token |
| `WHATSAPP_ACCESS_TOKEN` | Yes* | WhatsApp Business access token |
| `WHATSAPP_PHONE_NUMBER_ID` | Yes* | WhatsApp Business phone number ID |
| `OPENAI_API_KEY` | Yes | OpenAI API key for ChatGPT |

*Required for the respective platform (WhatsApp or Messenger)

## 📝 Example Usage

Once configured, users can:

1. **Send a WhatsApp message** to your business number
2. **Send a Messenger message** to your Facebook page  
3. **Receive AI responses** powered by ChatGPT

Example conversation:
```
User: "Hola, ¿cómo estás?"
ChatGPT: "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?"

User: "What's the weather like?"  
ChatGPT: "I don't have access to real-time weather data, but I'd be happy to help you with other questions!"
```

## 🎯 Next Steps

To enhance this basic implementation, consider adding:

- **Webhook signature verification** for security
- **User session management** for conversation context
- **Rate limiting** to prevent abuse
- **Database integration** for message history
- **Custom ChatGPT prompts** per use case
- **Rich media responses** (images, buttons, etc.)

## 🆘 Troubleshooting

**Common Issues:**

1. **"Webhook verification failed"**
   - Check that `VERIFY_TOKEN` matches in both `.env` and Meta console

2. **"Messages not being sent"** 
   - Verify access tokens are valid and not expired
   - Check Meta Developer Console for app permissions

3. **"OpenAI API errors"**
   - Ensure `OPENAI_API_KEY` is valid and has sufficient credits
   - Check OpenAI usage limits

4. **"Server not receiving webhooks"**
   - Ensure your server is publicly accessible via HTTPS
   - Check firewall and port settings

---

**Original Code Source:** Extracted and simplified from `chambella-docs/main.py` (Google A2A SDK integration)