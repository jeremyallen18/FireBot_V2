"""
FireBot 2.0 AI - Asistente virtual inteligente
Optimizado para interacción natural, control de alarma y reportes
"""

from datetime import datetime
import random
from report_generator import FireBotReportGenerator


class FireBotAssistant:
    """Asistente conversacional inteligente y proactivo del sistema FireBot"""

    def __init__(self, detector, arduino_controller):
        self.detector = detector
        self.arduino = arduino_controller
        self.report_generator = FireBotReportGenerator()
        self.context = []
        self.last_fire_state = False
        self.notification_sent = False
        self.last_notification_time = None

    # --------------------- ALERTAS Y MONITOREO --------------------- #
    def check_fire(self):
        """Verifica el estado del fuego y decide si enviar alerta"""
        stats = self.detector.get_stats()
        fire_now = stats['fire_detected']

        # Cambio de estado: fuego detectado
        if fire_now and not self.last_fire_state:
            self.last_fire_state = True
            self.notification_sent = True
            if self.arduino.is_connected:
                self.arduino.send_alarm(True)
            return self._fire_alert(stats)

        # Cambio de estado: fuego despejado
        elif not fire_now and self.last_fire_state:
            self.last_fire_state = False
            self.notification_sent = False
            if self.arduino.is_connected:
                self.arduino.send_alarm(False)
            return self._fire_cleared(stats)

        return None

    def _fire_alert(self, stats):
        confidence = stats.get('current_confidence', 0)
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"🚨 ¡ALERTA DE FUEGO! 🚨\nConfianza: {confidence:.1f}%\nHora: {timestamp}\nRevisa la zona inmediatamente!"

    def _fire_cleared(self, stats):
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"✅ Fuego ya no detectado.\nHora: {timestamp}\nAlarma desactivada automáticamente."

    # --------------------- CHAT INTELIGENTE --------------------- #
    def get_response(self, message):
        """Genera respuesta basada en contexto y comando del usuario"""
        text = message.lower().strip()
        self.context.append(text)
        if len(self.context) > 10:
            self.context.pop(0)

        # Saludos
        if any(word in text for word in ["hola", "hi", "buenos", "buenas"]):
            return self._greeting()

        # Preguntas sobre fuego
        if any(word in text for word in ["fuego", "incendio", "llama", "alerta"]):
            stats = self.detector.get_stats()
            return self._fire_status(stats)

        # Alarmas
        if any(word in text for word in ["alarma", "buzzer", "sonido"]):
            return self._handle_alarm_command(text)

        # Reportes
        if any(word in text for word in ["reporte", "pdf", "informe"]):
            return self._handle_report_command(text)

        # Estado del sistema
        if any(word in text for word in ["estado", "status", "situación", "cómo va"]):
            return self._system_status()

        # Historial de detecciones
        if any(word in text for word in ["historial", "anteriores", "detecciones"]):
            return self._historical_report()

        # Capacidades del sistema
        if any(word in text for word in ["puedes hacer", "capacidades", "funciones"]):
            return self._capabilities()

        # Despedida
        if any(word in text for word in ["adiós", "chau", "bye", "nos vemos"]):
            return random.choice([
                "¡Hasta luego! 👋 Sigo vigilando.",
                "¡Nos vemos! 🔥 Sistema operativo 24/7.",
                "¡Hasta pronto! 😎 Aquí si me necesitas."
            ])

        # Agradecimiento
        if any(word in text for word in ["gracias", "thanks"]):
            return random.choice([
                "¡De nada! 🤝",
                "¡Un placer ayudar! 💪",
                "Siempre al servicio. 😊"
            ])

        # Respuesta por defecto inteligente
        return self._default_response(text)

    # --------------------- MÉTODOS PRIVADOS --------------------- #
    def _greeting(self):
        hour = datetime.now().hour
        greeting = "¡Buenos días!" if hour < 12 else "¡Buenas tardes!" if hour < 19 else "¡Buenas noches!"
        stats = self.detector.get_stats()
        alert_msg = " 🚨 ALERTA ACTIVA DE FUEGO!" if stats['fire_detected'] else ""
        return f"{greeting}{alert_msg} Sistema monitoreando 24/7."

    def _fire_status(self, stats):
        if stats['fire_detected']:
            return f"🔴 ¡FUEGO DETECTADO AHORA!\nConfianza: {stats.get('current_confidence',0):.1f}%\nTiempo continuo: {stats['continuous_time']:.1f}s"
        else:
            return "🟢 No hay fuego detectado actualmente. Todo bajo control."

    def _system_status(self):
        stats = self.detector.get_stats()
        fire_status = "🔴 Activo" if stats['fire_detected'] else "🟢 Sin fuego"
        arduino_status = "✅ Conectado" if self.arduino.is_connected else "❌ Desconectado"
        alarm_status = "🚨 Sonando" if getattr(self.arduino,'alarm_active',False) else "🔕 Silenciada"
        camera_status = "🟢 Activa" if getattr(self.detector,'running',False) else "🔴 Inactiva"
        return f"🔥 Fuego: {fire_status}\n📹 Cámara: {camera_status}\n🔌 Arduino: {arduino_status}\n🔔 Alarma: {alarm_status}"

    def _handle_alarm_command(self, text):
        if any(word in text for word in ["apaga", "silencia", "stop"]):
            if getattr(self.arduino,'alarm_active',False):
                self.arduino.send_alarm(False)
                self.arduino.alarm_active = False
                return "🔕 Alarma desactivada. Sistema sigue detectando."
            return "Alarma ya está apagada."
        if "prueba" in text:
            if self.arduino.is_connected:
                self.arduino.send_alarm(True)
                return "🔔 Probando buzzer..."
            return "❌ Arduino no conectado. No puedo probar buzzer."
        return f"Alarma: {'🚨 Activa' if getattr(self.arduino,'alarm_active',False) else '🔕 Inactiva'}"

    def _handle_report_command(self, text):
        if "semanal" in text:
            return self._generate_report('week')
        if "mensual" in text:
            return self._generate_report('month')
        return "📄 Para generar reportes, escribe 'reporte semanal' o 'reporte mensual'."

    def _generate_report(self, period):
        try:
            filename = self.report_generator.generate_report(period=period)
            detections = self.report_generator.filter_by_period(period)
            return f"✅ Reporte {period} generado: {filename}\nD:\ {len(detections)} detecciones incluidas."
        except Exception as e:
            return f"❌ Error generando reporte: {e}"

    def _historical_report(self):
        detections = self.report_generator.filter_by_period('week')
        if not detections:
            return "📜 No hay detecciones recientes. Todo tranquilo."
        last_5 = detections[-5:]
        msg = "📜 Últimas 5 detecciones:\n"
        for d in reversed(last_5):
            dt = datetime.fromisoformat(d['timestamp'])
            msg += f"• {dt.strftime('%d/%m %H:%M')} - Confianza: {d['confidence']:.1f}%\n"
        return msg

    def _capabilities(self):
        return """🤖 FireBot 2.0 - Capacidades:
• Detección de fuego en tiempo real
• Alarma automática con Arduino
• Generación de reportes PDF
• Estadísticas completas y gráficas
• Respuestas contextuales e inteligentes"""

    def _default_response(self, text):
        if len(text) < 3:
            return "🤔 No entendí. Escribe 'ayuda' para ver comandos."
        return "👀 Entendido. Sigo monitoreando. Escribe 'ayuda' para asistencia."
    
    def get_fire_alert_message(self, confidence):
        return (
            "🚨 **ALERTA DE INCENDIO** 🚨\n\n"
            f"Se detectó fuego con una confianza del {confidence:.1f}%.\n"
            "Activa protocolos de seguridad inmediatamente.\n\n"
            "FireBot sigue monitoreando en tiempo real 🔥👀"
        )

    def get_fire_cleared_message(self):
        return (
            "✅ **Zona segura nuevamente**\n\n"
            "El fuego ya no está presente.\n"
            "Continuamos monitoreando en tiempo real 👀🔥\n\n"
            "Todo bajo control 😌"
        )
