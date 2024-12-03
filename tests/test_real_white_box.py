import os
from unittest import mock

import pytest

from main import UI
from views import ImageData
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QUrl, QMimeData, QPoint, QEvent
from PySide6.QtGui import QKeyEvent, Qt, QDragEnterEvent, QImage, QMouseEvent, QEnterEvent
from PySide6.QtWidgets import QApplication, QPushButton

from PySide6.QtGui import QPixmap, QColor

app = QApplication()


# app.setAttribute(Qt.AA_DisableHighDpiScaling)
# app.setAttribute(Qt.AA_UseSoftwareOpenGL)
# app.setQuitOnLastWindowClosed(False)

@pytest.fixture
def test_ui(qtbot) -> 'UI':
    ui = UI()
    qtbot.addWidget(ui)
    ui.setVisible(False)

    # Optional: Set the attribute to allow painting in memory
    ui.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    # Show the window in memory (does not display on screen)
    ui.show()
    return ui


@pytest.mark.parametrize("r, g, b", [
    (0, 0, 0),
    (255, 255, 255),
    (0, 0, 255),
    (81, 67, 125)
])
def test_imageData_get_colors_single_color_pixmap(r, g, b):
    pixmap = QPixmap(400, 400)
    pixmap.fill(QColor(r, g, b))
    imageData = ImageData(pixmap)
    colors = imageData.get_colors()
    assert len(colors) == 1
    assert colors[0] == [r, g, b]


@pytest.mark.parametrize("imagePath, output", [
    ('./tests/test_image_360x360.png', [[0, 255, 0], [255, 0, 0], [0, 0, 255]]),

])
def test_imageData_get_colors_pixmap_from_file(imagePath, output):
    pixmap = QPixmap(imagePath)
    assert pixmap.isNull() is False
    imageData = ImageData(pixmap)
    colors = imageData.get_colors()
    assert len(colors) == len(output)
    for color in zip(colors, output):
        assert color[0] == color[1]


@pytest.mark.parametrize("input, output", [
    ('000000', 'FFFFFF'),
    ('012345', 'FEDCBA'),
    ('798650', '8679AF'),
    ('', ''),
    ('0', 'F'),
    ('FFFFFFFFFFFF', '000000000000'),
])
def test_imageData_get_colors_pixmap_from_file(input, output):
    inversedInput = ImageData.invert_color(input)
    assert inversedInput == output

    inversedOutput = ImageData.invert_color(output)
    assert inversedOutput == input


@pytest.mark.parametrize(
    "r, g, b, output",
    [
        (0, 0, 0, (248, 248, 248)),
        (255, 255, 255, (0, 0, 0)),
        (200, 200, 200, (0, 0, 0)),
        (50, 50, 50, (248, 248, 248)),
        (100, 149, 237, (0, 0, 0)),
        (240, 128, 128, (0, 0, 0)),
        (0, 128, 128, (248, 248, 248)),
    ],
)
def test_luminance_color(r, g, b, output):
    result = ImageData.luminance_color(r, g, b)
    assert result == output


def test_load_image(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    assert test_ui.ui.content.image_picker.load_image("unknown_path") is False
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_palette.png")
    assert test_ui.ui.content.image_picker.load_image(test_image_path) is True
    test_image_path = os.path.join(os.path.dirname(__file__), "not_a_file.txt")
    assert test_ui.ui.content.image_picker.load_image(test_image_path) is False
    test_image_path = os.path.join(os.path.dirname(__file__), "test_real_white_box.py")
    assert test_ui.ui.content.image_picker.load_image(test_image_path) is False


def test_image_size(test_ui, qtbot):
    from PIL import Image
    import io
    import tempfile
    wide_image = Image.new("RGB", (1000, 5), "red")

    # Generowanie obrazu "wąskiego, ale wysokiego"
    tall_image = Image.new("RGB", (5, 1000), "blue")

    # Zapisz obrazy do pamięci w formacie PNG
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        wide_image.save(temp_file, format="PNG")
        wide_image_path = temp_file.name  # Ścieżka do tymczasowego pliku

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        tall_image.save(temp_file, format="PNG")
        tall_image_path = temp_file.name  # Ścieżka do tymczasowego pliku

    # Testowanie funkcji load_image z wczytanym obrazem
    assert test_ui.ui.content.image_picker.load_image(wide_image_path) is True
    assert test_ui.ui.content.image_picker.load_image(tall_image_path) is True

    # Po wykonaniu testu możesz usunąć tymczasowe pliki (jeśli nie potrzebujesz ich później)
    os.remove(wide_image_path)
    os.remove(tall_image_path)


def test_image_color(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_palette.png")
    test_image_path = test_image_path
    test_ui.ui.content.image_picker.load_image(test_image_path)
    assert test_ui.ui.content.color_picker.picked_color.background == "#008000"


@pytest.mark.parametrize("width, height", [
    (100, 100),
    (621, 345),
    (2137, 2137),
    (621, 3232),
    (3232, 432),
])
def test_resize(test_ui, width, height):
    test_ui.resize(width, height)
    assert test_ui.size().width() == max(620, width)
    assert test_ui.size().height() == max(344, height)


def test_drag_enter_event(test_ui, qtbot):
    mime_data = QMimeData()
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_palette.png")
    url = QUrl.fromLocalFile(test_image_path)
    mime_data.setUrls([url])
    event = QDragEnterEvent(QPoint(1, 1), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    test_ui.ui.content.image_picker.dragEnterEvent(event)
    assert event.isAccepted()
    with mock.patch.object(test_ui.ui.content.image_picker, "dragEnterEvent") as mock_drag_event:
        test_ui.ui.content.image_picker.dragEnterEvent(event)
        mock_drag_event.assert_called_once_with(event)


def test_paste_event(test_ui, qtbot):
    mime_data = QMimeData()
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_palette.png")
    url = QUrl.fromLocalFile(test_image_path)
    mime_data.setUrls([url])
    event = QDragEnterEvent(QPoint(1, 1), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    test_ui.ui.content.image_picker.dragEnterEvent(event)
    assert event.isAccepted()
    with mock.patch.object(test_ui.ui.content.image_picker, "dragEnterEvent") as mock_drag_event:
        test_ui.ui.content.image_picker.dragEnterEvent(event)
        mock_drag_event.assert_called_once_with(event)


def test_paste_image_from_clipboard(test_ui, qtbot):
    image_picker = test_ui.ui.content.image_picker
    image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    image = QImage(image_path)
    clipboard = QApplication.clipboard()
    clipboard.setImage(image)
    event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_V, Qt.ControlModifier)
    test_ui.keyPressEvent(event)
    assert image_picker.pixmap is not None
    assert image_picker.pixmap.toImage() == image


def test_paste_image_from_url(test_ui, qtbot):
    image_picker = test_ui.ui.content.image_picker
    image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    url = QUrl.fromLocalFile(image_path)
    clipboard = QApplication.clipboard()
    mime_data = QMimeData()
    mime_data.setUrls([url])
    clipboard.setMimeData(mime_data)
    # clipboard.mimeData().setUrls([image_path])
    event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_V, Qt.ControlModifier)
    test_ui.keyPressEvent(event)
    assert image_picker.pixmap is not None
    assert image_picker.pixmap.toImage() == QImage(image_path)


def test_image_zoom(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    test_ui.ui.content.image_picker.load_image(test_image_path)
    zoom_btn = test_ui.ui.content.zoom_image.zoom
    qtbot.mousePress(zoom_btn, QtCore.Qt.LeftButton)
    qtbot.mouseRelease(zoom_btn, QtCore.Qt.LeftButton)
    test_ui.ui.content.update()
    test_ui.ui.content.repaint()
    image_picker = test_ui.ui.content.image_picker
    test_ui.ui.content.image_picker.clicked_zoom = True
    point = QPoint(139, 6)
    qtbot.mousePress(image_picker, QtCore.Qt.LeftButton, pos=point)
    qtbot.mouseRelease(image_picker, QtCore.Qt.LeftButton, pos=point)
    test_ui.ui.content.image_picker.zoom_in(point)
    assert test_ui.ui.content.color_picker.picked_color.background == "#ff0000"


def test_image_mouse_none(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    point = QPoint(139, 6)
    event = QMouseEvent(QMouseEvent.MouseButtonRelease, point, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    assert test_ui.ui.content.image_picker.mouseReleaseEvent(event) is None
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    test_ui.ui.content.image_picker.load_image(test_image_path)
    event2 = QMouseEvent(QMouseEvent.MouseButtonRelease, point, Qt.RightButton, Qt.RightButton, Qt.NoModifier)
    assert test_ui.ui.content.image_picker.mouseReleaseEvent(event2) is None


def test_color_hover(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    test_ui.ui.content.image_picker.load_image(test_image_path)
    point = QPoint(1, 1)
    color = test_ui.ui.content.color_picker.picked_color
    colors = test_ui.ui.content.color_palette.widgets
    event = QEnterEvent(
        point,
        point,
        point
    )
    color.enterEvent(event)
    assert color.copy_text == "Click to copy"
    for clr in colors:
        clr.enterEvent(event)
        assert clr.copy_text == "Click to copy"
    event = QEvent(QEvent.Leave)
    color.leaveEvent(event)
    assert color.copy_text == ""
    for clr in colors:
        clr.leaveEvent(event)
        assert clr.copy_text == ""


def test_copy_clipboard(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    test_ui.ui.content.image_picker.load_image(test_image_path)
    color = test_ui.ui.content.color_picker.picked_color
    colors = test_ui.ui.content.color_palette.widgets
    point = QPoint(1, 1)
    event = QMouseEvent(QMouseEvent.MouseButtonRelease, point, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    color.mouseReleaseEvent(event)
    assert color.copy_text == "Copied!"
    assert QApplication.clipboard().text() == "#00ff00"
    for clr in colors:
        event = QMouseEvent(QMouseEvent.MouseButtonRelease, point, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        clr.mouseReleaseEvent(event)
        assert clr.copy_text == "Copied!"
        assert QApplication.clipboard().text() in {"#00ff00", "#ff0000", "#0000ff"}


def test_pick_color(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    picker = test_ui.ui.content.image_picker
    color = test_ui.ui.content.color_picker
    picker.load_image(test_image_path)
    picker.update()
    qtbot.wait_exposed(picker)
    qtbot.addWidget(picker)
    assert color.picked_color.background == "#00ff00"
    point = QPoint(132, 1)
    event = QMouseEvent(QMouseEvent.MouseButtonRelease, point, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    picker.mouseReleaseEvent(event)
    assert color.picked_color.background == "#ff0000"


def test_pick_color_name(test_ui, qtbot):
    qtbot.wait_exposed(test_ui.ui)
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image_360x360.png")
    test_image_path = test_image_path
    picker = test_ui.ui.content.image_picker
    color = test_ui.ui.content.color_picker
    picker.load_image(test_image_path)
    picker.update()
    qtbot.wait_exposed(picker)
    qtbot.addWidget(picker)
    assert color.name_label.text() == "Lime"
    test_image_path = os.path.join(os.path.dirname(__file__), "gradient.png")
    test_image_path = test_image_path
    picker.load_image(test_image_path)
    assert color.name_label.text() == "Darkslategray"
