import pytest
from unittest import mock

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QUrl
from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QApplication, QPushButton

from main import UI  # Przykład z Twoją klasą UI


@pytest.fixture
def test_ui(qtbot) -> 'UI':
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


def test_drag_and_drop(test_ui):
    test_image_path = "test_image_360x360.png"
    url = QUrl.fromLocalFile(test_image_path)
    event = mock.MagicMock()
    event.mimeData().hasUrls.return_value = True
    event.mimeData().urls.return_value = [url]
    image_picker = test_ui.ui.content.image_picker
    image_picker.dropEvent(event)
    assert image_picker.pixmap is not None
