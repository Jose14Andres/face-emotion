import sys
import pytest
from pathlib import Path
from unittest.mock import patch
from src.app import modo_imagen, modo_lote

def test_terminal_escape_injection_modo_imagen_not_found(capsys):
    malicious_path = "\033[31mExploit\033[0m_image.jpg"
    with patch("sys.exit") as mock_exit:
        # Patch sys.exit to raise an exception to stop execution instead of just mocking it to return
        # so that it doesn't continue with None frame reading
        mock_exit.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            modo_imagen(malicious_path)

    captured = capsys.readouterr()
    assert "\033" not in captured.out
    assert repr(malicious_path) in captured.out

def test_terminal_escape_injection_modo_lote_not_found(capsys):
    malicious_path = "\033[31mExploit\033[0m_folder"
    with patch("sys.exit") as mock_exit:
        mock_exit.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            modo_lote(malicious_path)

    captured = capsys.readouterr()
    assert "\033" not in captured.out
    assert repr(malicious_path) in captured.out
