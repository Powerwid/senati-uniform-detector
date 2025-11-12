from ultralytics import YOLO
import yaml
from pathlib import Path
from datetime import datetime
import json

def train_senati_detector():
    """
    Entrena el modelo de detección de uniformes SENATI
    """
    print("="*60)
    print("   ENTRENAMIENTO - DETECTOR UNIFORMES SENATI")
    print("="*60)
    print()
    
    # Cargar configuración
    print("📋 Cargando configuración...")
    with open('configs/training_config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("✅ Configuración cargada:")
    for key, value in config.items():
        if key not in ['pretrained', 'verbose', 'save', 'plots', 'exist_ok']:
            print(f"   • {key}: {value}")
    print()
    
    # Verificar dataset
    with open(config['data'], 'r', encoding='utf-8') as f:
        dataset_config = yaml.safe_load(f)
    
    base_path = Path(dataset_config['path'])
    train_path = base_path / dataset_config['train']
    val_path = base_path / dataset_config['val']
    
    train_count = len(list(train_path.glob('*.*')))
    val_count = len(list(val_path.glob('*.*')))
    
    print("🔍 Verificando dataset...")
    print(f"   • Train: {train_count} imágenes")
    print(f"   • Val: {val_count} imágenes")
    
    if train_count == 0 or val_count == 0:
        print("\n❌ ERROR: Dataset vacío")
        print("\n💡 Solución:")
        print("   1. Etiqueta las imágenes en data/labeled/")
        print("   2. Ejecuta: python src/training/split_dataset.py")
        return None
    
    print("   ✓ Dataset válido\n")
    
    # Inicializar modelo
    print("🤖 Inicializando YOLOv8s...")
    model = YOLO(config['model'])
    print("   ✓ Modelo cargado con pesos pre-entrenados\n")
    
    # Entrenar
    print("🚀 INICIANDO ENTRENAMIENTO")
    print("   Tiempo estimado: 10min (GPU) / 1-3h (CPU)")
    print("   Puedes detener con Ctrl+C\n")
    print("-"*60 + "\n")
    
    try:
        results = model.train(
            data=config['data'],
            epochs=config['epochs'],
            batch=config['batch'],
            imgsz=config['imgsz'],
            patience=config['patience'],
            device=config['device'],
            project=config['project'],
            name=config['name'],
            exist_ok=config['exist_ok'],
            pretrained=config.get('pretrained', True),
            verbose=config.get('verbose', True),
            plots=config.get('plots', True),
            save=config.get('save', True)
        )
        
        # Guardar metadata
        save_dir = Path(results.save_dir)
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'dataset': {
                'train_images': train_count,
                'val_images': val_count,
                'classes': dataset_config['nc']
            },
            'paths': {
                'best_model': str(save_dir / 'weights' / 'best.pt'),
                'last_model': str(save_dir / 'weights' / 'last.pt'),
                'results': str(save_dir / 'results.png')
            }
        }
        
        metadata_path = save_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("   ✅ ENTRENAMIENTO COMPLETADO")
        print("="*60)
        print(f"\n📁 Resultados: {save_dir}")
        print(f"🏆 Modelo: {save_dir / 'weights' / 'best.pt'}")
        print(f"📊 Gráficas: {save_dir / 'results.png'}")
        print(f"📝 Metadata: {metadata_path}")
        print(f"\n💡 Siguiente paso:")
        print(f"   python src/core/detector.py")
        print("="*60 + "\n")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Entrenamiento interrumpido")
        print("   Checkpoints guardados en models/trained/\n")
        return None
        
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    train_senati_detector()