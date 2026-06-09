import numpy as np
from src.detector import detectar_rostros

def test_detectar_rostros_sin_rostros():
    # Arrange: Create a blank (black) image
    imagen_vacia = np.zeros((100, 100, 3), dtype=np.uint8)

    # Act: Attempt to detect faces
    rostros = detectar_rostros(imagen_vacia)

    # Assert: Should return an empty list
    assert rostros == []
