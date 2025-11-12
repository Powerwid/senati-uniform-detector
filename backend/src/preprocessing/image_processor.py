import cv2
import numpy as np
from PIL import Image
import io
from pathlib import Path
from typing import Union, Tuple

class ImageProcessor:

    @staticmethod
    def validate_image(file_bytes: bytes) -> bool:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()  # Verifica que no esté corrupta
            return True
        except Exception:
            return False
    
    @staticmethod
    def bytes_to_opencv(file_bytes: bytes) -> np.ndarray:

        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("No se pudo decodificar la imagen")
        
        return img
    
    @staticmethod
    def opencv_to_bytes(img: np.ndarray, format: str = '.jpg') -> bytes:

        success, buffer = cv2.imencode(format, img)
        
        if not success:
            raise ValueError(f"No se pudo codificar la imagen en formato {format}")
        
        return buffer.tobytes()
    
    @staticmethod
    def resize_maintain_aspect(
        img: np.ndarray,
        target_size: int = 640,
        padding_color: Tuple[int, int, int] = (114, 114, 114)
    ) -> np.ndarray:

        h, w = img.shape[:2]
        
        # Calcular escala
        scale = target_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Redimensionar
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Crear canvas con padding
        canvas = np.full(
            (target_size, target_size, 3),
            padding_color,
            dtype=np.uint8
        )
        
        # Calcular posición para centrar
        top = (target_size - new_h) // 2
        left = (target_size - new_w) // 2
        
        # Colocar imagen en el centro
        canvas[top:top+new_h, left:left+new_w] = resized
        
        return canvas
    
    @staticmethod
    def normalize_image(img: np.ndarray) -> np.ndarray:

        return img.astype(np.float32) / 255.0
    
    @staticmethod
    def enhance_contrast(img: np.ndarray, alpha: float = 1.5, beta: int = 0) -> np.ndarray:

        return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    
    @staticmethod
    def get_image_info(img: Union[str, np.ndarray]) -> dict:

        if isinstance(img, str):
            img = cv2.imread(img)
        
        if img is None:
            raise ValueError("No se pudo leer la imagen")
        
        height, width = img.shape[:2]
        channels = img.shape[2] if len(img.shape) > 2 else 1
        
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'aspect_ratio': width / height,
            'total_pixels': width * height,
            'size_mb': img.nbytes / (1024 * 1024)
        }
    
    @staticmethod
    def check_image_quality(img_path: str) -> dict:

        img = cv2.imread(img_path)
        
        if img is None:
            raise ValueError(f"No se pudo leer la imagen: {img_path}")
        
        # Convertir a escala de grises para análisis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calcular nitidez (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calcular brillo promedio
        brightness = np.mean(gray)
        
        # Calcular contraste (desviación estándar)
        contrast = np.std(gray)
        
        # Evaluación cualitativa
        sharpness_quality = "buena" if laplacian_var > 100 else "baja"
        brightness_quality = "adecuado" if 50 < brightness < 200 else "inadecuado"
        contrast_quality = "bueno" if contrast > 30 else "bajo"
        
        return {
            'sharpness': round(laplacian_var, 2),
            'sharpness_quality': sharpness_quality,
            'brightness': round(brightness, 2),
            'brightness_quality': brightness_quality,
            'contrast': round(contrast, 2),
            'contrast_quality': contrast_quality,
            'overall_quality': "aceptable" if laplacian_var > 100 and contrast > 30 else "mejorable"
        }


# ==========================================
# FUNCIONES DE UTILIDAD
# ==========================================

def batch_resize_images(
    input_dir: str,
    output_dir: str,
    target_size: int = 640
):

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    processor = ImageProcessor()
    
    # Obtener todas las imágenes
    image_files = list(input_path.glob('*.jpg')) + \
                  list(input_path.glob('*.png')) + \
                  list(input_path.glob('*.jpeg'))
    
    print(f"📊 Redimensionando {len(image_files)} imágenes a {target_size}x{target_size}...")
    
    for i, img_file in enumerate(image_files, 1):
        print(f"   [{i}/{len(image_files)}] {img_file.name}")
        
        # Leer imagen
        img = cv2.imread(str(img_file))
        
        # Redimensionar
        resized = processor.resize_maintain_aspect(img, target_size)
        
        # Guardar
        output_file = output_path / img_file.name
        cv2.imwrite(str(output_file), resized)
    
    print(f"✅ Imágenes guardadas en: {output_dir}")


# ==========================================
# SCRIPT DE PRUEBA
# ==========================================

if __name__ == "__main__":
    print("="*60)
    print("   PRUEBA DEL PREPROCESADOR DE IMÁGENES")
    print("="*60)
    print()
    
    processor = ImageProcessor()
    
    # Buscar una imagen de test
    test_images_dir = Path("data/test/images")
    
    if test_images_dir.exists():
        test_images = list(test_images_dir.glob("*.jpg"))
        
        if test_images:
            test_image = str(test_images[0])
            
            print(f"🖼️  Imagen de prueba: {Path(test_image).name}\n")
            
            # Test 1: Información de la imagen
            print("TEST 1: Información de la imagen")
            print("-" * 40)
            info = processor.get_image_info(test_image)
            for key, value in info.items():
                print(f"  {key}: {value}")
            print()
            
            # Test 2: Análisis de calidad
            print("TEST 2: Análisis de calidad")
            print("-" * 40)
            quality = processor.check_image_quality(test_image)
            for key, value in quality.items():
                print(f"  {key}: {value}")
            print()
            
            # Test 3: Redimensionamiento
            print("TEST 3: Redimensionamiento")
            print("-" * 40)
            img = cv2.imread(test_image)
            resized = processor.resize_maintain_aspect(img, 640)
            cv2.imwrite("test_resized.jpg", resized)
            print(f"  Original: {img.shape[1]}x{img.shape[0]}")
            print(f"  Redimensionada: {resized.shape[1]}x{resized.shape[0]}")
            print(f"  Guardada: test_resized.jpg")
            print()
            
            print("✅ Todas las pruebas completadas")
        else:
            print("⚠️  No hay imágenes en data/test/images")
    else:
        print("⚠️  No existe la carpeta data/test/images")