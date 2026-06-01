"""
analizador.py — Análisis de emoción facial mediante DeepFace.
Recibe un recorte de rostro (BGR) y devuelve la emoción dominante en español
junto con su porcentaje de confianza.
"""

from deepface import DeepFace

# Traducción de las 7 emociones que devuelve DeepFace (inglés -> español)
EMOCIONES_ES = {
    "angry":    "Enojo",
    "disgust":  "Asco",
    "fear":     "Miedo",
    "happy":    "Feliz",
    "sad":      "Triste",
    "surprise": "Sorpresa",
    "neutral":  "Neutral",
}

# Valor de retorno cuando el análisis no puede completarse
_EMOCION_FALLBACK = ("Desconocida", 0.0)


def analizar_emocion(rostro):
    """
    Analiza la emoción dominante en un recorte de rostro.

    Parámetros
    ----------
    rostro : numpy.ndarray
        Imagen BGR del rostro ya recortado (proveniente de detector.py).
        No es necesario que contenga un fondo: solo el área del rostro.

    Retorna
    -------
    tuple[str, float]
        (emocion_es, confianza) donde emocion_es es la emoción dominante
        traducida al español y confianza es su porcentaje (0.0 – 100.0).
        Devuelve ("Desconocida", 0.0) si el análisis falla.
    """
    try:
        # enforce_detection=False porque el rostro ya viene recortado por
        # detector.py; evita que DeepFace lance error si no re-detecta la cara.
        resultados = DeepFace.analyze(
            rostro,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )

        # DeepFace siempre devuelve una lista; tomamos el primer elemento
        emociones = resultados[0]["emotion"]

        # Emoción con mayor puntuación (valor float 0-100)
        clave_dominante = max(emociones, key=emociones.get)
        confianza = float(emociones[clave_dominante])

        # Traducir al español; si llega una clave inesperada, conservar original
        emocion_es = EMOCIONES_ES.get(clave_dominante, clave_dominante.capitalize())

        return (emocion_es, confianza)

    except Exception as error:
        print(f"[analizador] Error al analizar emoción: {error}")
        return _EMOCION_FALLBACK


# ---------------------------------------------------------------------------
# Bloque de prueba aislada: detector + analizador juntos sobre la webcam
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import cv2

    # Importación flexible: funciona tanto al ejecutar directamente
    # (python src/analizador.py) como al importar desde otro módulo.
    try:
        from src import detector          # importado como parte del paquete src
    except ImportError:
        import detector                   # ejecutado directamente desde src/

    COLOR = (79, 70, 229)   # Índigo en BGR

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError(
            "No se pudo abrir la cámara. "
            "Verifica que esté conectada y no esté en uso por otra aplicación."
        )

    print("Analizador activo. La primera ejecución descarga modelos (~700 MB).")
    print("Presiona 'q' para salir.")

    num_frame = 0
    # Caché del último resultado para no redibujar "Desconocida" entre análisis
    cache_etiquetas = {}   # {indice_rostro: (emocion_es, confianza)}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: no se pudo leer el frame de la cámara.")
            break

        num_frame += 1
        rostros = detector.detectar_rostros(frame)

        # Analizar emociones 1 de cada 5 frames para mantener fluidez
        if num_frame % 5 == 0:
            cache_etiquetas = {}
            for i, (x, y, w, h) in enumerate(rostros):
                recorte = frame[y:y + h, x:x + w]
                cache_etiquetas[i] = analizar_emocion(recorte)

        # Dibujar recuadro y etiqueta usando el último resultado en caché
        for i, (x, y, w, h) in enumerate(rostros):
            cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR, 2)

            if i in cache_etiquetas:
                emocion_es, confianza = cache_etiquetas[i]
                etiqueta = f"{emocion_es} ({confianza:.1f}%)"
            else:
                etiqueta = "Analizando..."

            cv2.putText(
                frame,
                etiqueta,
                (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                COLOR,
                2,
            )

        cv2.imshow("SREF — Detector + Analizador (q para salir)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
