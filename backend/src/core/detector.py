from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Union
import json

class UniformDetector:
    
    def __init__(
        self, 
        model_path: str = "models/trained/senati_v1/weights/best.pt",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ):

        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f" No se encontró el modelo en: {model_path}\n"
                f"   Asegúrate de haber entrenado el modelo primero:\n"
                f"   python src/training/train_model.py"
            )
        
        print(f" Cargando modelo desde: {model_path}")
        self.model = YOLO(str(model_path))
        
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        print(f" Modelo cargado exitosamente")
        print(f"   Confianza mínima: {conf_threshold}")
        print(f"   IoU threshold: {iou_threshold}")
    
    def detect_image(
        self, 
        image_source: Union[str, np.ndarray],
        conf: float = None
    ) -> List[Dict]:

        if conf is None:
            conf = self.conf_threshold
        
        results = self.model.predict(
            source=image_source,
            conf=conf,
            iou=self.iou_threshold,
            imgsz=640,
            verbose=False
        )[0]
        
        detections = []
        
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            width = x2 - x1
            height = y2 - y1
            x_center = x1 + width / 2
            y_center = y1 + height / 2
            
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            class_name = results.names[class_id]
            
            detection = {
                'class': class_name,
                'class_id': class_id,
                'confidence': round(confidence, 3),
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'bbox_center': [float(x_center), float(y_center)],
                'bbox_size': [float(width), float(height)]
            }
            
            detections.append(detection)
        
        return detections
    
    def detect_and_draw(
        self,
        image_path: str,
        conf: float = None,
        save_path: str = None
    ) -> np.ndarray:

        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"No se pudo leer la imagen: {image_path}")
        
        detections = self.detect_image(image_path, conf)
        
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            confidence = det['confidence']
            class_name = det['class']
            
            color = (0, 255, 0)
            thickness = 2
            
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
            
            label = f"{class_name}: {confidence:.2f}"
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, font_thickness
            )
            
            cv2.rectangle(
                img,
                (x1, y1 - text_height - baseline - 5),
                (x1 + text_width, y1),
                color,
                -1 
            )
            
            cv2.putText(
                img,
                label,
                (x1, y1 - baseline - 5),
                font,
                font_scale,
                (0, 0, 0),
                font_thickness
            )
        
        if save_path:
            cv2.imwrite(save_path, img)
            print(f" Imagen guardada en: {save_path}")
    
        return img
    
    def get_detection_summary(
        self,
        image_path: str,
        conf: float = None
    ) -> Dict:

        detections = self.detect_image(image_path, conf)
        
        summary = {
            'image': str(image_path),
            'model': str(self.model_path),
            'confidence_threshold': conf or self.conf_threshold,
            'detections_count': len(detections),
            'detections': detections
        }
        
        return summary
    
    def detect_batch(
        self,
        image_dir: str,
        output_dir: str = None,
        conf: float = None
    ) -> List[Dict]:

        image_dir = Path(image_dir)
        
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(image_dir.glob(ext))
        
        if len(image_files) == 0:
            print(f"  No se encontraron imágenes en {image_dir}")
            return []
        
        print(f" Procesando {len(image_files)} imágenes...")
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for i, img_path in enumerate(image_files, 1):
            print(f"   [{i}/{len(image_files)}] {img_path.name}")
            
            summary = self.get_detection_summary(img_path, conf)
            results.append(summary)
            
            if output_dir:
                save_path = output_dir / f"detected_{img_path.name}"
                self.detect_and_draw(img_path, conf, str(save_path))
        
        print(f" Procesamiento completado")
        
        if output_dir:
            summary_path = output_dir / "detection_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f" Resumen guardado en: {summary_path}")
        
        return results
    
    def change_confidence_threshold(self, new_threshold: float):

        if not 0 <= new_threshold <= 1:
            raise ValueError("El umbral debe estar entre 0 y 1")
        
        self.conf_threshold = new_threshold
        print(f"✓ Umbral de confianza actualizado a: {new_threshold}")

def test_detector():

    print("="*60)
    print("   PRUEBA DEL DETECTOR DE UNIFORMES")
    print("="*60)
    print()
    
    try:
        detector = UniformDetector()
        
        test_images_dir = Path("data/test/images")
        
        if not test_images_dir.exists():
            print("  No se encontró la carpeta data/test/images")
            print("   Crea primero el dataset y entrena el modelo")
            return
        
        test_images = list(test_images_dir.glob("*.jpg")) + \
                      list(test_images_dir.glob("*.png"))
        
        if len(test_images) == 0:
            print("  No hay imágenes en data/test/images")
            return
        
        test_image = test_images[0]
        print(f"  Imagen de prueba: {test_image.name}\n")
        
        print("TEST 1: Detección simple")
        print("-" * 40)
        detections = detector.detect_image(str(test_image))
        print(f"Detecciones encontradas: {len(detections)}")
        
        for i, det in enumerate(detections, 1):
            print(f"  {i}. {det['class']} - Confianza: {det['confidence']}")
        print()
        
        print("TEST 2: Detección con visualización")
        print("-" * 40)
        output_image = "test_detection_result.jpg"
        detector.detect_and_draw(str(test_image), save_path=output_image)
        print()
        
        print("TEST 3: Resumen JSON")
        print("-" * 40)
        summary = detector.get_detection_summary(str(test_image))
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print()
        
        print("TEST 4: Procesamiento por lotes")
        print("-" * 40)
        detector.detect_batch(
            image_dir="data/test/images",
            output_dir="test_batch_results",
            conf=0.25
        )
        
        print("\n" + "="*60)
        print("TODAS LAS PRUEBAS COMPLETADAS")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"\n Error: {e}")
        print("\n Solución:")
        print("   1. Asegúrate de haber entrenado el modelo:")
        print("      python src/training/train_model.py")
        print("   2. Verifica que existe: models/trained/senati_v1/weights/best.pt")
    except Exception as e:
        print(f"\n Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_detector()