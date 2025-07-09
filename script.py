import cv2
import json
import os
import requests
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Dict, List, Tuple
import numpy as np


class VideoFaceLandmarksTracker:
    """
    Tracker que extrae landmarks faciales de un video usando MediaPipe
    y guarda las posiciones x,y en un archivo JSON.
    """
    
    # Configuración del modelo MediaPipe
    MODEL_URL = (
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
        "face_landmarker/float16/1/face_landmarker.task"
    )
    MODEL_DIR = os.path.expanduser("~/.mediapipe/models")
    MODEL_PATH = os.path.join(MODEL_DIR, "face_landmarker.task")
    
    def __init__(self):
        """
        Inicializa el tracker de landmarks faciales.
        """
        # Asegurar que el modelo esté descargado
        self._ensure_model_exists()
        
        # Inicializar MediaPipe FaceLandmarker
        base_options = python.BaseOptions(model_asset_path=self.MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,  # Rastrear solo una cara
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        
        # Almacenar resultados
        self.landmarks_data = {}
        
    def _ensure_model_exists(self):
        """Descarga el modelo si no existe localmente."""
        if not os.path.exists(self.MODEL_PATH):
            print(f"Descargando modelo MediaPipe a {self.MODEL_PATH}...")
            os.makedirs(self.MODEL_DIR, exist_ok=True)
            
            try:
                response = requests.get(self.MODEL_URL, stream=True)
                response.raise_for_status()
                
                with open(self.MODEL_PATH, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("Modelo descargado exitosamente.")
            except Exception as e:
                raise RuntimeError(
                    f"Error al descargar el modelo: {e}. "
                    f"Descárgalo manualmente desde {self.MODEL_URL} "
                    f"y colócalo en {self.MODEL_PATH}"
                )
    
    def _extract_landmarks_from_frame(self, frame: np.ndarray) -> Dict:
        """
        Extrae landmarks de un frame específico.
        
        Args:
            frame: Frame del video como numpy array
            
        Returns:
            Diccionario con landmarks numerados del 1 al 468
        """
        # Convertir frame a formato RGB para MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Crear imagen MediaPipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detectar landmarks
        detection_result = self.detector.detect(mp_image)
        
        if len(detection_result.face_landmarks) == 0:
            return {}
        
        # Obtener landmarks del primer rostro
        landmarks = detection_result.face_landmarks[0]
        
        # Convertir a coordenadas de imagen
        h, w = frame.shape[:2]
        landmarks_dict = {}
        
        # Crear diccionario con landmarks numerados del 1 al 468
        for i, landmark in enumerate(landmarks):
            x = landmark.x * w
            y = landmark.y * h
            landmarks_dict[str(i + 1)] = [x, y]
            
        return landmarks_dict
    
    def process_video(self, video_path: str, output_json: str = None) -> Dict:
        """
        Procesa un video completo y extrae landmarks de todos los frames.
        
        Args:
            video_path: Ruta al archivo de video
            output_json: Ruta donde guardar el JSON (opcional)
            
        Returns:
            Diccionario con landmarks por frame
        """
        # Verificar que el video existe
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"El video {video_path} no existe.")
        
        # Abrir video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video {video_path}")
        
        # Obtener información del video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Procesando video: {video_path}")
        print(f"Total frames: {total_frames}")
        print(f"FPS: {fps}")
        
        frame_count = 0
        self.landmarks_data = {}
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Extraer landmarks del frame actual
            landmarks = self._extract_landmarks_from_frame(frame)
            
            # Guardar landmarks en el diccionario
            frame_key = f"frame{frame_count}"
            self.landmarks_data[frame_key] = landmarks
            
            # Mostrar progreso
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progreso: {progress:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        print(f"Procesamiento completado. {frame_count} frames procesados.")
        
        # Guardar en JSON si se especifica
        if output_json:
            self.save_to_json(self.landmarks_data, output_json)
        
        return self.landmarks_data
    
    def save_to_json(self, data: Dict, output_path: str):
        """
        Guarda los datos de landmarks en un archivo JSON.
        
        Args:
            data: Diccionario con los datos a guardar
            output_path: Ruta donde guardar el archivo JSON
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Datos guardados en: {output_path}")
        except Exception as e:
            print(f"Error al guardar JSON: {e}")


def main():
    """
    Función principal para ejecutar el tracker.
    """
    # Configurar rutas - video fijo en ./video.mp4
    video_path = "./video.mp4"
    output_json = "video_landmarks.json"
    
    print(f"🎬 Procesando video: {video_path}")
    print(f"📄 Archivo de salida: {output_json}")
    print("-" * 50)
    
    try:
        # Verificar que el video existe antes de procesar
        if not os.path.exists(video_path):
            print(f"❌ Error: No se encontró el video en {video_path}")
            print("📁 Asegúrate de que el archivo 'video.mp4' esté en el directorio actual")
            return
        
        # Crear tracker
        print("🚀 Inicializando tracker...")
        tracker = VideoFaceLandmarksTracker()
        
        # Procesar video
        print("📊 Procesando video...")
        result = tracker.process_video(video_path, output_json)
        
        # Mostrar estadísticas básicas
        total_frames = len(result)
        frames_with_face = sum(1 for frame_data in result.values() if frame_data)
        
        print("\n" + "="*50)
        print("📈 ESTADÍSTICAS FINALES")
        print("="*50)
        print(f"📹 Total de frames: {total_frames}")
        print(f"👤 Frames con rostro detectado: {frames_with_face}")
        print(f"🎯 Tasa de detección: {frames_with_face/total_frames:.2%}")
        print("-" * 50)
        print(f"✅ Archivo JSON guardado en: {output_json}")
        print("🎉 ¡Procesamiento completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()