"""
detector.py — Localización de rostros mediante Haar Cascade (OpenCV).
Módulo independiente: puede ejecutarse directamente para probar la detección.
"""

import cv2

# Ruta al clasificador incluido con OpenCV
_RUTA_CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# Color índigo en BGR para recuadros y texto
COLOR_RECUADRO = (79, 70, 229)


def _cargar_cascade():
    """Carga el clasificador Haar Cascade y valida que se haya leído correctamente."""
    cascade = cv2.CascadeClassifier(_RUTA_CASCADE)
    if cascade.empty():
        raise RuntimeError(
            f"No se pudo cargar el clasificador Haar Cascade.\n"
            f"Ruta esperada: {_RUTA_CASCADE}\n"
            "Verifica que opencv-python esté instalado correctamente."
        )
    return cascade


# Instancia global para no recargar el archivo en cada llamada
_cascade = _cargar_cascade()


def detectar_rostros(frame):
    """
    Detecta rostros en un frame BGR de OpenCV.

    Parámetros
    ----------
    frame : numpy.ndarray
        Imagen en formato BGR proveniente de cv2.VideoCapture o cv2.imread.

    Retorna
    -------
    list[tuple[int, int, int, int]]
        Lista de tuplas (x, y, w, h) con la posición y tamaño de cada rostro.
        Devuelve lista vacía si no se detecta ningún rostro.
    """
    # Convertir a escala de grises: Haar Cascade trabaja con imágenes de un canal
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detección: scaleFactor escala la imagen en cada paso de la pirámide;
    # minNeighbors controla cuántos vecinos debe tener un candidato para aceptarse.
    rostros = _cascade.detectMultiScale(
        gris,
        scaleFactor=1.1,
        minNeighbors=5,
    )

    # detectMultiScale devuelve una tupla vacía cuando no encuentra nada
    if len(rostros) == 0:
        return []

    # Convertir cada fila del array a una tupla (x, y, w, h)
    return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in rostros]


# ---------------------------------------------------------------------------
# Bloque de prueba aislada: abre la webcam y dibuja recuadros sobre los rostros
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError(
            "No se pudo abrir la cámara. "
            "Verifica que esté conectada y no esté en uso por otra aplicación."
        )

    print("Detector activo. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: no se pudo leer el frame de la cámara.")
            break

        rostros = detectar_rostros(frame)

        # Dibujar un recuadro índigo por cada rostro detectado
        for (x, y, w, h) in rostros:
            cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR_RECUADRO, 2)
            cv2.putText(
                frame,
                f"Rostro ({w}x{h})",
                (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                COLOR_RECUADRO,
                2,
            )

        # Contador en pantalla
        cv2.putText(
            frame,
            f"Rostros detectados: {len(rostros)}",
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            COLOR_RECUADRO,
            2,
        )

        cv2.imshow("SREF — Detector (q para salir)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
