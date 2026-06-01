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

from src.detector  import detectar_rostros
from src.analizador import analizar_emocion
from src.registro  import registrar

# Color índigo en BGR para recuadros y etiquetas
_COLOR = (79, 70, 229)


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
            for i, (x, y, w, h) in enumerate(rostros):
                recorte = frame[y:y + h, x:x + w]
                emocion, confianza = analizar_emocion(recorte)
                cache[i] = (emocion, confianza)
                # Registrar cada detección en el CSV
                registrar(emocion, confianza, origen="webcam")

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
            f"Error: no se encontró el archivo '{ruta}'.\n"
            "Verifica que la ruta sea correcta."
        )
        sys.exit(1)

    frame = cv2.imread(str(ruta))
    if frame is None:
        print(
            f"Error: no se pudo leer la imagen '{ruta}'.\n"
            "Asegúrate de que sea un formato válido (JPG, PNG, BMP, etc.)."
        )
        sys.exit(1)

    print(f"Procesando imagen: {ruta.name}")

    rostros = detectar_rostros(frame)

    if not rostros:
        print("No se detectaron rostros en la imagen.")
    else:
        print(f"Rostros detectados: {len(rostros)}")

    # Analizar, dibujar y registrar cada rostro
    for i, (x, y, w, h) in enumerate(rostros):
        recorte = frame[y:y + h, x:x + w]
        emocion, confianza = analizar_emocion(recorte)

        print(f"  Rostro {i + 1}: {emocion} ({confianza:.1f}%)")
        dibujar(frame, x, y, w, h, emocion, confianza)
        registrar(emocion, confianza, origen=ruta.name)

    # Guardar copia anotada junto al archivo original
    ruta_resultado = ruta.parent / f"{ruta.stem}_resultado{ruta.suffix}"
    cv2.imwrite(str(ruta_resultado), frame)
    print(f"\nImagen anotada guardada en: {ruta_resultado.resolve()}")

    # Mostrar resultado en ventana (cerrar con cualquier tecla)
    cv2.imshow(f"SREF — {ruta.name} (cualquier tecla para cerrar)", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


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
        help="Ruta a un archivo de imagen. Sin este argumento arranca la webcam.",
    )
    args = parser.parse_args()

    if args.imagen:
        modo_imagen(args.imagen)
    else:
        modo_webcam()


if __name__ == "__main__":
    main()
