import pytest


from views import ImageData
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QUrl
from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QApplication, QPushButton

from PySide6.QtGui import QPixmap, QColor

app = QApplication()

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
    ('./tests/test_image_360x360.png', [[0, 255, 0], [255, 0, 0], [0, 0, 255 ]]),
     
])
def test_imageData_get_colors_pixmap_from_file(imagePath, output):
    pixmap = QPixmap(imagePath)
    assert pixmap.isNull() == False
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