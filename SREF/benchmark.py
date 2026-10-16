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
import csv
import os
from src.registro import _RUTA_CSV

def registrar_old(emocion, confianza, origen="webcam"):
    with open(_RUTA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["2023-01-01 12:00:00", origen, emocion, f"{confianza:.2f}"])

def registrar_new(entradas):
    filas = []
    for e in entradas:
        filas.append(["2023-01-01 12:00:00", e["origen"], e["emocion"], f"{e['confianza']:.2f}"])
    with open(_RUTA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(filas)

def run_benchmarks():
    if os.path.exists(_RUTA_CSV):
        os.remove(_RUTA_CSV)

    start_time = time.time()
    for _ in range(1000):
        registrar_old("Feliz", 90.0, origen="benchmark")
    end_time = time.time()
    old_time = end_time - start_time
    print(f"Time taken (1000 single writes): {old_time:.4f} seconds")

    if os.path.exists(_RUTA_CSV):
        os.remove(_RUTA_CSV)

    start_time = time.time()
    entradas = [{"emocion": "Feliz", "confianza": 90.0, "origen": "benchmark"} for _ in range(1000)]
    registrar_new(entradas)
    end_time = time.time()
    new_time = end_time - start_time
    print(f"Time taken (1 batch write of 1000): {new_time:.4f} seconds")
    print(f"Speedup: {old_time / new_time:.2f}x")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(_RUTA_CSV), exist_ok=True)
    run_benchmarks()
