from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import io
from pathlib import Path
import sys
import numpy as np

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.detector import UniformDetector
from src.preprocessing.image_processor import ImageProcessor

app = FastAPI(
    title="SENATI Uniform Detector API",
    description="API para detectar uniformes SENATI usando YOLOv8",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


TEMP_DIR = Path("tmp")
TEMP_DIR.mkdir(exist_ok=True)

print(" Iniciando API...")

try:
    detector = UniformDetector(
        model_path="models/trained/senati_v2/weights/best.pt",
        conf_threshold=0.25
    )
    processor = ImageProcessor()
    print(" Modelo cargado\n")
except Exception as e:
    print(f" Advertencia al cargar modelo: {e}")
    detector = None
    processor = ImageProcessor()


@app.get("/")
def root():
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
            "detect_video": "/api/detect/video",
            "live_frame": "/api/detect/live-frame",
            "analyze": "/api/analyze"
        }
    }


@app.get("/api/health")
def health_check():
    if detector is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "Modelo no cargado",
                "model_loaded": False,
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
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    stats = {
        "model_name": "YOLOv8s",
        "model_path": str(detector.model_path),
        "classes": ["uniforme_senati"],
        "confidence_threshold": detector.conf_threshold,
        "iou_threshold": detector.iou_threshold,
        "input_size": "640x640"
    }
    
    metadata_file = detector.model_path.parent.parent / "metadata.json"
    if metadata_file.exists():
        import json
        with open(metadata_file, "r") as f:
            stats["training_info"] = json.load(f)

    return stats

@app.post("/api/detect")
async def detect_uniform(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0, le=1)
):
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Debe enviar una imagen")

    contents = await file.read()
    if not processor.validate_image(contents):
        raise HTTPException(status_code=400, detail="Imagen inválida")

    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(contents)

    detections = detector.detect_image(str(temp_path), conf=confidence)

    temp_path.unlink(missing_ok=True)

    return {
        "filename": file.filename,
        "detections_count": len(detections),
        "detections": detections
    }

@app.post("/api/detect/visualize")
async def detect_and_visualize(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0, le=1)
):
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    contents = await file.read()
    if not processor.validate_image(contents):
        raise HTTPException(status_code=400, detail="Imagen inválida")

    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(contents)

    img_with_boxes = detector.detect_and_draw(str(temp_path), conf=confidence)
    temp_path.unlink(missing_ok=True)

    img_bytes = processor.opencv_to_bytes(img_with_boxes)

    return StreamingResponse(
        io.BytesIO(img_bytes),
        media_type="image/jpeg",
        headers={"Content-Disposition": f"inline; filename=detected_{file.filename}"}
    )

@app.post("/api/detect/video")
async def detect_video(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0, le=1)
):
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Debe enviar video")

    temp_video = TEMP_DIR / file.filename
    with open(temp_video, "wb") as f:
        f.write(await file.read())

    cap = cv2.VideoCapture(str(temp_video))
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="No se pudo procesar el video")

    results = []
    frame_count = 0
    total_detections = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        frame_path = TEMP_DIR / f"frame_{frame_count}.jpg"
        cv2.imwrite(str(frame_path), frame)

        detections = detector.detect_image(str(frame_path), conf=confidence)
        total_detections += len(detections)

        results.append({
            "frame": frame_count,
            "detections": detections
        })

        frame_path.unlink(missing_ok=True)

    cap.release()
    temp_video.unlink(missing_ok=True)

    return {
        "frames_processed": frame_count,
        "total_detections": total_detections,
        "results": results
    }

@app.post("/api/detect/live-frame")
async def detect_live_frame(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0, le=1)
):
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    content = await file.read()
    if not processor.validate_image(content):
        raise HTTPException(status_code=400, detail="Frame inválido")

    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(content)

    detections = detector.detect_image(str(temp_path), conf=confidence)
    temp_path.unlink(missing_ok=True)

    return {
        "detections_count": len(detections),
        "detections": detections
    }

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()

    if not processor.validate_image(contents):
        raise HTTPException(status_code=400, detail="Imagen inválida")

    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(contents)

    info = processor.get_image_info(str(temp_path))
    quality = processor.check_image_quality(str(temp_path))

    temp_path.unlink(missing_ok=True)

    return {
        "filename": file.filename,
        "image_info": info,
        "quality_metrics": quality
    }

@app.post("/api/confidence/set")
def set_confidence_threshold(threshold: float = Query(..., ge=0, le=1)):
    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    detector.change_confidence_threshold(threshold)

    return {"new_threshold": threshold}

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("   SENATI UNIFORM DETECTOR API")
    print("="*60)
    print(" http://localhost:8000")
    print(" API Docs: /docs")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    print("\n API detenida\n")
