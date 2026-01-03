"""
Detector de incendios con YOLO
Con soporte para cambiar entre cámaras USB
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time

class FireDetector:
    def __init__(self, on_fire_detected=None, on_fire_cleared=None, on_alarm_should_trigger=None):
        """
        Inicializa el detector de fuego
        """
        self.model = YOLO('best.pt')  # Tu modelo entrenado
        self.cap = None

        self.last_fire_frame = None

        
        # ✅ Índice de cámara actual
        self.camera_index = 0
        self.available_cameras = [0, 1, 2]  # Índices de cámaras USB disponibles
        
        # Callbacks
        self.on_fire_detected = on_fire_detected
        self.on_fire_cleared = on_fire_cleared
        self.on_alarm_should_trigger = on_alarm_should_trigger
        
        # Estado de detección
        self.fire_detected = False
        self.detection_count = 0
        self.continuous_detection_time = 0
        self.last_detection_time = None
        self.alarm_triggered = False
        self.current_confidence = 0
        
        # Para el delay de 3 segundos
        self.fire_start_time = None
        self.waiting_for_alarm = False
    
    def start_camera(self, camera_index=0):
        """Inicia la cámara"""
        try:
            self.camera_index = camera_index
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                # Si falla, intentar con otros índices comunes
                for idx in [1, 0, 2]:
                    self.cap = cv2.VideoCapture(idx)
                    if self.cap.isOpened():
                        self.camera_index = idx
                        print(f"✅ Cámara iniciada en índice {idx}")
                        return True
                return False
            
            print(f"✅ Cámara iniciada en índice {camera_index}")
            return True
            
        except Exception as e:
            print(f"❌ Error al iniciar cámara: {e}")
            return False
    
    def stop_camera(self):
        """Detiene la cámara"""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
    
    def flip_camera(self):
        """
        ✅ CAMBIA ENTRE CÁMARAS USB (0, 1, 2)
        """
        if not self.cap:
            return "No hay cámara activa"
        
        # Liberar cámara actual
        self.cap.release()
        
        # Buscar siguiente cámara disponible
        current_idx = self.available_cameras.index(self.camera_index) if self.camera_index in self.available_cameras else -1
        next_idx = (current_idx + 1) % len(self.available_cameras)
        new_camera = self.available_cameras[next_idx]
        
        # Intentar abrir nueva cámara
        self.cap = cv2.VideoCapture(new_camera)
        
        if self.cap.isOpened():
            self.camera_index = new_camera
            print(f"✅ Cambiado a cámara USB {new_camera}")
            return f"Cámara USB {new_camera}"
        else:
            # Si falla, volver a la anterior
            self.cap = cv2.VideoCapture(self.camera_index)
            print(f"⚠️ No se pudo cambiar a cámara {new_camera}, manteniendo cámara {self.camera_index}")
            return f"Cámara USB {self.camera_index} (no se pudo cambiar)"
    
    def process_frame(self):
        """
        Procesa un frame de la cámara y detecta fuego
        Retorna el frame procesado con anotaciones
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        
        # ✅ NO APLICAR VOLTEO - mantener imagen original
        
        # Realizar detección con YOLO
        results = self.model(frame, conf=0.5, verbose=False)
        
        # Analizar resultados
        fire_detected_now = False
        max_confidence = 0
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Obtener información de la detección
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Verificar si es fuego (clase 0 en tu modelo)
                if cls == 0 and self._passes_color_filter(frame, box):
                    fire_detected_now = True
                    max_confidence = max(max_confidence, conf)
                    
                    # Dibujar caja en el frame
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    color = (0, 0, 255)  # Rojo para fuego
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Etiqueta con confianza
                    label = f"FUEGO {conf*100:.1f}%"
                    cv2.putText(frame, label, (x1, y1-10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        if fire_detected_now:
            self.last_fire_frame = frame.copy()  # BGR, sin convertir

        # Actualizar estado de detección
        self._update_detection_state(fire_detected_now, max_confidence)
        
        # Añadir información al frame
        self._add_info_overlay(frame)
        
        # ✅ Convertir BGR a RGB para Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame_rgb
    
    def _update_detection_state(self, fire_detected_now, confidence):
        """Actualiza el estado de detección y maneja callbacks"""
        current_time = time.time()
        
        if fire_detected_now:
            self.current_confidence = confidence
            
            # Primera detección
            if not self.fire_detected:
                self.fire_detected = True
                self.fire_start_time = current_time
                self.waiting_for_alarm = True
                self.detection_count += 1
                
                if self.on_fire_detected:
                    self.on_fire_detected(confidence * 100, waiting_for_alarm=True)
            
            # Actualizar tiempo continuo
            if self.fire_start_time:
                self.continuous_detection_time = current_time - self.fire_start_time
                
                # Verificar si debe activarse la alarma (después de 3 segundos)
                if self.waiting_for_alarm and self.continuous_detection_time >= 3.0:
                    self.waiting_for_alarm = False
                    self.alarm_triggered = True
                    
                    if self.on_alarm_should_trigger:
                        self.on_alarm_should_trigger(
                            confidence * 100,
                            self.continuous_detection_time,
                            None  # evidence_path si lo necesitas
                        )
            
            self.last_detection_time = current_time
        
        else:
            # Fuego despejado
            if self.fire_detected:
                was_alarm = self.alarm_triggered
                
                self.fire_detected = False
                self.fire_start_time = None
                self.waiting_for_alarm = False
                self.alarm_triggered = False
                self.continuous_detection_time = 0
                self.current_confidence = 0
                
                if self.on_fire_cleared:
                    self.on_fire_cleared(was_alarm)
    
    def _add_info_overlay(self, frame):
        """Añade información en pantalla"""
        # Fondo semitransparente para el texto
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Información
        status = "🔥 FUEGO DETECTADO" if self.fire_detected else "✅ Normal"
        color = (0, 0, 255) if self.fire_detected else (0, 255, 0)
        
        cv2.putText(frame, status, (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        cv2.putText(frame, f"Detecciones: {self.detection_count}", (20, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if self.fire_detected:
            cv2.putText(frame, f"Tiempo: {self.continuous_detection_time:.1f}s", (20, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def get_stats(self):
        """Retorna estadísticas actuales"""
        return {
            'fire_detected': self.fire_detected,
            'detection_count': self.detection_count,
            'continuous_time': self.continuous_detection_time,
            'confidence': self.current_confidence * 100,
            'alarm_triggered': self.alarm_triggered
        }
    
    def _passes_color_filter(self, frame, box):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        roi = frame[y1:y2, x1:x2]

        if roi.size == 0:
            return False

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Rangos de fuego (no rojo puro)
        lower_fire1 = np.array([5, 100, 150])
        upper_fire1 = np.array([25, 255, 255])

        lower_fire2 = np.array([0, 50, 150])
        upper_fire2 = np.array([10, 255, 255])

        mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
        mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)

        fire_pixels = cv2.countNonZero(mask1 + mask2)
        total_pixels = roi.shape[0] * roi.shape[1]

        return (fire_pixels / total_pixels) > 0.15  # 15% fuego real
