# SREF — Sistema de Reconocimiento de Emociones Faciales

Este proyecto realiza la detección de rostros y el análisis de emociones utilizando OpenCV y DeepFace. Las emociones detectadas se registran en un archivo CSV para su posterior análisis.

## Requisitos

- Python 3.11+
- Dependencias listadas en `requirements.txt`

## Instalación

Se recomienda el uso de un entorno virtual:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

El sistema cuenta con tres modos de operación:

### 1. Modo Webcam (Tiempo Real)
Detecta y analiza emociones desde la cámara predeterminada.
```bash
python -m src.app
```
*Presiona 'q' para salir.*

### 2. Modo Imagen
Procesa una única imagen estática, guarda el resultado anotado y lo registra en el CSV.
```bash
python -m src.app --imagen ruta/a/tu/foto.jpg
```

### 3. Modo Lote (Batch)
Procesa todas las imágenes (.jpg, .png, etc.) dentro de una carpeta y registra cada detección.
```bash
python -m src.app --lote ruta/a/tu/carpeta
```

## Estructura del Proyecto

- `src/app.py`: Punto de entrada y CLI.
- `src/detector.py`: Detección de rostros con Haar Cascades.
- `src/analizador.py`: Análisis de emociones con DeepFace.
- `src/registro.py`: Gestión del archivo `data/registro.csv`.
- `tests/`: Pruebas unitarias con pytest.

## Registro de Datos
Todas las detecciones se guardan en `data/registro.csv` con el siguiente formato:
`timestamp, origen, emocion, confianza`
