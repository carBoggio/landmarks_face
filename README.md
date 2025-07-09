# 🎬 Face Landmarks Tracker

Tracker de landmarks faciales usando MediaPipe que procesa videos y extrae todas las posiciones de landmarks de cada frame, guardándolas en formato JSON.

## 🎯 Características

- ✅ Extrae 468 landmarks faciales por frame
- ✅ Procesa videos completos automáticamente
- ✅ Guarda resultados en formato JSON estructurado
- ✅ Descarga automática del modelo MediaPipe
- ✅ Estadísticas detalladas del procesamiento
- ✅ Compatible con Windows, macOS y Linux

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- 2GB de espacio libre (para el modelo y dependencias)

## 🚀 Instalación y Configuración

### Paso 1: Crear Ambiente Virtual

**Windows (Command Prompt):**
```cmd
python -m venv venv
```

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**Linux/macOS:**
```bash
python3 -m venv venv
```

### Paso 2: Activar Ambiente Virtual

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.8
pip install requests==2.31.0
pip install numpy==1.24.3
pip install Pillow==10.0.1
```

**O usar requirements.txt (si está disponible):**
```bash
pip install -r requirements.txt
```

### Paso 4: Verificar Instalación

```bash
python -c "import cv2, mediapipe, numpy, requests; print('✅ Todas las dependencias instaladas correctamente')"
```

## 📁 Estructura del Proyecto

```
face_landmarks_tracker/
├── venv/                        # Ambiente virtual
├── face_landmarks_tracker.py    # Script principal
├── video.mp4                    # Tu video (colócalo aquí)
├── requirements.txt             # Dependencias (opcional)
└── video_landmarks.json         # Resultado (se genera automáticamente)
```

## 🎬 Uso

### 1. Preparar Video
Coloca tu video en el directorio del proyecto con el nombre `video.mp4`:
```bash
# Ejemplo: copiar video desde otra ubicación
cp /ruta/a/tu/video.mp4 ./video.mp4
```

### 2. Ejecutar el Tracker
```bash
python face_landmarks_tracker.py
```

### 3. Resultado
El script generará automáticamente `video_landmarks.json` con todos los landmarks.

## 📊 Formato del JSON de Salida

```json
{
  "metadata": {
    "video_path": "./video.mp4",
    "total_frames": 300,
    "fps": 30.0,
    "duration_seconds": 10.0,
    "frames_with_face": 295
  },
  "frames": {
    "frame_000001": {
      "frame_number": 1,
      "timestamp": 0.033,
      "landmarks": [[x1, y1], [x2, y2], ...],
      "num_landmarks": 468
    },
    "frame_000002": {
      "frame_number": 2,
      "timestamp": 0.066,
      "landmarks": [[x1, y1], [x2, y2], ...],
      "num_landmarks": 468
    }
  }
}
```

## 🖥️ Comandos Completos por Sistema Operativo

### Windows (Command Prompt)
```cmd
# 1. Crear ambiente virtual
python -m venv venv

# 2. Activar ambiente virtual
venv\Scripts\activate.bat

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ejecutar tracker
python face_landmarks_tracker.py

# 5. Desactivar cuando termines
deactivate
```

### Windows (PowerShell)
```powershell
# 1. Crear ambiente virtual
python -m venv venv

# 2. Activar ambiente virtual
venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ejecutar tracker
python face_landmarks_tracker.py

# 5. Desactivar cuando termines
deactivate
```

### Linux/macOS
```bash
# 1. Crear ambiente virtual
python3 -m venv venv

# 2. Activar ambiente virtual
source venv/bin/activate

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ejecutar tracker
python face_landmarks_tracker.py

# 5. Desactivar cuando termines
deactivate
```

## 🔧 Solución de Problemas

### Error: "Python no encontrado"
```bash
# Verificar instalación de Python
python --version
# o
python3 --version
```

### Error: "No module named 'cv2'"
```bash
# Asegúrate de que el ambiente virtual esté activado
# Verifica que aparezca (venv) en tu prompt
# Reinstala opencv-python
pip install opencv-python
```

### Error: "No se encontró el video"
```bash
# Verificar que el video existe
ls video.mp4        # Linux/macOS
dir video.mp4       # Windows

# El video debe llamarse exactamente 'video.mp4'
```

### Error de permisos en Windows PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Reinstalar dependencias
```bash
# Si algo falla, reinstala todo
pip uninstall opencv-python mediapipe requests numpy Pillow
pip install opencv-python mediapipe requests numpy Pillow
```

## 📈 Estadísticas de Ejemplo

Al finalizar el procesamiento verás algo como:
```
==================================================
📈 ESTADÍSTICAS FINALES
==================================================
📹 Total de frames: 300
👤 Frames con rostro detectado: 295
🎯 Tasa de detección: 98.33%
📍 Promedio de landmarks por frame: 467.2
⏱️  Duración del video: 10.00 segundos
🎬 FPS del video: 30.00
--------------------------------------------------
✅ Archivo JSON guardado en: video_landmarks.json
🎉 ¡Procesamiento completado exitosamente!
```

## 🎯 Uso Avanzado

### Procesar múltiples videos
Para procesar varios videos, simplemente renómbralos a `video.mp4` uno por uno o modifica el script.

### Acceder a landmarks específicos
```python
import json

# Cargar datos
with open('video_landmarks.json', 'r') as f:
    data = json.load(f)

# Obtener landmarks del frame 1
frame_1_landmarks = data['frames']['frame_000001']['landmarks']

# Obtener landmark específico (ej: punta de nariz = índice 1)
nose_tip = frame_1_landmarks[1]  # [x, y]
```

## 🤝 Contribuciones

¿Encontraste un bug o tienes una mejora? ¡Las contribuciones son bienvenidas!

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**¿Necesitas ayuda?** Revisa la sección de solución de problemas o abre un issue en el repositorio.