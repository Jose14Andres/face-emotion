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
