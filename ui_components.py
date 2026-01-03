"""
Componentes de interfaz gráfica mejorados
"""

import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
from datetime import datetime
import config
from config import COLORS, WELCOME_MESSAGE


# =========================
# BOTÓN MODERNO
# =========================
class ModernButton(tk.Button):

    def __init__(self, parent, text, command, **kwargs):
        default_config = {
            "bg": COLORS["accent_red"],
            "fg": COLORS["text_white"],
            "font": ("Arial", 10, "bold"),
            "borderwidth": 0,
            "cursor": "hand2",
            "padx": 18,
            "pady": 8,
            "activebackground": COLORS["accent_orange"],
            "activeforeground": COLORS["text_white"]
        }
        default_config.update(kwargs)

        super().__init__(parent, text=text, command=command, **default_config)

        self.original_bg = default_config["bg"]
        self.bind("<Enter>", self._hover_on)
        self.bind("<Leave>", self._hover_off)

    def _hover_on(self, event):
        self.config(bg=COLORS["accent_orange"])

    def _hover_off(self, event):
        self.config(bg=self.original_bg)


# =========================
# INDICADOR DE ESTADO
# =========================
class StatusIndicator(tk.Frame):

    def __init__(self, parent, text):
        super().__init__(parent, bg=COLORS["bg_card"])

        self.dot = tk.Label(
            self,
            text="●",
            fg=COLORS["success"],
            bg=COLORS["bg_card"],
            font=("Arial", 20)
        )
        self.dot.pack(side="left")

        self.label = tk.Label(
            self,
            text=text,
            fg=COLORS["text_white"],
            bg=COLORS["bg_card"],
            font=("Arial", 12, "bold")
        )
        self.label.pack(side="left", padx=6)

    def set_status(self, active, text):
        self.dot.config(
            fg=COLORS["success"] if active else COLORS["accent_red"]
        )
        self.label.config(text=text)


# =========================
# TARJETA DE ESTADÍSTICA
# =========================
class StatCard(tk.Frame):

    def __init__(self, parent, icon, title, value="0"):
        super().__init__(parent, bg=COLORS["bg_card"])

        tk.Label(self, text=icon, bg=COLORS["bg_card"],
                 font=("Arial", 22)).pack()

        tk.Label(self, text=title, bg=COLORS["bg_card"],
                 fg=COLORS["text_gray"],
                 font=("Arial", 9)).pack()

        self.value = tk.Label(
            self,
            text=value,
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=("Arial", 16, "bold")
        )
        self.value.pack()

    def update_value(self, value):
        self.value.config(text=str(value))


# =========================
# CHAT
# =========================
class ChatBox(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_dark"])

        header = tk.Frame(self, bg=COLORS["bg_card"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="💬 Asistente FireBot",
            fg=COLORS["text_white"],
            bg=COLORS["bg_card"],
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=15, pady=12)

        # Área de chat con scroll
        self.chat = scrolledtext.ScrolledText(
            self,
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=("Consolas", 10),
            borderwidth=0,
            wrap="word",
            state="normal"  # ✅ Asegurar que esté habilitado
        )
        self.chat.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame de entrada
        input_frame = tk.Frame(self, bg=COLORS["bg_card"])
        input_frame.pack(fill="x", padx=10, pady=10)

        # Campo de entrada de texto
        self.entry = tk.Entry(
            input_frame,
            bg=COLORS["input_bg"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["text_white"],
            borderwidth=0,
            font=("Arial", 11),
            state="normal"  # ✅ Habilitado por defecto
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

        # Botón de enviar
        self.send_btn = ModernButton(
            input_frame,
            text="Enviar ➤",
            command=None  # Se configurará desde main.py
        )
        self.send_btn.pack(side="right")

    def add_message(self, sender, message):
        """Añade un mensaje al chat"""
        time = datetime.now().strftime("%H:%M:%S")

        if sender == "user":
            prefix = f"[{time}] 🧑 Tú:\n"
        elif sender == "bot":
            prefix = f"[{time}] 🤖 FireBot:\n"
        else:
            prefix = ""

        # Habilitar temporalmente para escribir
        self.chat.config(state="normal")
        self.chat.insert("end", prefix + message + "\n\n")
        self.chat.see("end")
        self.chat.config(state="disabled")  # Deshabilitar edición manual

    def get_entry(self):
        """Obtiene el texto del campo de entrada"""
        return self.entry.get().strip()

    def clear_entry(self):
        """Limpia el campo de entrada"""
        self.entry.delete(0, tk.END)


# =========================
# PANEL DE VIDEO
# =========================
class VideoPanel(tk.Frame):
    """Panel de video que ahora hereda correctamente de tk.Frame"""
    
    def __init__(self, parent):
        # ✅ HEREDAR DE tk.Frame
        super().__init__(parent, bg=COLORS["bg_dark"])

        # Header con botón de voltear cámara
        video_header = tk.Frame(self, bg=COLORS["bg_card"], height=50)
        video_header.pack(fill="x", pady=(0, 10))
        video_header.pack_propagate(False)

        tk.Label(
            video_header,
            text="📹 Video en Tiempo Real",
            fg=COLORS["text_white"],
            bg=COLORS["bg_card"],
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=15, pady=12)

        # Botón de cambiar cámara
        self.flip_btn = ModernButton(
            video_header,
            text="📹 Cambiar Cámara",
            command=None,  # Se configurará desde main.py
            bg=COLORS["accent_blue"]
        )
        self.flip_btn.pack(side="right", padx=15)

        # Canvas de video
        self.canvas = tk.Canvas(
            self, 
            bg="black", 
            highlightthickness=0,
            width=640, 
            height=480
        )
        self.canvas.pack(pady=10)

        # Tarjetas de estado
        self.cards_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        self.cards_frame.pack(pady=10)

        self.status_card = StatCard(self.cards_frame, "⚡", "Estado", "Normal")
        self.status_card.grid(row=0, column=0, padx=10)

        self.detect_card = StatCard(self.cards_frame, "👁️", "Detectados", "0")
        self.detect_card.grid(row=0, column=1, padx=10)

        self.time_card = StatCard(self.cards_frame, "⏱️", "Tiempo", "0.0s")
        self.time_card.grid(row=0, column=2, padx=10)

        # Indicador de Arduino
        self.arduino_indicator = StatusIndicator(self.cards_frame, "Arduino: Conectando...")
        self.arduino_indicator.grid(row=1, column=0, columnspan=3, pady=10)

    # ----------------------------
    # ACTUALIZAR VIDEO
    # ----------------------------
    def update_video(self, frame):
        """Actualiza el frame de video en el canvas"""
        try:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        except Exception as e:
            print(f"Error actualizando imagen: {e}")

    # ----------------------------
    # ACTUALIZAR ESTADO
    # ----------------------------
    def update_status(self, fire_detected):
        """Actualiza el estado del sistema"""
        try:
            if fire_detected:
                self.status_card.update_value("🔥 FUEGO")
                self.status_card.value.config(fg=COLORS["accent_red"])
            else:
                self.status_card.update_value("✅ Normal")
                self.status_card.value.config(fg=COLORS["success"])
        except Exception as e:
            print(f"Error actualizando estado: {e}")

    # ----------------------------
    # ACTUALIZAR DETECCIONES
    # ----------------------------
    def update_detections(self, count):
        """Actualiza el contador de detecciones"""
        try:
            self.detect_card.update_value(str(count))
        except Exception as e:
            print(f"Error actualizando detecciones: {e}")

    # ----------------------------
    # ACTUALIZAR TIEMPO CONTINUO
    # ----------------------------
    def update_continuous_time(self, time_seconds):
        """Actualiza el tiempo de detección continua"""
        try:
            from config import ALARM_ACTIVATION_DELAY
            
            self.time_card.update_value(f"{time_seconds:.1f}s")

            # Cambiar color según el riesgo
            if time_seconds >= ALARM_ACTIVATION_DELAY:
                self.time_card.value.config(fg=COLORS["accent_red"])
            elif time_seconds >= ALARM_ACTIVATION_DELAY * 0.6:
                self.time_card.value.config(fg=COLORS["warning"])
            else:
                self.time_card.value.config(fg=COLORS["text_white"])

        except Exception as e:
            print(f"Error actualizando continuous_time: {e}")

    # ----------------------------
    # ACTUALIZAR ESTADO DE ARDUINO
    # ----------------------------
    def update_arduino(self, is_connected):
        """Actualiza el indicador de estado de Arduino"""
        try:
            if is_connected:
                self.arduino_indicator.set_status(True, "Arduino: ✅ Conectado")
            else:
                self.arduino_indicator.set_status(False, "Arduino: ❌ Desconectado")
        except Exception as e:
            print(f"Error actualizando Arduino: {e}")

    def update_arduino_status(self, is_connected):
        """Alias para compatibilidad con main.py"""
        self.update_arduino(is_connected)