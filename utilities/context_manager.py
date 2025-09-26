"""
Context Management System for GPS Control Chatbot
Handles conversation context, intent recognition, and response generation
"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# GPS Control Keywords and Context
GPS_CONTROL_KEYWORDS = [
    "camaras de seguridad", "transmision en tiempo real", "grabacion en la nube", 
    "vision nocturna", "seguimiento en vivo", "alertas de video", "acceso remoto", 
    "evidencia visual", "monitoreo 24 7", "deteccion de movimiento", 
    "centro de control", "vigilancia continua", "seguimiento en tiempo real", 
    "soporte 24/7", "atencion personalizada", "alertas inmediatas", "respaldo de seguridad",
    "supervision activa", "intervencion rapida", "gestion de incidentes", 
    "gps", "rastreo satelital", "localizacion en tiempo real", 
    "geocercas", "rutas optimizadas", "informes de viaje", "historial de recorridos", 
    "velocidad promedio", "tiempo de parada", "mantenimiento predictivo", "telemetria", 
    "diagnostico remoto", "comportamiento del conductor", "analisis de datos", 
    "integracion con flotas", "movilidad inteligente", "vehiculos conectados", 
    "iot", "internet de las cosas", "plataforma de gestion", "aplicaciones moviles", 
    "interfaz de usuario", "reportes personalizados", "seguimiento de activos", 
    "control de flotas", "optimizacion de rutas", "reduccion de costos", 
    "seguridad vehicular", "monitoreo de temperatura", "control de acceso", 
    "sistemas de alarmas", "gestion de combustible", "eficiencia operativa",
    "rastreo de motos", "rastreo de camiones", "rastreo de maquinaria", 
    "rastreo de trailers", "rastreo de autobuses", "rastreo de bicicletas",
    "vehiculos electricos", "carros hibridos", "instalacion gps"
]

# Intent patterns for GPS Control services
INTENT_PATTERNS = {
    "cotizacion_gps": [
        r"cotiz[ar|ación].*gps", r"precio.*gps", r"costo.*rastreo",
        r"cuanto.*cuesta.*gps", r"quiero.*cotizar", r"necesito.*precio"
    ],
    "cotizacion_camaras": [
        r"cotiz[ar|ación].*camara", r"precio.*camara", r"costo.*video",
        r"cuanto.*cuesta.*camara", r"vigilancia", r"seguridad.*video"
    ],
    "informacion_servicios": [
        r"que.*servicios", r"como.*funciona", r"informacion", 
        r"caracteristicas", r"beneficios", r"ventajas"
    ],
    "instalacion": [
        r"como.*instalar", r"instalacion", r"donde.*instalan",
        r"cuanto.*tarda.*instalar", r"proceso.*instalacion"
    ],
    "soporte_tecnico": [
        r"soporte", r"ayuda", r"problema", r"no.*funciona",
        r"tecnico", r"falla", r"error"
    ],
    "vehiculos_especiales": [
        r"carro.*electrico", r"vehiculo.*hibrido", r"moto.*electrica",
        r"puede.*instalar.*en", r"compatible.*con"
    ],
    "saludo": [
        r"hola", r"buenos.*dias", r"buenas.*tardes", r"buenas.*noches",
        r"saludos", r"que.*tal", r"hi", r"hello"
    ],
    "despedida": [
        r"adios", r"hasta.*luego", r"nos.*vemos", r"gracias",
        r"bye", r"chau", r"hasta.*pronto"
    ]
}

# Response templates for different intents
RESPONSE_TEMPLATES = {
    "cotizacion_gps": [
        "¡Excelente! Te puedo ayudar con una cotización de GPS. Para darte el mejor precio necesito saber:",
        "📍 ¿Qué tipo de vehículo quieres rastrear? (auto, moto, camión, etc.)",
        "📊 ¿Cuántos vehículos necesitas rastrear?",
        "🏢 ¿Es para uso personal o empresarial?",
        "📍 ¿En qué ciudad o zona te encuentras?"
    ],
    "cotizacion_camaras": [
        "¡Perfecto! Las cámaras de seguridad son una excelente inversión. Para cotizarte necesito:",
        "📹 ¿Cuántas cámaras necesitas?",
        "🏠 ¿Es para casa, negocio o vehículo?", 
        "🌙 ¿Necesitas visión nocturna?",
        "📱 ¿Quieres acceso remoto desde tu celular?",
        "📍 ¿En qué zona vas a instalar?"
    ],
    "informacion_servicios": [
        "🚗 **Servicios GPS Control by Machín** 🚗",
        "",
        "📍 **GPS Satelital:**",
        "• Rastreo en tiempo real 24/7",
        "• Historial de rutas y paradas", 
        "• Geocercas y alertas",
        "• App móvil gratuita",
        "",
        "📹 **Cámaras de Seguridad:**",
        "• Grabación en la nube",
        "• Visión nocturna",
        "• Acceso remoto",
        "• Detección de movimiento",
        "",
        "⚡ **Centro de Monitoreo 24/7**",
        "• Atención inmediata",
        "• Intervención en emergencias", 
        "• Soporte técnico especializado",
        "",
        "¿Te interesa algún servicio en particular? 🤔"
    ],
    "vehiculos_especiales": [
        "¡Claro! Nuestros dispositivos GPS son totalmente compatibles con:",
        "🔋 Vehículos eléctricos (Tesla, Nissan Leaf, etc.)",
        "⚡ Vehículos híbridos",
        "🏍️ Motocicletas eléctricas",
        "🚛 Camiones eléctricos",
        "",
        "La instalación es segura y no afecta la garantía del vehículo.",
        "¿Te gustaría una cotización para tu vehículo específico? 🚗"
    ],
    "saludo": [
        "¡Hola! 👋 Soy Machín de GPS Control",
        "Estoy aquí para ayudarte con:",
        "📍 Rastreo GPS satelital",
        "📹 Cámaras de seguridad", 
        "🛡️ Monitoreo 24/7",
        "",
        "¿En qué te puedo ayudar hoy? 😊"
    ],
    "despedida": [
        "¡Gracias por contactarnos! 😊",
        "📞 Si tienes más preguntas, estoy aquí 24/7",
        "🌐 Visita: gpscontrol.mx",
        "📱 WhatsApp: +52 55 1234 5678",
        "¡Que tengas excelente día! 🌟"
    ],
    "instalacion": [
        "🔧 **Proceso de Instalación GPS Control:**",
        "",
        "1️⃣ **Agendar cita** (gratuita a domicilio)",
        "2️⃣ **Instalación profesional** (30-45 min)",
        "3️⃣ **Configuración y pruebas**",
        "4️⃣ **Capacitación en la app**",
        "",
        "✅ Instalación certificada",
        "✅ 1 año de garantía",
        "✅ Sin afectar garantía del vehículo",
        "",
        "¿En qué zona necesitas la instalación? 📍"
    ]
}

class ContextManager:
    """Manages conversation context and intent recognition for GPS Control chatbot"""
    
    def __init__(self):
        self.active_contexts = {}  # user_id -> context_data
        self.context_timeout = timedelta(minutes=30)
        
    def get_intent(self, message: str) -> Tuple[str, float]:
        """
        Analyze message and return most likely intent with confidence score
        """
        message_lower = message.lower()
        best_intent = "general"
        best_score = 0.0
        
        for intent, patterns in INTENT_PATTERNS.items():
            score = 0
            pattern_matches = 0
            
            for pattern in patterns:
                matches = len(re.findall(pattern, message_lower))
                if matches > 0:
                    pattern_matches += 1
                    score += matches
            
            # Calculate confidence based on pattern matches and keyword presence
            keyword_matches = sum(1 for keyword in GPS_CONTROL_KEYWORDS 
                                if keyword in message_lower)
            
            if pattern_matches > 0:
                confidence = min(0.9, (score + keyword_matches * 0.1) / len(patterns))
                if confidence > best_score:
                    best_score = confidence
                    best_intent = intent
        
        return best_intent, best_score
    
    def get_context(self, user_id: str, channel: str) -> Dict:
        """Get or create user context"""
        key = f"{user_id}_{channel}"
        
        if key not in self.active_contexts:
            self.active_contexts[key] = {
                "user_id": user_id,
                "channel": channel,
                "current_intent": None,
                "conversation_history": [],
                "quote_data": {},
                "last_activity": datetime.now(),
                "step": 0
            }
        
        # Check if context has expired
        context = self.active_contexts[key]
        if datetime.now() - context["last_activity"] > self.context_timeout:
            context = self._reset_context(key)
        
        return context
    
    def update_context(self, user_id: str, channel: str, message: str, 
                      intent: str, response: str) -> Dict:
        """Update user context with new interaction"""
        context = self.get_context(user_id, channel)
        
        # Update context data
        context["current_intent"] = intent
        context["last_activity"] = datetime.now()
        context["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "intent": intent,
            "response": response
        })
        
        # Keep only last 10 interactions
        if len(context["conversation_history"]) > 10:
            context["conversation_history"] = context["conversation_history"][-10:]
        
        return context
    
    def _reset_context(self, key: str) -> Dict:
        """Reset context for expired or new conversations"""
        user_id, channel = key.split("_", 1)
        self.active_contexts[key] = {
            "user_id": user_id,
            "channel": channel,
            "current_intent": None,
            "conversation_history": [],
            "quote_data": {},
            "last_activity": datetime.now(),
            "step": 0
        }
        return self.active_contexts[key]
    
    def generate_contextual_response(self, message: str, user_id: str, 
                                   channel: str) -> Tuple[str, str, float]:
        """
        Generate contextual response based on message and conversation history
        """
        context = self.get_context(user_id, channel)
        intent, confidence = self.get_intent(message)
        
        # Get base response template
        if intent in RESPONSE_TEMPLATES:
            base_response = RESPONSE_TEMPLATES[intent]
            if isinstance(base_response, list):
                response = "\n".join(base_response)
            else:
                response = base_response
        else:
            response = self._generate_gps_control_response(message, context)
        
        # Update context
        self.update_context(user_id, channel, message, intent, response)
        
        return response, intent, confidence
    
    def _generate_gps_control_response(self, message: str, context: Dict) -> str:
        """Generate GPS Control specific response"""
        message_lower = message.lower()
        
        # Check for specific GPS Control keywords
        if any(keyword in message_lower for keyword in ["precio", "costo", "cuanto"]):
            return ("Para darte un precio exacto necesito conocer más detalles. "
                   "¿Podrías decirme qué tipo de servicio te interesa: GPS, cámaras o ambos?")
        
        if any(keyword in message_lower for keyword in ["como funciona", "que incluye"]):
            return ("Nuestro sistema GPS Control incluye:\n"
                   "📍 Rastreo satelital 24/7\n"
                   "📱 App móvil gratuita\n" 
                   "🛡️ Centro de monitoreo\n"
                   "⚡ Alertas en tiempo real\n\n"
                   "¿Te gustaría más información sobre algún servicio específico?")
        
        if any(keyword in message_lower for keyword in ["instalacion", "instalar"]):
            return ("La instalación es muy sencilla:\n"
                   "✅ Agendamos cita gratuita\n"
                   "✅ Técnico certificado va a tu ubicación\n"
                   "✅ Instalación en 30-45 minutos\n"
                   "✅ Te enseñamos a usar la app\n\n"
                   "¿En qué zona necesitas la instalación?")
        
        # Default GPS Control response
        return ("¡Hola! Soy Machín de GPS Control 🤖\n\n"
               "Te puedo ayudar con:\n"
               "📍 Cotizaciones de GPS\n" 
               "📹 Cámaras de seguridad\n"
               "🔧 Información de instalación\n"
               "📞 Soporte técnico\n\n"
               "¿Qué servicio te interesa? 😊")
    
    def is_quote_in_progress(self, user_id: str, channel: str) -> bool:
        """Check if user has an active quote process"""
        context = self.get_context(user_id, channel)
        return bool(context.get("quote_data")) and context.get("current_intent") in [
            "cotizacion_gps", "cotizacion_camaras"
        ]
    
    def get_quote_data(self, user_id: str, channel: str) -> Dict:
        """Get current quote data for user"""
        context = self.get_context(user_id, channel)
        return context.get("quote_data", {})
    
    def update_quote_data(self, user_id: str, channel: str, data: Dict):
        """Update quote data in context"""
        context = self.get_context(user_id, channel)
        if "quote_data" not in context:
            context["quote_data"] = {}
        context["quote_data"].update(data)
        context["last_activity"] = datetime.now()

# Global context manager instance
context_manager = ContextManager()

def get_contextual_response(message: str, user_id: str, channel: str = "web") -> Tuple[str, str, float]:
    """
    Main function to get contextual response for GPS Control chatbot
    Returns: (response, intent, confidence)
    """
    try:
        return context_manager.generate_contextual_response(message, user_id, channel)
    except Exception as e:
        logger.error(f"Error generating contextual response: {e}")
        return (
            "Disculpa, tuve un problema procesando tu mensaje. ¿Podrías repetirlo?",
            "error",
            0.0
        )

def analyze_intent(message: str) -> Tuple[str, float]:
    """
    Analyze message intent
    Returns: (intent, confidence)
    """
    try:
        return context_manager.get_intent(message)
    except Exception as e:
        logger.error(f"Error analyzing intent: {e}")
        return ("general", 0.0)