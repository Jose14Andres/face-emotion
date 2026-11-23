# SREF — Sistema de Reconocimiento de Emociones Faciales

Aplicación de línea de comandos en Python que detecta rostros con **OpenCV (Haar Cascade)** y clasifica su emoción dominante con **DeepFace**. Funciona en tiempo real con la webcam, sobre una imagen suelta o sobre una carpeta completa, y guarda cada detección en un archivo CSV para analizarla después.

## Características

- **Tres modos de uso**: webcam en tiempo real, imagen individual y procesamiento por lotes.
- **7 emociones** traducidas al español: Enojo, Asco, Miedo, Feliz, Triste, Sorpresa y Neutral.
- **Imágenes anotadas**: cada rostro se marca con un recuadro y la etiqueta `Emoción (XX.X%)`; el resultado se guarda como `<nombre>_resultado.<ext>`.
- **Registro en CSV** (`SREF/data/registro.csv`) con escritura por lotes para reducir operaciones de E/S.
- **Fluidez en webcam**: el análisis de emociones se ejecuta 1 de cada 5 frames y el último resultado se reutiliza entre análisis.
- **Medidas de seguridad**:
  - Protección contra inyección de fórmulas en el CSV (valores que empiezan por `=`, `+`, `-` o `@`).
  - Rutas de archivo escapadas en los mensajes de consola para evitar inyección de secuencias de escape en la terminal.
  - Límite de 20 MB por imagen.

## Estructura del proyecto

```
face-emotion/
├── README.md
└── SREF/
    ├── requirements.txt
    ├── benchmark.py          # Benchmarks de rendimiento (modo lote y escritura en CSV)
    ├── src/
    │   ├── app.py            # Punto de entrada y CLI (webcam / imagen / lote)
    │   ├── detector.py       # Detección de rostros con Haar Cascade
    │   ├── analizador.py     # Análisis de emociones con DeepFace
    │   └── registro.py       # Persistencia en data/registro.csv
    └── tests/                # Pruebas unitarias con pytest
```

## Requisitos

- Python 3.11 o superior
- Una cámara web (solo para el modo webcam)
- Dependencias principales (`SREF/requirements.txt`):

| Paquete        | Versión   |
|----------------|-----------|
| deepface       | 0.0.93    |
| opencv-python  | 4.10.0.84 |
| tf-keras       | 2.19.0    |
| scikit-learn   | 1.6.0     |
| matplotlib     | 3.10.0    |
| pytest         | 8.3.4     |

> La primera vez que se ejecuta el análisis, DeepFace descarga automáticamente los pesos del modelo de emociones, así que se necesita conexión a internet.

## Instalación

```bash
git clone https://github.com/Jose14Andres/face-emotion.git
cd face-emotion/SREF

# Crear y activar un entorno virtual
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

Todos los comandos se ejecutan **desde la carpeta `SREF/`**.

### 1. Modo webcam (tiempo real)

```bash
python -m src.app
```

Abre la cámara predeterminada y muestra las emociones en vivo. Pulsa `q` para salir.

### 2. Modo imagen

```bash
python -m src.app --imagen ruta/a/foto.jpg
```

Analiza la imagen, imprime la emoción de cada rostro, guarda `foto_resultado.jpg` junto al original y registra las detecciones en el CSV.

### 3. Modo lote

```bash
python -m src.app --lote ruta/a/carpeta
```

Procesa todas las imágenes `.jpg`, `.jpeg`, `.png`, `.bmp` y `.webp` de la carpeta, genera una copia anotada de cada una y registra todas las detecciones.

### Probar módulos por separado

Cada módulo incluye un bloque de prueba independiente:

```bash
python -m src.detector     # Solo detección de rostros con la webcam
python -m src.analizador   # Detección + emoción con la webcam
python -m src.registro     # Escribe filas de ejemplo en el CSV
```

## Registro de datos

Las detecciones se guardan en `SREF/data/registro.csv` (se crea automáticamente) con este formato:

```csv
timestamp,origen,emocion,confianza
2026-11-22 10:15:32,webcam,Feliz,91.50
2026-11-22 10:16:04,foto.jpg,Sorpresa,74.30
```

| Columna     | Descripción                                            |
|-------------|--------------------------------------------------------|
| `timestamp` | Fecha y hora de la detección (`YYYY-MM-DD HH:MM:SS`)   |
| `origen`    | `webcam` o el nombre del archivo de imagen             |
| `emocion`   | Emoción dominante en español                           |
| `confianza` | Porcentaje de confianza (0.00 – 100.00)                |

Si el análisis falla, la emoción se registra como `Desconocida` con confianza `0.00`.

## Pruebas

```bash
cd SREF
pytest
```

Las pruebas cubren la traducción de emociones y el manejo de errores del analizador, la detección sin rostros, la escritura del CSV (incluida la escritura por lotes y la protección contra inyección de fórmulas) y la seguridad de los mensajes de la CLI. DeepFace se simula con `unittest.mock`, así que no hace falta descargar el modelo para ejecutarlas.

## Benchmark

```bash
cd SREF
python benchmark.py
```

Mide el tiempo del modo lote sobre 1000 imágenes sintéticas (con detección y análisis simulados) y compara escrituras individuales frente a una escritura por lotes en el CSV.

## Tecnologías

- [OpenCV](https://opencv.org/): captura de video, detección de rostros y dibujo.
- [DeepFace](https://github.com/serengil/deepface): clasificación de emociones.
- [TensorFlow / tf-keras](https://www.tensorflow.org/): backend del modelo de DeepFace.
- [pytest](https://pytest.org/): pruebas unitarias.
