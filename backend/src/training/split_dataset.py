import os
import shutil
import random
from pathlib import Path

def split_dataset(
    source_dir='data/labeled',
    train_ratio=0.7,
    val_ratio=0.2,
    test_ratio=0.1,
    seed=42
):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, \
        "Las proporciones deben sumar 1.0"
    
    random.seed(seed)
    
    source_path = Path(source_dir)
    image_files = list(source_path.glob('*.jpg')) + list(source_path.glob('*.png'))
    
    if len(image_files) == 0:
        print(f" No se encontraron imágenes en {source_dir}")
        return
    
    print(f" Total de imágenes encontradas: {len(image_files)}")
    
    random.shuffle(image_files)
    
    total = len(image_files)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    
    train_files = image_files[:train_end]
    val_files = image_files[train_end:val_end]
    test_files = image_files[val_end:]
    
    print(f"  ├─ Train: {len(train_files)} imágenes ({len(train_files)/total*100:.1f}%)")
    print(f"  ├─ Val:   {len(val_files)} imágenes ({len(val_files)/total*100:.1f}%)")
    print(f"  └─ Test:  {len(test_files)} imágenes ({len(test_files)/total*100:.1f}%)")
    
    datasets = {
        'train': train_files,
        'val': val_files,
        'test': test_files
    }
    
    for split_name, file_list in datasets.items():
        img_dir = Path(f'data/{split_name}/images')
        lbl_dir = Path(f'data/{split_name}/labels')
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        
        for img_file in file_list:
            shutil.copy(img_file, img_dir / img_file.name)
            
            txt_file = img_file.with_suffix('.txt')
            if txt_file.exists():
                shutil.copy(txt_file, lbl_dir / txt_file.name)
            else:
                print(f"  Advertencia: No se encontró {txt_file.name}")
    
    print("\n Dataset dividido exitosamente")
    print(f"   Estructura creada en data/train, data/val, data/test")
    
    print("\n Verificando integridad...")
    for split_name in ['train', 'val', 'test']:
        img_count = len(list(Path(f'data/{split_name}/images').glob('*.*')))
        lbl_count = len(list(Path(f'data/{split_name}/labels').glob('*.txt')))
        
        if img_count == lbl_count:
            print(f"  ✓ {split_name}: {img_count} imágenes = {lbl_count} etiquetas")
        else:
            print(f"  ✗ {split_name}: {img_count} imágenes ≠ {lbl_count} etiquetas")

if __name__ == "__main__":
    print(" Iniciando división del dataset...\n")
    split_dataset()