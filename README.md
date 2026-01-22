# FireBot - Sistema de Detección de Incendios con IA

## Descripción General

FireBot es un sistema avanzado de detección y monitoreo de incendios que utiliza Inteligencia Artificial (IA) basada en el modelo YOLO (You Only Look Once) versión 2 para identificar fuegos en tiempo real a través de cámaras. El sistema integra múltiples componentes para proporcionar una solución completa de seguridad contra incendios, incluyendo detección automática, alertas sonoras, interfaz gráfica de usuario intuitiva, asistente conversacional inteligente y generación automática de reportes.

### Características Principales

- **Detección en Tiempo Real**: Utiliza IA YOLO para detectar incendios con alta precisión
- **Interfaz Gráfica Moderna**: Aplicación de escritorio con diseño intuitivo
- **Control de Alarmas**: Integración con Arduino para activación de buzzer
- **Asistente Conversacional**: Chatbot inteligente para interacción y control del sistema
- **Base de Datos**: Almacenamiento persistente de detecciones y estadísticas
- **Generación de Reportes**: Reportes automáticos en formato Word con gráficos y análisis
- **Soporte Multi-Cámara**: Capacidad para cambiar entre diferentes cámaras USB
- **Monitoreo Continuo**: Sistema de vigilancia 24/7 con alertas proactivas

## Arquitectura del Sistema

### Componentes Principales

#### 1. `main.py` - Aplicación Principal
- **Función**: Punto de entrada del sistema, maneja la interfaz gráfica principal
- **Tecnologías**: Tkinter para GUI, threading para operaciones concurrentes
- **Responsabilidades**:
  - Inicialización de todos los componentes del sistema
  - Gestión del ciclo de vida de la aplicación
  - Coordinación entre detector, Arduino y chatbot
  - Manejo de eventos de la interfaz de usuario

#### 2. `fire_detector.py` - Detector de Incendios
- **Función**: Implementa la lógica de detección usando IA YOLO
- **Tecnologías**: OpenCV, Ultralytics YOLO, NumPy
- **Características**:
  - Carga del modelo entrenado (`best.pt`)
  - Procesamiento de video en tiempo real
  - Soporte para múltiples cámaras USB (índices 0, 1, 2)
  - Sistema de confianza configurable (umbral por defecto: 0.6)
  - Callbacks para eventos de detección y limpieza
  - Temporización para activación de alarmas (delay de 3 segundos)

#### 3. `arduino_controller.py` - Controlador de Arduino
- **Función**: Maneja la comunicación serial con placa Arduino
- **Tecnologías**: PySerial para comunicación serial
- **Características**:
  - Conexión automática al puerto COM configurado
  - Control de buzzer para alertas sonoras
  - Temporización configurable de alarmas
  - Manejo de errores de conexión

#### 4. `chatbot.py` - Asistente Conversacional
- **Función**: Proporciona interfaz de chat inteligente
- **Características**:
  - Interacción natural con el usuario
  - Control remoto del sistema (activar/desactivar alarmas)
  - Generación de reportes por comando
  - Alertas proactivas sobre estado del sistema
  - Historial de conversaciones persistente

#### 5. `database.py` - Gestión de Base de Datos
- **Función**: Manejo de conexiones y operaciones con MySQL
- **Tecnologías**: PyMySQL
- **Características**:
  - Conexión segura a base de datos local
  - Creación automática de tablas
  - Operaciones CRUD para detecciones

#### 6. `report_generator.py` - Generador de Reportes
- **Función**: Crea reportes detallados de detecciones
- **Tecnologías**: python-docx, Matplotlib
- **Características**:
  - Reportes en formato Word (.docx)
  - Gráficos de detecciones por hora/día
  - Estadísticas detalladas
  - Información de ubicación GPS
  - Imágenes de detección guardadas

#### 7. `ui_components.py` - Componentes de Interfaz
- **Función**: Define componentes reutilizables de la GUI
- **Características**:
  - Botones modernos con efectos hover
  - Indicadores de estado visuales
  - Panel de video integrado
  - Caja de chat con scroll

#### 8. `config.py` - Configuración Centralizada
- **Función**: Almacena todas las configuraciones del sistema
- **Secciones**:
  - Configuración del modelo YOLO
  - Parámetros de Arduino
  - Colores y temas de la interfaz
  - Configuración de ventana

### Estructura de Archivos

```
IA YOLO V2/
├── main.py                 # Aplicación principal
├── fire_detector.py        # Detector de incendios con YOLO
├── arduino_controller.py   # Controlador de Arduino
├── chatbot.py              # Asistente conversacional
├── database.py             # Gestión de base de datos
├── report_generator.py     # Generador de reportes
├── ui_components.py        # Componentes de interfaz
├── config.py               # Configuraciones
├── best.pt                 # Modelo YOLO entrenado
├── firebot_history.json    # Historial del chatbot
├── main.spec               # Especificación PyInstaller
├── README.md               # Este archivo
├── Arduino/                # Código para Arduino
│   └── sketch_dec9a/
│       └── sketch_dec9a.ino
├── build/                  # Archivos de compilación
├── detecciones/            # Carpeta para imágenes guardadas
└── __pycache__/            # Cache de Python
```

## Base de Datos

### Descripción General
El sistema utiliza MySQL como base de datos principal para almacenar todas las detecciones de incendios, estadísticas y metadatos asociados. La base de datos se llama `firebot_db` y contiene una tabla principal llamada `detections`.

### Script de Creación de Base de Datos

```sql
-- ===============================
-- CREAR BASE DE DATOS
-- ===============================
CREATE DATABASE IF NOT EXISTS firebot_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

-- ===============================
-- CREAR USUARIO
-- ===============================
CREATE USER IF NOT EXISTS 'firebot_user'@'localhost'
IDENTIFIED BY '12345678';

-- ===============================
-- PERMISOS
-- ===============================
GRANT ALL PRIVILEGES ON firebot_db.* 
TO 'firebot_user'@'localhost';

FLUSH PRIVILEGES;

-- ===============================
-- USAR BASE DE DATOS
-- ===============================
USE firebot_db;

-- ===============================
-- TABLA DE DETECCIONES
-- ===============================
CREATE TABLE IF NOT EXISTS detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    confidence FLOAT NOT NULL,
    duration FLOAT DEFAULT 0,
    alarm_triggered BOOLEAN DEFAULT FALSE,
    manual_silence BOOLEAN DEFAULT FALSE,
    image_path VARCHAR(255),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    location_name VARCHAR(100),

    INDEX idx_timestamp (timestamp)
);
```

### Explicación de la Tabla `detections`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INT AUTO_INCREMENT PRIMARY KEY | Identificador único de cada detección |
| `timestamp` | DATETIME NOT NULL | Fecha y hora exacta de la detección |
| `confidence` | FLOAT NOT NULL | Nivel de confianza de la detección (0.0 - 1.0) |
| `duration` | FLOAT DEFAULT 0 | Duración de la detección en segundos |
| `alarm_triggered` | BOOLEAN DEFAULT FALSE | Indica si se activó la alarma para esta detección |
| `manual_silence` | BOOLEAN DEFAULT FALSE | Indica si la alarma fue silenciada manualmente |
| `image_path` | VARCHAR(255) | Ruta al archivo de imagen guardado de la detección |
| `latitude` | DECIMAL(9,6) | Coordenada GPS de latitud |
| `longitude` | DECIMAL(9,6) | Coordenada GPS de longitud |
| `location_name` | VARCHAR(100) | Nombre descriptivo de la ubicación |

### Índices
- `idx_timestamp`: Índice en el campo `timestamp` para optimizar consultas por fecha

### Configuración de Conexión
La conexión a la base de datos se configura en `database.py` con los siguientes parámetros:
- **Host**: localhost
- **Usuario**: firebot_user
- **Contraseña**: FireBot_2024! (Nota: diferente a la del script SQL)
- **Base de datos**: firebot_db
- **Puerto**: 3307

## Requisitos del Sistema

### Hardware
- Cámara USB compatible con OpenCV
- Placa Arduino (opcional, para control de buzzer)
- Computadora con puerto USB

### Software
- Python 3.8+
- MySQL Server 8.0+
- Arduino IDE (para programar la placa)

### Dependencias Python
```
ultralytics
opencv-python
pymysql
tkinter (incluido en Python estándar)
Pillow
python-docx
matplotlib
pyserial
```

## Instalación y Configuración

### 1. Instalación de Dependencias
```bash
pip install ultralytics opencv-python pymysql Pillow python-docx matplotlib pyserial
```

### 2. Configuración de Base de Datos
1. Instalar MySQL Server
2. Ejecutar el script SQL proporcionado arriba
3. Verificar la conexión en `database.py`

### 3. Configuración de Arduino (Opcional)
1. Conectar Arduino al puerto COM3 (o modificar en `config.py`)
2. Subir el código `Arduino/sketch_dec9a/sketch_dec9a.ino`
3. Verificar conexión serial

### 4. Configuración del Modelo YOLO
- Colocar el archivo `best.pt` en el directorio raíz
- Ajustar umbral de confianza en `config.py` si es necesario

## Uso del Sistema

### Inicio de la Aplicación
```bash
python main.py
```

### Interfaz de Usuario
1. **Panel de Video**: Muestra el feed de la cámara con detecciones en tiempo real
2. **Chatbot**: Área de conversación con el asistente inteligente
3. **Controles**: Botones para cambiar cámara, generar reportes, etc.
4. **Indicadores**: Estado del sistema, alarmas y detecciones

### Comandos del Chatbot
- "generar reporte": Crea un reporte de detecciones
- "activar alarma": Activa la alarma manualmente
- "silenciar": Desactiva la alarma
- "estado": Muestra estado actual del sistema

## Funcionamiento del Sistema

### Proceso de Detección
1. **Captura de Video**: La cámara captura frames continuamente
2. **Procesamiento IA**: YOLO analiza cada frame buscando patrones de fuego
3. **Validación**: Si la confianza supera el umbral, se confirma detección
4. **Activación de Alarma**: Después de 3 segundos de detección continua, se activa el buzzer
5. **Registro**: La detección se guarda en base de datos con timestamp y metadatos
6. **Notificación**: El chatbot informa al usuario sobre el evento

### Sistema de Alarmas
- **Activación Automática**: Se activa tras detección continua por tiempo configurable
- **Control Manual**: Puede activarse/desactivarse vía chatbot o interfaz
- **Duración Configurable**: Tiempo de sonido del buzzer ajustable

### Generación de Reportes
Los reportes incluyen:
- Estadísticas de detecciones por período
- Gráficos de tendencias
- Información GPS de ubicación
- Imágenes de detecciones guardadas
- Análisis de confianza y duración

## Desarrollo y Contribución

### Estructura del Código
- **Modularidad**: Cada componente tiene su propio archivo
- **Configuración Centralizada**: Todas las constantes en `config.py`
- **Callbacks**: Comunicación entre componentes vía funciones callback
- **Threading**: Operaciones concurrentes para UI responsiva

### Extensiones Futuras
- Soporte para múltiples cámaras IP
- Integración con servicios de notificación (email, SMS)
- Dashboard web para monitoreo remoto
- Análisis predictivo de riesgos
- Integración con sistemas de extinción automática