import pytest
from unittest import mock
from PySide6.QtWidgets import QFileDialog

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QUrl, QPoint
from PySide6.QtGui import QKeyEvent, Qt, QColor
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QPixmap

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import UI  # Przykład z Twoją klasą UI


@pytest.fixture
def test_ui(qtbot) -> 'UI':
    """Fixture przygotowujące aplikację i UI."""
    # Używamy qtbot do automatycznego stworzenia aplikacji
    ui = UI()  # QApplication jest tworzona automatycznie przez qtbot
    qtbot.addWidget(ui)  # Rejestrujemy widget w qtbot
    return ui


def test_zoom_button_ui_change(test_ui, qtbot):
    button = test_ui.ui.content.zoom_image.zoom
    qtbot.mouseClick(button, Qt.LeftButton)
    assert button.clicked_zoom is True


def test_zoom_button_ui_change_back(test_ui, qtbot):
    button = test_ui.ui.content.zoom_image.zoom
    qtbot.mouseClick(button, Qt.LeftButton)
    qtbot.mouseClick(button, Qt.LeftButton)
    assert button.clicked_zoom is False


def test_zoom_button_ui_image_displayed(test_ui, qtbot):
    button = test_ui.ui.content.zoom_image.zoom
    qtbot.mouseClick(button, Qt.LeftButton)
    event = mock.MagicMock()
    test_ui.ui.content.zoom_image.paintEvent(event)
    target_image = QPixmap("assets/Zoom_in_clicked.png")
    target_image = target_image.scaled(100, 85).toImage()
    image = test_ui.ui.content.zoom_image.image.toImage()
    assert image == target_image


def test_zoom_button_ui_image_displayed_back(test_ui, qtbot):
    button = test_ui.ui.content.zoom_image.zoom
    qtbot.mouseClick(button, Qt.LeftButton)
    qtbot.mouseClick(button, Qt.LeftButton)
    event = mock.MagicMock()
    test_ui.ui.content.zoom_image.paintEvent(event)
    target_image = QPixmap("assets/Zoom_in_not_clicked.png")
    target_image = target_image.scaled(100, 85).toImage()
    image = test_ui.ui.content.zoom_image.image.toImage()
    assert image == target_image


def test_zoom_pixel_value(test_ui, qtbot):
    test_image_path = "tests/gradient.png"
    # Create widgets
    image_picker = test_ui.ui.content.image_picker
    image_picker.show()
    color_widget = test_ui.ui.content.color_picker.picked_color

    # Load and draw image
    image_picker.load_image(test_image_path)
    event = mock.MagicMock()
    image_picker.paintEvent(event)

    # Calculate the pixel location to click (e.g., the center of the button)
    x, y = 1, 1
    click_point = QPoint(x, y)

    # Simulate clicking
    qtbot.mouseClick(image_picker, Qt.LeftButton, pos=click_point)
    # Save picked color
    picked_color_b4_zoom = color_widget.text_color
    
    # simulating zoom
    #Zoom button
    button = test_ui.ui.content.zoom_image.zoom
    qtbot.mouseClick(button, Qt.LeftButton)
    # first click to zoom
    qtbot.mouseClick(image_picker, Qt.LeftButton, pos=click_point)
    # secound click to pick color in the same spot
    qtbot.mouseClick(image_picker, Qt.LeftButton, pos=click_point)
    picked_color_after_zoom = color_widget.text_color

    assert picked_color_b4_zoom == picked_color_after_zoom