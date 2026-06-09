import csv
import os
from src.registro import registrar, _RUTA_CSV

def test_registrar_crea_csv(tmp_path, monkeypatch):
    # Mocking _RUTA_CSV to use a temporary directory
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)

    registrar("Feliz", 95.0, origen="test")

    assert test_csv.exists()
    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["timestamp", "origen", "emocion", "confianza"]
        assert reader[1][1] == "test"
        assert reader[1][2] == "Feliz"
        assert reader[1][3] == "95.00"

from unittest.mock import patch

def test_registrar_error(capsys):
    def mock_open(*args, **kwargs):
        raise IOError("Simulated error")

    with patch("builtins.open", mock_open):
        registrar("Feliz", 95.0, origen="test")

    captured = capsys.readouterr()
    assert "[registro] No se pudo escribir en el CSV: Simulated error" in captured.out


def test_registrar_append(tmp_path, monkeypatch):
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)

    registrar("Triste", 80.0, origen="img1")
    registrar("Enojo", 70.0, origen="img2")

    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 3 # Header + 2 rows
        assert reader[1][2] == "Triste"
        assert reader[2][2] == "Enojo"
