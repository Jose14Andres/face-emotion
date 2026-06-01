"""
registro.py — Persistencia de detecciones en data/registro.csv.
La ruta del CSV se resuelve siempre relativa a la raíz del proyecto SREF,
sin importar desde qué directorio se invoque el script.
"""

import csv
import datetime
from pathlib import Path

# Raíz del proyecto: sube un nivel desde src/ -> SREF/
_RAIZ = Path(__file__).parent.parent

# Carpeta y archivo de salida
_DIR_DATA = _RAIZ / "data"
_RUTA_CSV = _DIR_DATA / "registro.csv"

# Columnas del CSV (orden fijo)
_ENCABEZADO = ["timestamp", "origen", "emocion", "confianza"]


def _inicializar_csv():
    """
    Crea data/ y registro.csv con encabezado si aún no existen.
    Se llama automáticamente antes de cada escritura.
    """
    _DIR_DATA.mkdir(parents=True, exist_ok=True)

    # Solo escribe el encabezado si el archivo es nuevo o está vacío
    if not _RUTA_CSV.exists() or _RUTA_CSV.stat().st_size == 0:
        with open(_RUTA_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(_ENCABEZADO)


def registrar(emocion, confianza, origen="webcam"):
    """
    Añade una fila de detección al CSV.

    Parámetros
    ----------
    emocion : str
        Emoción detectada en español (p. ej. "Feliz").
    confianza : float
        Porcentaje de confianza de la emoción dominante (0.0 – 100.0).
    origen : str, opcional
        Fuente de la detección: "webcam" o el nombre del archivo de imagen.
        Por defecto "webcam".
    """
    try:
        _inicializar_csv()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(_RUTA_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, origen, emocion, f"{confianza:.2f}"])

    except Exception as error:
        # El fallo de escritura no debe detener el resto de la aplicación
        print(f"[registro] No se pudo escribir en el CSV: {error}")


# ---------------------------------------------------------------------------
# Bloque de prueba aislada: escribe filas de ejemplo y muestra el resultado
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Escribiendo filas de prueba en: {_RUTA_CSV}\n")

    # Tres detecciones de ejemplo con distintos orígenes
    registrar("Feliz",    91.5,  origen="webcam")
    registrar("Sorpresa", 74.3,  origen="webcam")
    registrar("Neutral",  88.0,  origen="foto_prueba.jpg")

    # Leer e imprimir el contenido completo del CSV
    print("Contenido actual de registro.csv:")
    print("-" * 55)
    with open(_RUTA_CSV, "r", encoding="utf-8") as f:
        print(f.read(), end="")
    print("-" * 55)
    print(f"\nArchivo guardado en: {_RUTA_CSV.resolve()}")
