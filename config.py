# config.py
"""
Configuración centralizada del sistema FireBot
"""

# ============================
#     MODELO Y CÁMARA
# ============================
MODEL_PATH = "best.pt"
CAM_URL = 0
CONFIDENCE_THRESHOLD = 0.6

# Volteo de cámara
FLIP_CAMERA = False   # True para voltear, False normal
FLIP_MODE = 1         # 0 = vertical, 1 = horizontal, -1 = ambos

# ============================
#     ARDUINO
# ============================
ARDUINO_PORT = "COM3"  # Cambia según tu puerto (COM3, COM4, /dev/ttyUSB0, etc.)
ARDUINO_BAUDRATE = 9600
ALARM_DURATION = 5  # segundos de duración de la alarma
ALARM_ACTIVATION_DELAY = 2  # segundos de detección continua antes de activar alarma

# ============================
#     COLORES MODERNOS
# ============================
COLORS = {
    'bg_dark': '#0a0e27',
    'bg_card': '#1a1f3a',
    'accent_red': '#ff4757',
    'accent_blue': '#4488ff', 
    'accent_orange': '#ff6348',
    'text_white': '#ffffff',
    'text_gray': '#a4b0be',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'input_bg': '#252b4a',
    'border': '#2d3561',
    'danger': '#e74c3c'
}

# ============================
#     INTERFAZ
# ============================
WINDOW_CONFIG = {
    'title': "FireBot - IA CONTRA INCENDIOS D.A.T.",
    'geometry': "1200x800",
    'video_max_width': 720
}

# ============================
#     MENSAJES
# ============================
WELCOME_MESSAGE = """🤖 FireBot: ¡Hola! Soy FireBot, tu asistente de detección de incendios.

Estoy monitoreando la cámara en tiempo real. Si detecto fuego por más de 3 
segundos continuos, te alertaré y activaré la alarma del buzzer.

Esto previene falsas alarmas por detecciones momentáneas. 🎯

Puedes preguntarme sobre:
- Estado del sistema
- Estadísticas de detección
- Información sobre incendios
- Control de alarma

¿En qué puedo ayudarte?
"""

# ============================
#     UBICACIÓN FÍSICA
# ============================
LOCATION_INFO = {
    "zona": "Salon de Ingenieria en sistemas",
    "edificio": "Edificio B",
    "camara_id": "CAM_01",
    "latitude": 19.432608,
    "longitude": -99.133209
}