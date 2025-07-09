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
    
    def _extract_landmarks_from_frame(self, frame: np.ndarray) -> List[Tuple[float, float]]:
        """
        Extrae landmarks de un frame específico.
        
        Args:
            frame: Frame del video como numpy array
            
        Returns:
            Lista de tuplas (x, y) con las posiciones de landmarks
        """
        # Convertir frame a formato RGB para MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Crear imagen MediaPipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detectar landmarks
        detection_result = self.detector.detect(mp_image)
        
        if len(detection_result.face_landmarks) == 0:
            return []
        
        # Obtener landmarks del primer rostro
        landmarks = detection_result.face_landmarks[0]
        
        # Convertir a coordenadas de imagen
        h, w = frame.shape[:2]
        landmark_points = []
        
        for landmark in landmarks:
            x = landmark.x * w
            y = landmark.y * h
            landmark_points.append((x, y))
            
        return landmark_points
    
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
            frame_key = f"frame_{frame_count:06d}"
            
            if landmarks:
                self.landmarks_data[frame_key] = {
                    "frame_number": frame_count,
                    "timestamp": frame_count / fps,
                    "landmarks": landmarks,
                    "num_landmarks": len(landmarks)
                }
            else:
                self.landmarks_data[frame_key] = {
                    "frame_number": frame_count,
                    "timestamp": frame_count / fps,
                    "landmarks": [],
                    "num_landmarks": 0
                }
            
            # Mostrar progreso
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progreso: {progress:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        
        print(f"Procesamiento completado. {frame_count} frames procesados.")
        
        # Agregar metadata
        metadata = {
            "video_path": video_path,
            "total_frames": frame_count,
            "fps": fps,
            "duration_seconds": frame_count / fps,
            "frames_with_face": sum(1 for data in self.landmarks_data.values() if data["num_landmarks"] > 0)
        }
        
        result = {
            "metadata": metadata,
            "frames": self.landmarks_data
        }
        
        # Guardar en JSON si se especifica
        if output_json:
            self.save_to_json(result, output_json)
        
        return result
    
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
    
    def load_from_json(self, json_path: str) -> Dict:
        """
        Carga datos de landmarks desde un archivo JSON.
        
        Args:
            json_path: Ruta al archivo JSON
            
        Returns:
            Diccionario con los datos cargados
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar JSON: {e}")
            return {}
    
    def get_frame_landmarks(self, frame_number: int) -> List[Tuple[float, float]]:
        """
        Obtiene landmarks de un frame específico.
        
        Args:
            frame_number: Número del frame
            
        Returns:
            Lista de landmarks del frame
        """
        frame_key = f"frame_{frame_number:06d}"
        if frame_key in self.landmarks_data:
            return self.landmarks_data[frame_key]["landmarks"]
        return []
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del procesamiento.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.landmarks_data:
            return {}
        
        frames_with_face = sum(1 for data in self.landmarks_data.values() if data["num_landmarks"] > 0)
        total_frames = len(self.landmarks_data)
        
        return {
            "total_frames": total_frames,
            "frames_with_face": frames_with_face,
            "detection_rate": frames_with_face / total_frames if total_frames > 0 else 0,
            "average_landmarks_per_frame": sum(data["num_landmarks"] for data in self.landmarks_data.values()) / total_frames if total_frames > 0 else 0
        }


def main():
    """
    Función principal para ejecutar el tracker.
    """
    # Configurar rutas - video fijo en ./video.mp4
    video_path = "./video.mp4"
    output_json = "video_landmarks.json"  # Nombre fijo para el output
    
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
        
        # Mostrar estadísticas
        stats = tracker.get_statistics()
        print("\n" + "="*50)
        print("📈 ESTADÍSTICAS FINALES")
        print("="*50)
        print(f"📹 Total de frames: {stats['total_frames']}")
        print(f"👤 Frames con rostro detectado: {stats['frames_with_face']}")
        print(f"🎯 Tasa de detección: {stats['detection_rate']:.2%}")
        print(f"📍 Promedio de landmarks por frame: {stats['average_landmarks_per_frame']:.1f}")
        print(f"⏱️  Duración del video: {result['metadata']['duration_seconds']:.2f} segundos")
        print(f"🎬 FPS del video: {result['metadata']['fps']:.2f}")
        print("-" * 50)
        print(f"✅ Archivo JSON guardado en: {output_json}")
        print("🎉 ¡Procesamiento completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Verifica que:")
        print("   - El archivo 'video.mp4' existe en el directorio actual")
        print("   - El archivo no está corrupto")
        print("   - Tienes permisos de lectura en el archivo")


if __name__ == "__main__":
    main()