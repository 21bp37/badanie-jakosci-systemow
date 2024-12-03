import pytest
from unittest import mock
from PySide6.QtWidgets import QFileDialog

from PySide6 import QtWidgets, QtCore, QtGui
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


def test_color_update_on_image_load(test_ui):
    test_image_path = "test_image_360x360.png"
    url = QUrl.fromLocalFile(test_image_path)
    event = mock.MagicMock()
    event.mimeData().hasUrls.return_value = True
    event.mimeData().urls.return_value = [url]
    image_picker = test_ui.ui.content.image_picker
    image_picker.dropEvent(event)
    selected_color = test_ui.ui.content.color_picker.picked_color.painted

    assert selected_color is True


def test_color_palette_update_on_image_load(test_ui):
    test_image_path = "test_image_360x360.png"
    url = QUrl.fromLocalFile(test_image_path)
    event = mock.MagicMock()
    event.mimeData().hasUrls.return_value = True
    event.mimeData().urls.return_value = [url]
    image_picker = test_ui.ui.content.image_picker
    image_picker.dropEvent(event)
    for widget in test_ui.ui.content.color_palette.widgets:
        assert widget.painted is True


def test_invalid_file_drag_and_drop_memory(test_ui):
    import io
    invalid_file_content = b"plik nie obraz"
    invalid_file = io.BytesIO(invalid_file_content)
    invalid_file.name = "invalid_file.txt"
    url = QUrl.fromLocalFile(invalid_file.name)
    event = mock.MagicMock()
    event.mimeData().hasUrls.return_value = True
    event.mimeData().urls.return_value = [url]
    with mock.patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        test_ui.ui.content.image_picker.dropEvent(event)
        assert test_ui.ui.content.image_picker.pixmap is None


def test_button_click(test_ui, qtbot):
    button = test_ui.ui.content.image_picker.image_button
    with mock.patch.object(QFileDialog, "getOpenFileName", return_value=("test_image.png", "")) as mock_dialog:
        qtbot.mouseClick(button, QtCore.Qt.LeftButton)
        mock_dialog.assert_called_once()