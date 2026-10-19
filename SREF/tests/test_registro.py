import csv
from src.registro import registrar, registrar_lote, _RUTA_CSV

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

def test_registrar_lote(tmp_path, monkeypatch):
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)
    monkeypatch.setattr("src.registro._csv_inicializado", False)

    entradas = [
        ("Enojo", 88.5, "img1.jpg"),
        ("Neutral", 92.1, "img2.jpg"),
        ("Triste", 45.0, "img3.jpg")
    ]
    registrar(lote=entradas)

    assert test_csv.exists()
    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 4 # Header + 3 rows
        assert reader[1][1] == "img1.jpg"
        assert reader[1][2] == "Enojo"
        assert reader[1][3] == "88.50"
        assert reader[3][1] == "img3.jpg"
        assert reader[3][2] == "Triste"

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
    monkeypatch.setattr("src.registro._csv_inicializado", False)

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

def test_registrar_lote_formula_injection(tmp_path, monkeypatch):
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)
    monkeypatch.setattr("src.registro._csv_inicializado", False)

    from src.registro import registrar_lote
    detecciones = [
        ("Feliz", 95.0, "img1.jpg"),
        ("Triste", 80.0, "img2.jpg"),
        ("Neutral", 50.0, "=cmd|' /C calc'!A0")
    ]
    registrar_lote(detecciones)

    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 4  # Header + 3 rows
        # Check first row
        assert reader[1][1] == "img1.jpg"
        assert reader[1][2] == "Feliz"
        assert reader[1][3] == "95.00"
        # Check second row
        assert reader[2][1] == "img2.jpg"
        assert reader[2][2] == "Triste"
        assert reader[2][3] == "80.00"
        # Check formula injection sanitization in third row
        assert reader[3][1] == "'=cmd|' /C calc'!A0"
        assert reader[3][2] == "Neutral"
        assert reader[3][3] == "50.00"

def test_registrar_lote_empty(tmp_path, monkeypatch):
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)
    monkeypatch.setattr("src.registro._csv_inicializado", False)

    from src.registro import registrar_lote
    registrar_lote([])

    # Ensure no file is created when detections list is empty
    assert not test_csv.exists()

    registros = [
        ("Feliz", 95.0, "img1.jpg"),
        ("Triste", 80.5, "img2.jpg"),
        ("Neutral", 50.0, "=cmd|' /C calc'!A0")
    ]

    registrar_lote(registros)

    assert test_csv.exists()
    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 4 # Header + 3 rows
        assert reader[0] == ["timestamp", "origen", "emocion", "confianza"]

        # Row 1
        assert reader[1][1] == "img1.jpg"
        assert reader[1][2] == "Feliz"
        assert reader[1][3] == "95.00"

        # Row 2
        assert reader[2][1] == "img2.jpg"
        assert reader[2][2] == "Triste"
        assert reader[2][3] == "80.50"

        # Row 3 (injection defense)
        assert reader[3][1] == "'=cmd|' /C calc'!A0"
        assert reader[3][2] == "Neutral"
        assert reader[3][3] == "50.00"
def test_registrar_formula_injection_whitespace(tmp_path, monkeypatch):
    test_csv = tmp_path / "test_registro.csv"
    monkeypatch.setattr("src.registro._RUTA_CSV", test_csv)
    monkeypatch.setattr("src.registro._DIR_DATA", tmp_path)
    monkeypatch.setattr("src.registro._csv_inicializado", False)

    malicious_origens = [
        " =cmd|' /C calc'!A0",
        "  +1-1",
        "\t-1+1",
        " \t @SUM(1+1)"
    ]

    for origen in malicious_origens:
        registrar("Neutral", 50.0, origen=origen)

    with open(test_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 5 # Header + 4 rows
        for i, origen in enumerate(malicious_origens, start=1):
            assert reader[i][1] == f"'{origen}"
