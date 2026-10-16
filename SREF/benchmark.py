import time
import shutil
import cv2
import numpy as np
from pathlib import Path
from src.app import modo_lote
from unittest.mock import patch
import sys

folder = Path("data/bench_images")
folder.mkdir(parents=True, exist_ok=True)

# 1000 images
for i in range(1000):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    cv2.imwrite(str(folder / f"img_{i}.jpg"), img)

def mock_detectar_rostros(frame):
    return [(0,0,10,10)] * 10 # 10 faces per image

def mock_analizar_emocion(recorte):
    return "Feliz", 99.0

class DummyFile:
    def write(self, x): pass
    def flush(self): pass

@patch('src.app.detectar_rostros', mock_detectar_rostros)
@patch('src.app.analizar_emocion', mock_analizar_emocion)
def run_benchmark():
    start = time.time()
    modo_lote(str(folder))
    end = time.time()
    return end - start

if __name__ == "__main__":
    old_stdout = sys.stdout
    sys.stdout = DummyFile()
    t = run_benchmark()
    sys.stdout = old_stdout
    print(f"Baseline Time taken: {t:.4f} seconds")

    # cleanup
    shutil.rmtree(str(folder))
    if Path("data/registro.csv").exists():
        Path("data/registro.csv").unlink()
