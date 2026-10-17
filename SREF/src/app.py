"""
app.py — Punto de entrada del Sistema de Reconocimiento de Emociones Faciales.

Modos de uso:
  python -m src.app                  -> modo webcam en tiempo real
  python -m src.app --imagen RUTA    -> modo imagen sobre un archivo

Ejecutar siempre desde la raíz del proyecto SREF.
"""

import argparse
import sys
from pathlib import Path

import cv2

import os

from src.detector  import detectar_rostros
from src.analizador import analizar_emocion
from src.registro  import registrar, registrar_lote

# Intentar detectar si hay un entorno gráfico disponible
_HEADLESS = os.environ.get("DISPLAY") is None

# Color índigo en BGR para recuadros y etiquetas
_COLOR = (79, 70, 229)

# Límite máximo de tamaño de archivo (20 MB en bytes)
_MAX_FILE_SIZE = 20 * 1024 * 1024


# ---------------------------------------------------------------------------
# Función auxiliar de dibujo — reutilizada en ambos modos
# ---------------------------------------------------------------------------

def dibujar(frame, x, y, w, h, emocion, confianza):
    """
    Dibuja un recuadro índigo y la etiqueta 'Emocion (XX.X%)' sobre frame.

    Parámetros
    ----------
    frame    : numpy.ndarray  Imagen BGR sobre la que se pinta.
    x, y, w, h : int          Posición y tamaño del rostro detectado.
    emocion  : str            Emoción dominante en español.
    confianza: float          Porcentaje de confianza (0.0 – 100.0).
    """
    # Recuadro alrededor del rostro
    cv2.rectangle(frame, (x, y), (x + w, y + h), _COLOR, 2)

    etiqueta = f"{emocion} ({confianza:.1f}%)"

    # Fondo semitransparente para la etiqueta (mejora legibilidad)
    (ancho_txt, alto_txt), _ = cv2.getTextSize(
        etiqueta, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2
    )
    y_fondo = max(y - 28, 0)
    cv2.rectangle(
        frame,
        (x, y_fondo),
        (x + ancho_txt + 6, y_fondo + alto_txt + 8),
        _COLOR,
        cv2.FILLED,
    )

    cv2.putText(
        frame,
        etiqueta,
        (x + 3, y_fondo + alto_txt + 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),  # texto blanco sobre fondo índigo
        2,
    )


# ---------------------------------------------------------------------------
# Modo webcam
# ---------------------------------------------------------------------------

def modo_webcam():
    """Captura video de la cámara 0, detecta rostros y analiza emociones."""
    if _HEADLESS:
        print("Error: El modo webcam requiere un entorno gráfico (DISPLAY).")
        sys.exit(1)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(
            "Error: no se pudo abrir la cámara.\n"
            "Verifica que esté conectada y no esté en uso por otra aplicación."
        )
        sys.exit(1)

    print("Modo webcam activo. Presiona 'q' para salir.")

    num_frame = 0
    # Caché: guarda el último análisis para no redibujar 'Analizando...' entre frames
    cache = {}  # {i: (emocion_es, confianza)}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: no se pudo leer el frame de la cámara. Cerrando.")
            break

        num_frame += 1
        rostros = detectar_rostros(frame)

        # Analizar y registrar 1 de cada 5 frames para mantener fluidez
        if num_frame % 5 == 0:
            cache = {}
            detecciones = []
            registros_lote = []
            entradas = []
            for i, (x, y, w, h) in enumerate(rostros):
                recorte = frame[y:y + h, x:x + w]
                emocion, confianza = analizar_emocion(recorte)
                cache[i] = (emocion, confianza)
                # Acumular cada detección para el CSV
                detecciones.append((emocion, confianza, "webcam"))
            registrar_lote(detecciones)
                registros_lote.append({'emocion': emocion, 'confianza': confianza, 'origen': 'webcam'})

            # Registrar todas las detecciones del frame en una sola operación I/O
            if registros_lote:
                registrar(registros_lote)
                entradas.append((emocion, confianza, "webcam"))

            if entradas:
                registrar(lote=entradas)

        # Dibujar usando el último resultado disponible en caché
        for i, (x, y, w, h) in enumerate(rostros):
            if i in cache:
                emocion, confianza = cache[i]
            else:
                emocion, confianza = "Analizando...", 0.0
            dibujar(frame, x, y, w, h, emocion, confianza)

        cv2.imshow("SREF — Webcam (q para salir)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Sesión webcam finalizada.")


# ---------------------------------------------------------------------------
# Modo imagen
# ---------------------------------------------------------------------------

def modo_imagen(ruta_str):
    """
    Detecta y analiza emociones en una imagen estática.

    Guarda una copia anotada como <nombre>_resultado.<ext> junto al original.
    """
    ruta = Path(ruta_str)

    if not ruta.exists():
        print(
            f"Error: no se encontró el archivo {str(ruta)!r}.\n"
            "Verifica que la ruta sea correcta."
        )
        sys.exit(1)

    if os.path.getsize(str(ruta)) > _MAX_FILE_SIZE:
        print(
            f"Error: el archivo {ruta!r} supera el límite de tamaño permitido "
            f"({_MAX_FILE_SIZE / (1024*1024):.0f} MB)."
        )
        sys.exit(1)

    frame = cv2.imread(str(ruta))
    if frame is None:
        print(
            f"Error: no se pudo leer la imagen {str(ruta)!r}.\n"
            "Asegúrate de que sea un formato válido (JPG, PNG, BMP, etc.)."
        )
        sys.exit(1)

    print(f"Procesando imagen: {str(ruta.name)!r}")

    rostros = detectar_rostros(frame)

    if not rostros:
        print("No se detectaron rostros en la imagen.")
    else:
        print(f"Rostros detectados: {len(rostros)}")

    # Analizar, dibujar y registrar cada rostro
    detecciones = []
    registros_lote = []
    entradas = []
    for i, (x, y, w, h) in enumerate(rostros):
        recorte = frame[y:y + h, x:x + w]
        emocion, confianza = analizar_emocion(recorte)

        print(f"  Rostro {i + 1}: {emocion} ({confianza:.1f}%)")
        dibujar(frame, x, y, w, h, emocion, confianza)
        detecciones.append((emocion, confianza, ruta.name))

    registrar_lote(detecciones)
        registros_lote.append({'emocion': emocion, 'confianza': confianza, 'origen': ruta.name})

    if registros_lote:
        registrar(registros_lote)
        entradas.append((emocion, confianza, ruta.name))

    if entradas:
        registrar(lote=entradas)

    # Guardar copia anotada junto al archivo original
    ruta_resultado = ruta.parent / f"{ruta.stem}_resultado{ruta.suffix}"
    cv2.imwrite(str(ruta_resultado), frame)
    print(f"\nImagen anotada guardada en: {ruta_resultado.resolve()}")

    # Mostrar resultado en ventana si no estamos en modo headless
    if not _HEADLESS:
        cv2.imshow(f"SREF — {ruta.name} (cualquier tecla para cerrar)", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# Modo lote
# ---------------------------------------------------------------------------

def modo_lote(ruta_carpeta):
    """
    Procesa todas las imágenes de una carpeta.
    """
    carpeta = Path(ruta_carpeta)

    if not carpeta.exists() or not carpeta.is_dir():
        print(
            f"Error: no se encontró la carpeta {str(carpeta)!r} o no es un directorio.\n"
            "Verifica que la ruta sea correcta."
        )
        sys.exit(1)

    extensiones = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    imagenes = [f for f in carpeta.iterdir() if f.suffix.lower() in extensiones]

    if not imagenes:
        print(f"No se encontraron imágenes en la carpeta {str(carpeta)!r}.")
        return

    print(f"Procesando lote de {len(imagenes)} imágenes en: {str(carpeta.name)!r}")

    resultados_lote = []

    for ruta_img in imagenes:
        if os.path.getsize(str(ruta_img)) > _MAX_FILE_SIZE:
            print(
                f"  [Error] El archivo {ruta_img.name!r} supera el límite "
                f"({_MAX_FILE_SIZE / (1024*1024):.0f} MB). Saltando."
            )
            continue

        # Reutilizamos la lógica de modo_imagen pero sin mostrar ventanas
        frame = cv2.imread(str(ruta_img))
        if frame is None:
            print(f"  [Error] No se pudo leer la imagen: {str(ruta_img.name)!r}")
            continue

        rostros = detectar_rostros(frame)
        print(f"  Imagen: {str(ruta_img.name)!r} - Rostros: {len(rostros)}")

        detecciones = []
        registros_lote = []
        entradas = []
        for i, (x, y, w, h) in enumerate(rostros):
            recorte = frame[y:y + h, x:x + w]
            emocion, confianza = analizar_emocion(recorte)
            dibujar(frame, x, y, w, h, emocion, confianza)
            detecciones.append((emocion, confianza, ruta_img.name))

        registrar_lote(detecciones)
            registros_lote.append({'emocion': emocion, 'confianza': confianza, 'origen': ruta_img.name})

        if registros_lote:
            registrar(registros_lote)
            resultados_lote.append((emocion, confianza, ruta_img.name))
            entradas.append((emocion, confianza, ruta_img.name))

        if entradas:
            registrar(lote=entradas)

        # Guardar copia anotada
        ruta_resultado = ruta_img.parent / f"{ruta_img.stem}_resultado{ruta_img.suffix}"
        cv2.imwrite(str(ruta_resultado), frame)

    if resultados_lote:
        registrar_lote(resultados_lote)

    print(f"\nProceso de lote finalizado. Resultados guardados en {carpeta.resolve()}")


# ---------------------------------------------------------------------------
# Punto de entrada — parseo de argumentos
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="python -m src.app",
        description="SREF — Sistema de Reconocimiento de Emociones Faciales",
    )
    parser.add_argument(
        "--imagen",
        metavar="RUTA",
        help="Ruta a un archivo de imagen.",
    )
    parser.add_argument(
        "--lote",
        metavar="CARPETA",
        help="Ruta a una carpeta de imágenes para procesar en lote.",
    )
    args = parser.parse_args()

    if args.imagen:
        modo_imagen(args.imagen)
    elif args.lote:
        modo_lote(args.lote)
    else:
        modo_webcam()


if __name__ == "__main__":
    main()
