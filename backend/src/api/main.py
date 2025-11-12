from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import io
from pathlib import Path
import sys

# Agregar ruta para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.detector import UniformDetector
from src.preprocessing.image_processor import ImageProcessor

# ==========================================
# INICIALIZACIÓN
# ==========================================

app = FastAPI(
    title="SENATI Uniform Detector API",
    description="API para detectar uniformes SENATI usando YOLOv8",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especifica tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo al iniciar
print("🚀 Iniciando API...")

try:
    detector = UniformDetector(
        model_path="models/trained/senati_v1/weights/best.pt",
        conf_threshold=0.25
    )
    processor = ImageProcessor()
    print("✅ Modelo cargado\n")
except Exception as e:
    print(f"⚠️  Advertencia: {e}")
    print("   El modelo se cargará cuando esté disponible\n")
    detector = None
    processor = ImageProcessor()

# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "name": "SENATI Uniform Detector API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "stats": "/api/stats",
            "detect": "/api/detect",
            "visualize": "/api/detect/visualize",
            "analyze": "/api/analyze"
        }
    }


@app.get("/api/health")
def health_check():
    """
    Verifica estado de la API y del modelo
    """
    if detector is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "Modelo no cargado",
                "model_loaded": False,
                "suggestion": "Entrena el modelo: python src/training/train_model.py"
            }
        )
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_path": str(detector.model_path),
        "confidence_threshold": detector.conf_threshold,
        "version": "1.0.0"
    }


@app.get("/api/stats")
def get_model_stats():
    """
    Obtiene información del modelo
    """
    if detector is None:
        raise HTTPException(
            status_code=503, 
            detail="Modelo no disponible. Entrena primero el modelo."
        )
    
    stats = {
        "model_name": "YOLOv8s",
        "model_path": str(detector.model_path),
        "classes": ["uniforme_senati"],
        "confidence_threshold": detector.conf_threshold,
        "iou_threshold": detector.iou_threshold,
        "input_size": "640x640"
    }
    
    # Agregar metadata si existe
    metadata_file = detector.model_path.parent.parent / "metadata.json"
    if metadata_file.exists():
        import json
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            stats["training_info"] = metadata
    
    return stats


@app.post("/api/detect")
async def detect_uniform(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.0, le=1.0)
):
    """
    Detecta uniformes en una imagen
    
    Returns:
        JSON con detecciones
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Archivo debe ser una imagen")
    
    try:
        # Leer y validar
        contents = await file.read()
        if not processor.validate_image(contents):
            raise HTTPException(status_code=400, detail="Imagen inválida o corrupta")
        
        # Guardar temporalmente
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Detectar
        detections = detector.detect_image(temp_path, conf=confidence)
        
        # Limpiar
        Path(temp_path).unlink(missing_ok=True)
        
        # Respuesta
        return {
            "filename": file.filename,
            "confidence_threshold": confidence,
            "detections_count": len(detections),
            "detections": detections
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect/visualize")
async def detect_and_visualize(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.0, le=1.0)
):
    """
    Detecta uniformes y retorna imagen con bounding boxes
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Archivo debe ser una imagen")
    
    try:
        # Leer y validar
        contents = await file.read()
        if not processor.validate_image(contents):
            raise HTTPException(status_code=400, detail="Imagen inválida")
        
        # Guardar temporalmente
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Detectar y dibujar
        img_with_boxes = detector.detect_and_draw(temp_path, conf=confidence)
        
        # Limpiar
        Path(temp_path).unlink(missing_ok=True)
        
        # Convertir a bytes
        img_bytes = processor.opencv_to_bytes(img_with_boxes, '.jpg')
        
        # Retornar imagen
        return StreamingResponse(
            io.BytesIO(img_bytes),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"inline; filename=detected_{file.filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analiza calidad de imagen sin detectar
    """
    try:
        contents = await file.read()
        
        if not processor.validate_image(contents):
            raise HTTPException(status_code=400, detail="Imagen inválida")
        
        # Guardar temporalmente
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Analizar
        info = processor.get_image_info(temp_path)
        quality = processor.check_image_quality(temp_path)
        
        # Limpiar
        Path(temp_path).unlink(missing_ok=True)
        
        return {
            "filename": file.filename,
            "image_info": info,
            "quality_metrics": quality,
            "recommendation": (
                "Imagen adecuada para detección" 
                if quality['overall_quality'] == "aceptable" 
                else "Considere usar una imagen de mejor calidad"
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/confidence/set")
def set_confidence_threshold(threshold: float = Query(..., ge=0.0, le=1.0)):
    """
    Cambia el umbral de confianza
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    detector.change_confidence_threshold(threshold)
    
    return {
        "message": "Umbral actualizado",
        "new_threshold": threshold
    }


# ==========================================
# EVENTOS
# ==========================================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("   SENATI UNIFORM DETECTOR API")
    print("="*60)
    print("\n📍 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("\n🔌 Endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/stats")
    print("   POST /api/detect")
    print("   POST /api/detect/visualize")
    print("   POST /api/analyze")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    print("\n👋 API detenida\n")