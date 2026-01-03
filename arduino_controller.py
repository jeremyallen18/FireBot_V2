# arduino_controller.py
"""
Controlador para comunicación con Arduino y buzzer
"""

import serial
import threading
import time
from config import ARDUINO_PORT, ARDUINO_BAUDRATE, ALARM_DURATION


class ArduinoController:
    """Maneja la comunicación con Arduino para controlar el buzzer"""
    
    def __init__(self):
        self.serial_connection = None
        self.is_connected = False
        self.alarm_active = False
        self.alarm_thread = None
        
    def connect(self):
        """Conecta con el Arduino"""
        try:
            self.serial_connection = serial.Serial(
                ARDUINO_PORT, 
                ARDUINO_BAUDRATE, 
                timeout=1
            )
            time.sleep(2)  # Esperar a que Arduino se inicialice
            self.is_connected = True
            print(f"✅ Arduino conectado en {ARDUINO_PORT}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar con Arduino: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Desconecta el Arduino"""
        if self.serial_connection and self.is_connected:
            self.stop_alarm()
            self.serial_connection.close()
            self.is_connected = False
            print("🔌 Arduino desconectado")
    
    def send_command(self, command):
        """Envía un comando al Arduino"""
        if not self.is_connected:
            print("⚠️ Arduino no conectado")
            return False
        
        try:
            self.serial_connection.write(f"{command}\n".encode())
            return True
        except Exception as e:
            print(f"❌ Error al enviar comando: {e}")
            return False
    
    def activate_alarm(self):
        """Activa la alarma del buzzer"""
        if not self.alarm_active:
            self.alarm_active = True
            self.send_command("ALARM_ON")
            print("🚨 Alarma ACTIVADA")
            
            # Desactivar automáticamente después del tiempo configurado
            if self.alarm_thread and self.alarm_thread.is_alive():
                return
            
            self.alarm_thread = threading.Thread(
                target=self._auto_stop_alarm, 
                daemon=True
            )
            self.alarm_thread.start()
    
    def stop_alarm(self):
        """Detiene la alarma del buzzer"""
        if self.alarm_active:
            self.alarm_active = False
            self.send_command("ALARM_OFF")
            print("🔕 Alarma DESACTIVADA")
    
    def _auto_stop_alarm(self):
        """Detiene la alarma automáticamente después de ALARM_DURATION segundos"""
        time.sleep(ALARM_DURATION)
        self.stop_alarm()
    
    def test_buzzer(self):
        """Prueba el buzzer con un beep corto"""
        if self.is_connected:
            self.send_command("TEST")
            print("🔔 Prueba de buzzer")
            return True
        return False