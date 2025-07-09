#!/bin/bash

# Script para crear ambiente virtual e instalar dependencias para Face Landmarks Tracker
# Compatible con Linux, macOS y Windows (Git Bash)

echo "=== CONFIGURACIÓN DE AMBIENTE VIRTUAL PARA FACE LANDMARKS TRACKER ==="
echo ""

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python no está instalado o no está en el PATH"
    echo "Instala Python desde https://python.org/downloads/"
    exit 1
fi

# Determinar comando de Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo "✅ Python encontrado: $($PYTHON_CMD --version)"

# Verificar pip
if ! command -v $PIP_CMD &> /dev/null; then
    echo "❌ Error: pip no está instalado"
    echo "Instala pip siguiendo las instrucciones en https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

echo "✅ pip encontrado: $($PIP_CMD --version)"
echo ""

# Crear directorio del proyecto
PROJECT_DIR="face_landmarks_tracker"
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  El directorio $PROJECT_DIR ya existe."
    read -p "¿Deseas continuar? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Operación cancelada."
        exit 1
    fi
else
    mkdir "$PROJECT_DIR"
    echo "📁 Directorio creado: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Crear ambiente virtual
echo "🔨 Creando ambiente virtual..."
$PYTHON_CMD -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Error al crear el ambiente virtual"
    echo "Intenta instalar python3-venv: sudo apt-get install python3-venv (Ubuntu/Debian)"
    exit 1
fi

echo "✅ Ambiente virtual creado exitosamente"

# Activar ambiente virtual
echo "🔄 Activando ambiente virtual..."

# Detectar sistema operativo para activación
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
    ACTIVATE_CMD="venv\\Scripts\\activate.bat"
elif [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # macOS y Linux
    source venv/bin/activate
    ACTIVATE_CMD="source venv/bin/activate"
else
    echo "⚠️  Sistema operativo no detectado, intentando activación estándar..."
    source venv/bin/activate
    ACTIVATE_CMD="source venv/bin/activate"
fi

echo "✅ Ambiente virtual activado"
echo ""

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# Crear archivo requirements.txt
echo "📝 Creando archivo requirements.txt..."
cat > requirements.txt << EOF
# Dependencias para Face Landmarks Tracker
opencv-python==4.8.1.78
mediapipe==0.10.8
requests==2.31.0
numpy==1.24.3
Pillow==10.0.1

# Dependencias opcionales para desarrollo
matplotlib==3.7.2
jupyter==1.0.0
EOF

echo "✅ Archivo requirements.txt creado"

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
echo "Esto puede tomar varios minutos..."

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar algunas dependencias"
    echo "Intenta instalar manualmente:"
    echo "pip install opencv-python mediapipe requests numpy Pillow"
    exit 1
fi

echo "✅ Todas las dependencias instaladas correctamente"
echo ""

# Crear script de activación rápida
echo "🚀 Creando script de activación rápida..."

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    cat > activate_env.bat << EOF
@echo off
call venv\\Scripts\\activate.bat
echo.
echo ===== AMBIENTE VIRTUAL ACTIVADO =====
echo Para desactivar, escribe: deactivate
echo Para ejecutar el tracker: python face_landmarks_tracker.py
echo.
EOF
    echo "✅ Script de activación creado: activate_env.bat"
else
    # macOS y Linux
    cat > activate_env.sh << EOF
#!/bin/bash
source venv/bin/activate
echo ""
echo "===== AMBIENTE VIRTUAL ACTIVADO ====="
echo "Para desactivar, escribe: deactivate"
echo "Para ejecutar el tracker: python face_landmarks_tracker.py"
echo ""
EOF
    chmod +x activate_env.sh
    echo "✅ Script de activación creado: activate_env.sh"
fi

# Verificar instalación
echo "🧪 Verificando instalación..."
python -c "
import cv2
import mediapipe as mp
import numpy as np
import requests
from PIL import Image
print('✅ OpenCV version:', cv2.__version__)
print('✅ MediaPipe version:', mp.__version__)
print('✅ NumPy version:', np.__version__)
print('✅ Requests disponible')
print('✅ Pillow disponible')
print('✅ Todas las dependencias funcionan correctamente')
"

if [ $? -ne 0 ]; then
    echo "❌ Error en la verificación de dependencias"
    exit 1
fi

echo ""
echo "🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!"
echo ""
echo "📁 Directorio del proyecto: $(pwd)"
echo "🔧 Ambiente virtual: venv/"
echo "📄 Dependencias: requirements.txt"
echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo "1. Copia el archivo face_landmarks_tracker.py a este directorio"
echo "2. Para usar el ambiente virtual:"

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "   - Windows: ejecuta activate_env.bat"
else
    echo "   - Linux/macOS: ejecuta ./activate_env.sh"
fi

echo "3. Ejecuta: python face_landmarks_tracker.py"
echo ""
echo "📋 COMANDOS ÚTILES:"
echo "• Activar manualmente: $ACTIVATE_CMD"
echo "• Desactivar: deactivate"
echo "• Instalar nueva dependencia: pip install nombre_paquete"
echo "• Ver dependencias instaladas: pip list"
echo ""
echo "💡 TIPS:"
echo "• El ambiente virtual solo funciona cuando está activado"
echo "• Siempre activa el ambiente antes de ejecutar el script"
echo "• Puedes crear múltiples ambientes virtuales para diferentes proyectos"
echo ""