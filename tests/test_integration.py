import pytest
from unittest import mock
from PySide6.QtWidgets import QFileDialog

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QUrl
from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QApplication, QPushButton

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import UI


@pytest.fixture
def test_ui(qtbot) -> 'UI':
    ui = UI()
    qtbot.addWidget(ui)
    return ui


def test_ctrl_v_functionality(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    with mock.patch.object(test_ui.ui.content, "image_picker") as mock_picker:
        mock_picker.paste = mock.MagicMock()
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_V, Qt.ControlModifier)  # noqa
        test_ui.keyPressEvent(event)
        mock_picker.paste.assert_called_once()


def test_drag_and_drop(test_ui):
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    url = QUrl.fromLocalFile(test_image_path)
    event = mock.MagicMock()
    event.mimeData().hasUrls.return_value = True
    event.mimeData().urls.return_value = [url]
    image_picker = test_ui.ui.content.image_picker
    image_picker.dropEvent(event)
    assert image_picker.pixmap is not None


def test_color_update_on_image_load(test_ui):
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    url = QUrl.fromLocalFile(test_image_path)
    event = mock.MagicMock()
    event.mimeData().hasUrls.return_value = True
    event.mimeData().urls.return_value = [url]
    image_picker = test_ui.ui.content.image_picker
    image_picker.dropEvent(event)
    selected_color = test_ui.ui.content.color_picker.picked_color.painted

    assert selected_color is True


def test_color_palette_update_on_image_load(test_ui):
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
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
    qtbot.wait_exposed(test_ui.ui)
    button = test_ui.ui.content.image_picker.image_button
    with mock.patch.object(QFileDialog, "getOpenFileName", return_value=("test_image.png", "")) as mock_dialog:
        qtbot.mouseClick(button, QtCore.Qt.LeftButton)
        mock_dialog.assert_called_once()


def test_zoom_button_ui_change(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    url = QUrl.fromLocalFile(test_image_path)
    event = mock.MagicMock()
    event.mimeData().hasUrls.return_value = True
    event.mimeData().urls.return_value = [url]
    image_picker = test_ui.ui.content.image_picker
    image_picker.dropEvent(event)
    button = test_ui.ui.content.zoom_image.zoom
    image_before = test_ui.ui.content.image_picker.pixmap.copy()
    qtbot.mouseClick(button, Qt.LeftButton)
    image_after = test_ui.ui.content.image_picker.pixmap.copy()
    assert image_before != image_after
