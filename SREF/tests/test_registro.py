import csv
from src.registro import registrar, _RUTA_CSV
import os
from src.registro import registrar

def test_registrar_crea_csv(tmp_path, monkeypatch):
    # Mocking _RUTA_CSV to use a temporary directory
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)
    monkeypatch.setattr("src.registro._csv_inicializado", False)

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
    monkeypatch.setattr("src.registro._csv_inicializado", False)

    registrar("Triste", 80.0, origen="img1")
    registrar("Enojo", 70.0, origen="img2")

    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 3 # Header + 2 rows
        assert reader[1][2] == "Triste"
        assert reader[2][2] == "Enojo"


def test_registrar_formula_injection(tmp_path, monkeypatch):
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)

    malicious_origens = [
        "=cmd|' /C calc'!A0",
        "+1-1",
        "-1+1",
        "@SUM(1+1)"
    ]

    for origen in malicious_origens:
        registrar("Neutral", 50.0, origen=origen)

    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 5 # Header + 4 rows
        for i, origen in enumerate(malicious_origens, start=1):
            assert reader[i][1] == f"'{origen}"
