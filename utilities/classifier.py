"""
Classification and Intent Recognition System for GPS Control Chatbot
Simplified version of the original clasificador.py focused on essential functionality
"""
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata

logger = logging.getLogger(__name__)

# Video mapping for GPS Control content
VIDEOS_DICT = {
    "${v1}": "machin-v1-rastreo-satelital-c.mp4",
    "${v2}": "machin-v2-particulares-c.mp4", 
    "${v3}": "machin-v3-bienvenida-app-c.mp4",
    "${v4}": "machin-v4-industrias_c.mp4",
    "${v5}": "machin-v5-monitoreo_dedicado_c.mp4",
    "${v6}": "machin-v6-vvm_c.mp4",
    "${v7}": "machin-v7-diferenciadores_c.mp4",
    "${v8}": "machin-v8-accesorios_c.mp4",
    "${v9}": "machin-v9-ivan-on_c.mp4",
    "${v10}": "machin-v10-combustible_c.mp4",
    "${v11}": "machin-v11-mantenimientos_c.mp4",
    "${v12}": "machin-v12-adasydms_c.mp4",
    "${v13}": "machin-v13-cadena-de-frío_c.mp4",
    "${v14}": "machin-v14-beneficios_c.mp4",
    "${v15}": "machin-v15-gpscontrol_c.mp4",
    "${v16}": "machin-v16-visualizacion-de-camaras_c.mp4"
}

VIDEOS_INFO = {
    "${machin-v1-rastreo-satelital-c}": "Explicación básica del rastreo satelital.",
    "${machin-v2-particulares-c}": "Soluciones para particulares.",
    "${machin-v3-bienvenida-app-c}": "Introducción a la aplicación de GPScontrol.",
    "${machin-v4-industrias}": "Soluciones para Empresas Industrias.", 
    "${machin-v5-monitoreo_dedicado_c}": "Monitoreo dedicado para flotas.",
    "${machin-v6-vvm_c}": "Videovigilancia móvil (VVM).",
    "${machin-v7-diferenciadores_c}": "Diferenciadores de GPScontrol frente a la competencia.",
    "${machin-v8-accesorios_c}": "Accesorios disponibles para el sistema.",
    "${machin-v9-ivan-on_c}": "Ivan-On Asistente Virtual en Cabina.", 
    "${machin-v10-combustible_c}": "Control de combustible.",
    "${machin-v11-mantenimientos_c}": "Mantenimientos preventivos.",
    "${machin-v12-adasydms_c}": "Cámaras ADAS y DMS para seguridad avanzada.",
    "${machin-v13-cadena-de-frío_c}": "Soluciones para la cadena de frío.",
    "${machin-v14-beneficios_c}": "Beneficios clave de contratar servicios con GPScontrol.",
    "${machin-v15-gpscontrol_c}": "Presentación general de GPScontrol.",
    "${machin-v16-visualizacion-de-camaras_c}": "Ejemplos de Visualización de cámaras en tiempo real."
}

class GPSControlClassifier:
    """Classification system for GPS Control chatbot interactions"""
    
    def __init__(self):
        self.dataset = []
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=None,  # Keep Spanish stop words
            max_features=1000,
            ngram_range=(1, 2)
        )
        self.load_dataset()
        self._prepare_classifier()
    
    def load_dataset(self):
        """Load GPS Control dataset from JSON file"""
        try:
            dataset_path = Path(__file__).parent / "dataset_gpscontrol.json"
            if dataset_path.exists():
                with open(dataset_path, "r", encoding="utf-8") as f:
                    self.dataset = json.load(f)
                logger.info(f"Loaded {len(self.dataset)} entries from dataset")
            else:
                logger.warning("Dataset file not found, using empty dataset")
                self.dataset = []
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            self.dataset = []
    
    def _prepare_classifier(self):
        """Prepare TF-IDF vectors for similarity matching"""
        if not self.dataset:
            logger.warning("No dataset available for classification")
            return
        
        try:
            # Extract input texts for vectorization
            input_texts = [item.get("input", "") for item in self.dataset]
            
            # Fit vectorizer on input texts
            if input_texts:
                self.input_vectors = self.vectorizer.fit_transform(input_texts)
                logger.info("TF-IDF vectors prepared successfully")
        except Exception as e:
            logger.error(f"Error preparing classifier: {e}")
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Remove extra whitespace and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def find_best_match(self, user_input: str, threshold: float = 0.3) -> Optional[Dict]:
        """Find the best matching response from dataset"""
        if not self.dataset or not hasattr(self, 'input_vectors'):
            return None
        
        try:
            # Normalize and vectorize user input
            normalized_input = self.normalize_text(user_input)
            user_vector = self.vectorizer.transform([normalized_input])
            
            # Calculate similarities
            similarities = cosine_similarity(user_vector, self.input_vectors)[0]
            
            # Find best match above threshold
            best_idx = similarities.argmax()
            best_score = similarities[best_idx]
            
            if best_score >= threshold:
                match = self.dataset[best_idx].copy()
                match['similarity_score'] = float(best_score)
                return match
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding best match: {e}")
            return None
    
    def classify_intent(self, message: str) -> Tuple[str, str, float]:
        """
        Classify user message intent and return appropriate response
        Returns: (response, intent, confidence)
        """
        try:
            best_match = self.find_best_match(message)
            
            if best_match:
                # Get response and process video placeholders
                response = best_match.get("answer", "")
                response = self._process_video_placeholders(response)
                
                intent = best_match.get("intention", "general")
                confidence = best_match.get("similarity_score", 0.0)
                
                # Add suggested responses if available
                suggested = best_match.get("suggested_responses", [])
                if suggested:
                    response += "\n\n" + "Opciones disponibles:\n"
                    for i, suggestion in enumerate(suggested[:4], 1):
                        response += f"{i}. {suggestion}\n"
                
                return response, intent, confidence
            
            # Fallback response if no good match found
            return self._get_fallback_response(), "general", 0.0
            
        except Exception as e:
            logger.error(f"Error in classify_intent: {e}")
            return "Disculpa, tuve un problema. ¿Podrías repetir tu pregunta?", "error", 0.0
    
    def _process_video_placeholders(self, response: str) -> str:
        """Process video placeholders in responses"""
        # Replace ${video} with video information
        if "${video}" in response:
            response = response.replace("${video}", 
                "🎥 Te comparto un video explicativo sobre nuestros servicios.")
        
        # Replace specific video references
        for placeholder, video_file in VIDEOS_DICT.items():
            if placeholder in response:
                video_info = VIDEOS_INFO.get(placeholder.replace("${", "${machin-"), "Video informativo")
                response = response.replace(placeholder, f"🎥 {video_info}")
        
        return response
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when no good match is found"""
        return (
            "¡Hola! Soy Machín de GPS Control 🤖\n\n"
            "Te puedo ayudar con:\n"
            "📍 Cotizaciones de GPS satelital\n"
            "📹 Información sobre cámaras de seguridad\n"  
            "🔧 Proceso de instalación\n"
            "📞 Soporte técnico\n"
            "🏢 Soluciones empresariales\n\n"
            "¿Qué necesitas saber? 😊"
        )
    
    def get_classification_stats(self) -> Dict:
        """Get classification statistics"""
        if not self.dataset:
            return {"total_entries": 0, "classifications": {}}
        
        stats = {
            "total_entries": len(self.dataset),
            "classifications": {},
            "intentions": {}
        }
        
        for item in self.dataset:
            classification = item.get("clasification", "Unknown")
            intention = item.get("intention", "Unknown")
            
            stats["classifications"][classification] = stats["classifications"].get(classification, 0) + 1
            stats["intentions"][intention] = stats["intentions"].get(intention, 0) + 1
        
        return stats

# Global classifier instance
gps_classifier = GPSControlClassifier()

def classify_message(message: str) -> Tuple[str, str, float]:
    """
    Main function to classify user message and get appropriate response
    Returns: (response, intent, confidence)
    """
    try:
        return gps_classifier.classify_intent(message)
    except Exception as e:
        logger.error(f"Error in classify_message: {e}")
        return (
            "Disculpa, ocurrió un error procesando tu mensaje. ¿Podrías intentar de nuevo?",
            "error", 
            0.0
        )

def get_suggested_responses(intent: str) -> List[str]:
    """Get suggested responses for a given intent"""
    suggestions_map = {
        "cotizacion": [
            "Quiero cotizar GPS para mi auto",
            "Necesito información sobre cámaras", 
            "¿Cuánto cuesta el servicio?",
            "Soluciones para empresas"
        ],
        "informacion": [
            "¿Cómo funciona el GPS?",
            "Beneficios del servicio",
            "Proceso de instalación",
            "Contactar soporte técnico"
        ],
        "saludo": [
            "Ayúdame con una cotización",
            "Requiero información de servicios", 
            "Beneficios de GPS Control",
            "Contactar a Soporte Técnico"
        ]
    }
    
    return suggestions_map.get(intent, [
        "Cotizar GPS satelital",
        "Información sobre cámaras",
        "Proceso de instalación", 
        "Soporte técnico"
    ])