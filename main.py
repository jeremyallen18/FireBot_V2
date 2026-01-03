"""
Aplicación principal FireBot - Sistema de detección de incendios con IA
Versión mejorada con generación de reportes PDF
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time
import os

from config import COLORS, WINDOW_CONFIG
from arduino_controller import ArduinoController
from fire_detector import FireDetector
from chatbot import FireBotAssistant
from ui_components import VideoPanel, ChatBox, ModernButton


class FireBotApp:
    """Aplicación principal del sistema FireBot"""
    
    def __init__(self):
        # Ventana principal
        self.root = tk.Tk()
        self.root.title(WINDOW_CONFIG['title'])
        self.root.geometry(WINDOW_CONFIG['geometry'])
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Sistema de control
        self.running = True
        
        # Inicializar componentes
        self.arduino = ArduinoController()
        self.detector = FireDetector(
            on_fire_detected=self.on_fire_detected,
            on_fire_cleared=self.on_fire_cleared,
            on_alarm_should_trigger=self.on_alarm_should_trigger
        )
        self.chatbot = FireBotAssistant(self.detector, self.arduino)
        
        # Crear interfaz
        self.create_ui()
        
        # Mensaje de bienvenida
        welcome_msg = """🔥 **¡Bienvenido a FireBot!**

Sistema de detección de incendios con IA iniciado.
Monitoreando en tiempo real... 👀

💡 **Nuevas funciones:**
• Genera reportes PDF (semanales/mensuales)
• Escribe "ayuda" para ver todos los comandos
• Pregúntame lo que necesites en lenguaje natural

¡Todo listo para protegerte! 🛡️"""
        self.chat_box.add_message("system", welcome_msg)
        
        # Conectar Arduino
        arduino_connected = self.arduino.connect()
        if not arduino_connected:
            messagebox.showwarning(
                "Arduino",
                "No se pudo conectar con Arduino.\n\n"
                "El sistema funcionará sin alarma de buzzer.\n"
                "Verifica la conexión y reinicia la aplicación."
            )
            self.chat_box.add_message("system", 
                "⚠️ Arduino no conectado. Sistema funcionando sin alarma física.")
        else:
            self.chat_box.add_message("system", 
                "✅ Arduino conectado correctamente. Alarma lista.")
        
        # Iniciar cámara
        if not self.detector.start_camera():
            messagebox.showerror(
                "Error de Cámara",
                "No se pudo conectar con la cámara.\n\n"
                "Verifica la URL en config.py"
            )
            self.root.destroy()
            return
        
        self.chat_box.add_message("system", 
            "📹 Cámara conectada. Análisis de video iniciado.")
        
        # Iniciar threads
        threading.Thread(target=self.video_loop, daemon=True).start()
        threading.Thread(target=self.update_ui_loop, daemon=True).start()
        
        # Iniciar aplicación
        self.root.mainloop()
    
    def create_ui(self):
        """Crea la interfaz de usuario"""
        
        # ========== HEADER ==========
        header_frame = tk.Frame(self.root, bg=COLORS['bg_card'], height=90)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_container = tk.Frame(header_frame, bg=COLORS['bg_card'])
        title_container.pack(expand=True)
        
        # Icono
        tk.Label(
            title_container,
            text="🔥",
            bg=COLORS['bg_card'],
            font=("Arial", 36)
        ).pack(side='left', padx=(0, 15))
        
        # Título
        title_box = tk.Frame(title_container, bg=COLORS['bg_card'])
        title_box.pack(side='left')
        
        tk.Label(
            title_box,
            text="FireBot",
            fg=COLORS['accent_red'],
            bg=COLORS['bg_card'],
            font=("Arial", 32, "bold")
        ).pack(anchor='w')
        
        tk.Label(
            title_box,
            text="Sistema Inteligente de Detección de Incendios con IA",
            fg=COLORS['text_gray'],
            bg=COLORS['bg_card'],
            font=("Arial", 12)
        ).pack(anchor='w')
        
        # Botones de control
        controls = tk.Frame(title_container, bg=COLORS['bg_card'])
        controls.pack(side='right', padx=(30, 0))
        
        ModernButton(
            controls,
            text="🔔 Probar Buzzer",
            command=self.test_buzzer,
            bg=COLORS['warning']
        ).pack(side='left', padx=5)
        
        ModernButton(
            controls,
            text="🔕 Silenciar",
            command=self.silence_alarm,
            bg=COLORS['danger']
        ).pack(side='left', padx=5)
        
        ModernButton(
            controls,
            text="📄 Reportes",
            command=self.show_reports_menu,
            bg=COLORS['accent_blue']
        ).pack(side='left', padx=5)
        
        # ========== CONTENEDOR PRINCIPAL ==========
        main_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # ========== PANEL IZQUIERDO (Video) ==========
        self.video_panel = VideoPanel(main_container)
        self.video_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # ✅ Conectar botón de voltear cámara
        self.video_panel.flip_btn.config(command=self.flip_camera)
        
        # ========== PANEL DERECHO (Chat) ==========
        self.chat_box = ChatBox(main_container)
        self.chat_box.pack(side='right', fill='both', padx=(10, 0))
        
        # ✅ Configurar comandos del chat
        self.chat_box.send_btn.config(command=self.send_message)
        self.chat_box.entry.bind('<Return>', lambda e: self.send_message())
        
        # Actualizar estado inicial de Arduino
        self.video_panel.update_arduino(self.arduino.is_connected)
    
    def video_loop(self):
        """Loop principal de procesamiento de video"""
        while self.running:
            frame = self.detector.process_frame()
            if frame is not None:
                try:
                    self.video_panel.update_video(frame)
                except Exception as e:
                    print(f"Error actualizando video: {e}")
            
            time.sleep(0.03)  # ~30 FPS
    
    def update_ui_loop(self):
        """Loop de actualización de UI"""
        while self.running:
            stats = self.detector.get_stats()
            
            try:
                self.video_panel.update_status(stats['fire_detected'])
                self.video_panel.update_detections(stats['detection_count'])
                self.video_panel.update_continuous_time(stats['continuous_time'])
                self.video_panel.update_arduino_status(self.arduino.is_connected)
            except Exception as e:
                print(f"Error actualizando UI: {e}")
            
            time.sleep(0.1)
    
    def on_fire_detected(self, confidence, waiting_for_alarm=False):
        """Callback cuando se detecta fuego inicialmente"""
        alert_msg = f"🔥 Fuego detectado (confianza: {confidence:.1f}%)\n⏳ Verificando por 3 segundos..."
        self.chat_box.add_message("system", alert_msg)
    
    def on_alarm_should_trigger(self, confidence, duration, evidence_path):
        """Callback cuando la alarma debe activarse (después del delay)"""
        # Activar alarma física
        if self.arduino.is_connected:
            self.arduino.activate_alarm()
        
        # Guardar detección en historial
        detection_data = {
            'confidence': confidence * 100,  # Convertir a porcentaje
            'duration': duration,
            'alarm_triggered': self.arduino.alarm_active,
            'manual_silence': False
        }
        self.chatbot.report_generator.save_detection(
         detection_data=detection_data,
         camera_frame=self.detector.last_fire_frame
         )

        
        # Mostrar alerta
        alert_msg = self.chatbot.get_fire_alert_message(confidence)
        self.chat_box.add_message("system", alert_msg)
    
    def on_fire_cleared(self, was_alarm_triggered):
        """Callback cuando el fuego se despeja"""
        msg = self.chatbot.get_fire_cleared_message()
        self.chat_box.add_message("system", msg)
    
    def send_message(self):
        """Envía un mensaje al chatbot"""
        user_msg = self.chat_box.get_entry()
        if not user_msg:
            return
        
        # Mostrar mensaje del usuario
        self.chat_box.add_message("user", user_msg)
        self.chat_box.clear_entry()
        
        # Obtener respuesta del bot
        bot_response = self.chatbot.get_response(user_msg)
        self.chat_box.add_message("bot", bot_response)
    
    def test_buzzer(self):
        """Prueba el buzzer"""
        if self.arduino.is_connected:
            self.arduino.test_buzzer()
            self.chat_box.add_message("system", "🔔 Prueba de buzzer ejecutada")
        else:
            messagebox.showwarning(
                "Arduino no conectado",
                "No se puede probar el buzzer.\nArduino no está conectado."
            )
    
    def silence_alarm(self):
        """Silencia la alarma"""
        if self.arduino.alarm_active:
            # Guardar que fue silenciada manualmente
            if self.detector.fire_detected:
                detection_data = {
                    'confidence': self.detector.current_confidence * 100,
                    'duration': self.detector.continuous_detection_time,
                    'alarm_triggered': True,
                    'manual_silence': True
                }
                self.chatbot.report_generator.save_detection(detection_data)
            
            self.arduino.stop_alarm()
            self.chat_box.add_message("system", "🔕 Alarma silenciada manualmente")
        else:
            self.chat_box.add_message("system", "La alarma ya está apagada")
    
    def flip_camera(self):
        """Voltea la imagen de la cámara"""
        mode_name = self.detector.flip_camera()
        self.chat_box.add_message("system", f"🔄 Modo de cámara: {mode_name}")
    
    def show_reports_menu(self):
        """Muestra menú de reportes"""
        response = messagebox.askquestion(
            "Generar Reporte",
            "¿Qué tipo de reporte deseas generar?\n\n"
            "Sí = Reporte Semanal (últimos 7 días)\n"
            "No = Reporte Mensual (últimos 30 días)",
            icon='question'
        )
        
        if response == 'yes':
            self.generate_report('week')
        else:
            self.generate_report('month')
    
    def generate_report(self, period):
        """Genera un reporte PDF"""
        try:
            # Generar reporte
            period_text = "semanal" if period == 'week' else "mensual"
            self.chat_box.add_message("system", 
                f"📄 Generando reporte {period_text}... Por favor espera.")
            
            filename = self.chatbot.report_generator.generate_report(period=period)
            
            # Mostrar resultado
            detections = self.chatbot.report_generator.filter_by_period(period)
            
            msg = f"""✅ **Reporte {period_text.capitalize()} Generado**

📄 Archivo: {filename}
📊 Detecciones: {len(detections)}
📅 Período: {'Últimos 7 días' if period == 'week' else 'Últimos 30 días'}

El PDF incluye estadísticas, gráficas y análisis completo.
¿Deseas abrir el reporte ahora?"""
            
            self.chat_box.add_message("system", msg)
            
            # Preguntar si quiere abrir el archivo
            if messagebox.askyesno("Reporte Generado", 
                                   f"Reporte generado exitosamente:\n{filename}\n\n¿Deseas abrirlo ahora?"):
                os.startfile(filename)  # Windows
                # Para Linux/Mac usa: os.system(f'xdg-open "{filename}"')
                
        except Exception as e:
            error_msg = f"❌ Error al generar el reporte: {str(e)}\n\n"
            error_msg += "Verifica que las dependencias estén instaladas:\n"
            error_msg += "pip install reportlab matplotlib"
            
            self.chat_box.add_message("system", error_msg)
            messagebox.showerror("Error", error_msg)
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar FireBot?"):
            self.running = False
            
            # Mensaje de despedida
            self.chat_box.add_message("system", 
                "👋 Cerrando FireBot... ¡Hasta pronto!")
            
            # Detener sistemas
            if self.arduino.is_connected:
                self.arduino.disconnect()
            
            self.detector.stop_camera()
            
            # Cerrar ventana
            self.root.after(500, self.root.destroy)


# ============================
#     EJECUTAR APLICACIÓN
# ============================
if __name__ == "__main__":
    try:
        app = FireBotApp()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error", f"No se pudo iniciar FireBot:\n\n{e}")