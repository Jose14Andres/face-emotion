import time
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
