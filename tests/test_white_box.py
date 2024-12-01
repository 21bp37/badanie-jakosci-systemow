import pytest
from unittest import mock

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QApplication, QPushButton

from main import UI  # Przykład z Twoją klasą UI


@pytest.fixture
def test_ui(qtbot):
    """Fixture przygotowujące aplikację i UI."""
    # Używamy qtbot do automatycznego stworzenia aplikacji
    ui = UI()  # QApplication jest tworzona automatycznie przez qtbot
    qtbot.addWidget(ui)  # Rejestrujemy widget w qtbot
    return ui


def test_ctrl_v_functionality(test_ui, qtbot):
    """Testuje, czy aplikacja reaguje na Ctrl+V."""
    # Mockujemy komponent content i image_picker
    with mock.patch.object(test_ui.ui.content, "image_picker") as mock_picker:
        mock_picker.paste = mock.MagicMock()  # Zastępujemy paste() mockiem

        # Symulujemy naciśnięcie Ctrl+V
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_V, Qt.ControlModifier)
        test_ui.keyPressEvent(event)

        # Sprawdzamy, czy metoda paste() została wywołana
        mock_picker.paste.assert_called_once()

