# 🧠 SENATI Uniform Detector

Sistema de detección de uniformes institucionales usando visión por computadora y aprendizaje profundo.
Desarrollado con **FastAPI**, **YOLOv8 (Ultralytics)**, **PyTorch** y **OpenCV**.

---

## 📋 Objetivo

Detectar automáticamente uniformes SENATI en imágenes o video mediante un modelo de *Deep Learning* entrenado con un conjunto de imágenes etiquetadas manualmente.

---

## ⚙️ Arquitectura general

```
senati-uniform-detector/
├── configs/
│   ├── senati_dataset.yaml         # Definición del dataset YOLO
│   └── training_config.yaml        # Hiperparámetros de entrenamiento
├── data/
│   ├── raw/                        # Imágenes originales
│   ├── labeled/                    # Imágenes + etiquetas YOLO (.txt)
│   ├── train/                      # Dataset dividido para entrenamiento
│   ├── val/                        # Dataset para validación
│   └── test/                       # Dataset de prueba
├── models/
│   ├── pretrained/                 # Pesos YOLO base
│   └── trained/
│       └── senati_v1/              # Modelo entrenado
│           ├── weights/
│           │   ├── best.pt
│           │   └── last.pt
│           ├── results.png
│           └── metadata.json
├── src/
│   ├── api/
│   │   └── main.py                 # API FastAPI
│   ├── core/
│   │   └── detector.py             # Lógica de detección YOLO
│   ├── preprocessing/
│   │   └── image_processor.py      # Redimensionamiento y validación de imágenes
│   └── training/
│       ├── split_dataset.py        # Divide labeled → train/val/test
│       └── train_model.py          # Entrenamiento del modelo
└── README.md
```

---

## 🧬 Tecnologías principales

| Componente        | Tecnología                   | Descripción                                              |
| ----------------- | ---------------------------- | -------------------------------------------------------- |
| **Backend**       | FastAPI                      | Framework para exponer el modelo como API REST.          |
| **Modelo ML**     | Ultralytics YOLOv8 + PyTorch | Detección de objetos entrenada con Transfer Learning.    |
| **Procesamiento** | OpenCV                       | Lectura, redimensionamiento y análisis de imágenes.      |
| **Etiquetado**    | LabelImg                     | Herramienta para generar las etiquetas YOLO manualmente. |

---

## 🧮 Instalación

1. Clonar el repositorio

   ```bash
   git clone <repo_url>
   cd senati-uniform-detector
   ```

2. Crear entorno virtual

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instalar dependencias

   ```bash
   pip install -r requirements.txt
   ```

   *(Si no existe aún, genera uno con)*

   ```bash
   pip freeze > requirements.txt
   ```

---

## 🌂 Etiquetado de datos (LabelImg)

### Requisitos

Instalar la versión estable:

```bash
pip install labelImg==1.8.6
```

### Pasos

1. Ejecuta LabelImg:

   ```bash
   labelImg
   ```
2. En la interfaz:

   * **Open Dir:** `data/raw/`
   * **Change Save Dir:** `data/labeled/`
   * **Selecciona formato:** YOLO
   * **Default label:** `uniforme_senati`
3. Dibuja los *bounding boxes* y guarda (`Ctrl+S`).

Cada imagen generará un `.txt` como:

```
0 0.5 0.4 0.3 0.6
```

---

## 🧪 Preparar dataset

Divide las imágenes en `train`, `val` y `test`:

```bash
python src/training/split_dataset.py
```

---

## 🤓 Entrenamiento del modelo

1. Configura `configs/training_config.yaml`:

   ```yaml
   model: yolov8s.pt
   data: configs/senati_dataset.yaml
   epochs: 50
   batch: 8
   imgsz: 640
   patience: 10
   device: cpu      # Cambiar a 0 si tienes GPU
   project: models/trained
   name: senati_v1
   ```

2. Ejecuta:

   ```bash
   python src/training/train_model.py
   ```

3. Resultado:

   ```
   models/trained/senati_v1/weights/best.pt
   models/trained/senati_v1/results.png
   ```

---

## 🔍 Prueba del modelo

Prueba detección local:

```bash
python src/core/detector.py
```

Esto generará:

```
test_detection_result.jpg
test_batch_results/
 ├── detected_*.jpg
 └── detection_summary.json
```

---

## 🌐 API REST (FastAPI)

Inicia el servidor:

```bash
uvicorn src.api.main:app --reload
```

Abre en navegador:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Endpoints

| Ruta                    | Método | Descripción                           |
| ----------------------- | ------ | ------------------------------------- |
| `/`                     | GET    | Estado general del servicio           |
| `/api/health`           | GET    | Verifica si el modelo está cargado    |
| `/api/stats`            | GET    | Muestra información del modelo        |
| `/api/detect`           | POST   | Detecta uniformes en una imagen       |
| `/api/detect/visualize` | POST   | Devuelve la imagen con bounding boxes |
| `/api/analyze`          | POST   | Analiza calidad de imagen             |
| `/api/confidence/set`   | POST   | Cambia el umbral de confianza         |

---

## 📊 Flujo completo

1. Recolectar imágenes → `data/raw/`
2. Etiquetar con LabelImg → `data/labeled/`
3. Dividir dataset → `split_dataset.py`
4. Entrenar modelo → `train_model.py`
5. Probar modelo → `detector.py`
6. Servir API → `main.py`
7. (Opcional) Conectar frontend React para subir imágenes.

---

## 🧩 Pendientes del backend

* Validar más robustamente el formato YOLO en `split_dataset.py`.
* Agregar manejo de excepciones en carga de modelos en `main.py`.
* Crear endpoint `/api/train` para automatizar entrenamientos desde la API.
* Documentar con OpenAPI/Swagger cada parámetro de entrada.
* Optimizar carga del modelo con caché o lazy loading.
