from unittest.mock import patch
import numpy as np
from src.analizador import EMOCIONES_ES, analizar_emocion

def test_emociones_es_mapping():
    assert EMOCIONES_ES["happy"] == "Feliz"
    assert EMOCIONES_ES["sad"] == "Triste"
    assert EMOCIONES_ES["angry"] == "Enojo"
    assert EMOCIONES_ES["surprise"] == "Sorpresa"
    assert EMOCIONES_ES["fear"] == "Miedo"
    assert EMOCIONES_ES["disgust"] == "Asco"
    assert EMOCIONES_ES["neutral"] == "Neutral"

def test_analizar_emocion_fallback():
    # Test with invalid input should trigger exception and return fallback
    result = analizar_emocion(None)
    assert result == ("Desconocida", 0.0)

@patch('src.analizador.DeepFace.analyze')
def test_analizar_emocion_success(mock_analyze):
    # Mocking successful analyze output from DeepFace
    mock_analyze.return_value = [
        {
            "emotion": {
                "angry": 2.1,
                "disgust": 0.5,
                "fear": 1.2,
                "happy": 95.0,
                "sad": 0.1,
                "surprise": 0.8,
                "neutral": 0.3
            }
        }
    ]

    # Dummy numpy array for face (e.g., 10x10 RGB image)
    rostro = np.zeros((10, 10, 3), dtype=np.uint8)

    # Call the function
    result = analizar_emocion(rostro)

    # Verify result
    assert result == ("Feliz", 95.0)

    # Verify mock was called with expected arguments
    mock_analyze.assert_called_once_with(
        rostro,
        actions=["emotion"],
        enforce_detection=False,
        silent=True,
    )
