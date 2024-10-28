import logging
from PySide6 import QtGui, QtCore
from PySide6.QtCore import QRect, Signal, Slot, QObject, QEvent
from PySide6.QtGui import QPainter, QPaintEvent, QPixmap, QImage, QResizeEvent, QColor, QFontMetrics, \
    QMouseEvent, QCursor, QPen, QEnterEvent, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, \
    QGridLayout, QGraphicsDropShadowEffect, \
    QStyleOption, QStyle, QWidget, QVBoxLayout, QApplication, QLabel, QFileDialog, QPushButton
from PIL import Image, ImageQt
from views.logic import ImageData


class Header(QWidget):
    def __init__(self, parent: QObject = None, *args, **kwargs) -> None:
        super(Header, self).__init__(parent=parent, *args, **kwargs)
        self.setMinimumHeight(50)
        self.setMaximumHeight(50)
        self.__set_shadow()

    def __set_shadow(self, blur: float = 8) -> None:
        """Sets header shadow"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 0)
        shadow.setBlurRadius(blur)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        It's recommended to reimplement paintEvent()
        A paint event is a request to repaint all or part of a widget.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.end()


class Communicate(QObject):
    """Communication between widgets"""
    speak = Signal(type(QPixmap))

    def __init__(self, parent: QObject = None) -> None:
        super(Communicate, self).__init__(parent=parent)


class ColorPicker(QWidget):

    def __init__(self, parent: QObject = None, **kwargs) -> None:
        """Initialize widget"""
        super(ColorPicker, self).__init__(parent=parent, **kwargs)

        self.picked_color_widget = QWidget(self)

        self.picked_color = ColorWidget(self.picked_color_widget)  # picked color widget
        self.picked_color.setObjectName('pickedColor')
        self.picked_color.setCursor(QtCore.Qt.PointingHandCursor)
        self.picked_color.helper_size = 10

        self.color_label = QLabel(self.picked_color_widget)  # static text
        self.color_label.setText('Color')
        self.color_label.setAlignment(QtCore.Qt.AlignCenter)

        self.name_label = QLabel(self.picked_color_widget)  # color name label
        self.name_label.setObjectName('pickedColorLabel')
        self.name_label.setText('')
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setMaximumHeight(30)
        self.name_label.setMinimumHeight(30)

        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.addWidget(self.picked_color_widget)

        self.picked_color_layout = QVBoxLayout(self.picked_color_widget)
        self.picked_color_layout.setContentsMargins(0, 0, 0, 0)
        self.picked_color_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.picked_color_layout.addWidget(self.color_label)
        self.picked_color_layout.addWidget(self.picked_color)
        self.picked_color_layout.addWidget(self.name_label)

        self.__set_size_policy()

    def __set_size_policy(self):
        """Sets layout size policy"""
        self.setMaximumWidth(300)
        self.setMinimumWidth(120)
        self.widget_layout.setSpacing(0)
        self.picked_color_layout.setSpacing(4)
        self.picked_color_layout.setContentsMargins(0, 0, 0, 0)

    def update_color(self, r: int, g: int, b: int) -> None:
        """Update picked color"""
        from views.colors import COLORS
        self.picked_color.set_color(QColor(r, g, b))
        self.picked_color.painted = True
        color_diffs = {}
        for key, color in COLORS.items():  # lot of iterations O(n)
            color_diffs[key] = ImageData.color_distance((r, g, b), color)
        self.name_label.setText(min(color_diffs, key=color_diffs.get).title())

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Resize event"""
        super().resizeEvent(event)
        w = int(self.picked_color_widget.width() - 24)
        self.picked_color.setMinimumSize(w, min(w, self.height() - 90))  # keep scale and/or prevent overflow
        self.picked_color.setMaximumSize(w, min(w, self.height() - 90))

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        It's recommended to reimplement paintEvent()
        A paint event is a request to repaint all or part of a widget.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.end()


class ImagePicker(QWidget):
    pick = Signal(type(QColor))  # color pick signal

    # signals have to be defined as a class variable.

    def __init__(self, parent: QObject = None, **kwargs) -> None:
        super(ImagePicker, self).__init__(parent=parent, **kwargs)
        """Initialize class instance"""
        self.setAcceptDrops(True)  # accepts file drops.
        self.setMouseTracking(True)  # allows receiving mouse position
        self._pixmap = None
        self.widget_layout = QGridLayout(self)
        self.sgn = Communicate()
        self.pixmap_coordinates = [[0, 0], [0, 0]]

        """Image button"""
        self.image_button = QPushButton(self)
        self.image_button.setText('Upload file')
        self.image_button.setEnabled(True)
        self.image_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        """Lambda function is used here to not execute that method on init.
        Connects button release with given method.
        """
        self.image_button.released.connect(lambda: self.image_button_function())
        # self.widget_layout.addWidget(self.image_button) # it's whatever
        self.setStyleSheet('border-color: rgba(152,152,152,255);')

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept file"""
        if event.mimeData().hasUrls() or event.mimeData().hasImage:
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            """Drop event has image 'link' so we are able to use load_image() method"""
            for url in event.mimeData().urls():
                img = url.toLocalFile()
                if self.load_image(img):  # return true on first image file that was found
                    break

    def paste(self) -> None:
        """Gets pasted image from clipboard."""
        clipboard = QApplication.clipboard()
        md = clipboard.mimeData()
        if md.hasImage():
            """Since md.hasImage() gets a pixmap using other way, we can't use load_image() method."""
            img = QImage(md.imageData())
            if not img.isNull():
                # Qt can't handle properly cropped image w/ windows snipping tool (visual bug)
                self.pixmap = QPixmap().fromImage(img)
                self.sgn.speak.emit(self.pixmap)  # emit picked pixmap
                self.repaint()
                return
        if md.hasUrls():
            """However we can use load_image() method when clipboard holds a 'link' to the image."""
            for url in md.urls():
                img = url.toLocalFile()
                if self.load_image(img):
                    break

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Pick color on mouse release"""
        super().mouseReleaseEvent(event)
        # return if there's no pixmap or event wasn't caused by mouse left click
        if not self.pixmap:
            return
        if event.button() != QtCore.Qt.LeftButton:
            return
        x = event.localPos().x()
        y = event.localPos().y()
        x1, y1 = self.pixmap_coordinates[0]
        x2, y2 = self.pixmap_coordinates[1]
        if x1 < x < x2 and y1 < y < y2:  # check if a click was within the pixmap coordinates
            pixmap = QPixmap(self.width(), self.height())
            self.render(pixmap)
            image = pixmap.toImage()
            color = image.pixelColor(x, y)
            self.pick.emit(color)  # Emits picked color

    def image_button_function(self) -> None:
        """Image button"""
        data = QFileDialog.getOpenFileName(self, 'Select an image', '', 'Image files (*.jpg *.png *.svg *.gif)')
        if data:
            path = data[0]
            self.load_image(path)

    def load_image(self, url: str) -> bool:
        """Method that handles image upload"""
        try:
            with Image.open(url) as im:
                """Pill Image verify"""
                im.verify()
            with Image.open(url) as im:
                """If transpose fails throws an exception
                An additional method to check if image file is ok
                """
                im.transpose(Image.FLIP_LEFT_RIGHT)
                img_qt = ImageQt.ImageQt(im)
                self.pixmap = QPixmap().fromImage(img_qt)
                self.sgn.speak.emit(self.pixmap)  # emit signal that contains pixmap (to get color palette, etc.)
                self.repaint()  # repaint event draws loaded pixmap
                return True
        except Exception as e:
            # PIL.UnidentifiedImageError
            logging.exception(e)
            return False

    @property
    def pixmap(self) -> QPixmap:
        """returns QPixmap"""
        return self._pixmap

    @pixmap.setter
    def pixmap(self, value: QPixmap) -> None:
        """Update stylesheet on image upload
            (Remove borders)
        """
        self._pixmap = value
        if self._pixmap is None:
            self.setStyleSheet('border-color: rgba(152,152,152,255);')
            return
        self.setStyleSheet('border-color: rgba(152,152,152,0);')

    def paintEvent(self, event: QPaintEvent) -> None:
        # cpu expensive
        # todo: improve performance (nie chce mi sie robic tych todo tbh)
        """
        It's recommended to reimplement paintEvent()
        A paint event is a request to repaint all or part of a widget.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        if self.pixmap is None:
            # browse a file stuff
            # if there is no pixmap uploaded
            if not self.image_button.isVisible():
                self.image_button.setVisible(True)
                self.image_button.setEnabled(True)
            metrics = QFontMetrics(self.font())
            height = metrics.height()
            painter.setPen(QPen(QColor(0, 0, 0, 255)))
            text = f'Drag an image here\n— or —\nselect an image from your computer'
            text = metrics.elidedText(text,
                                      QtCore.Qt.ElideRight, self.width() - 12)
            painter.drawText(QRect(0, int((self.height() - height * 3) * 0.5), self.width(), height * 3), 133, text)
            self.image_button.move(int((self.width() - self.image_button.width()) * 0.5),
                                   int((self.height() + height * 3) * 0.5) + 8)  # moves image button to the center
            painter.end()
            return
        if self.image_button.isVisible():
            self.image_button.setEnabled(False)
            self.image_button.setVisible(False)
        w, h = self.pixmap.size().width(), self.pixmap.size().height()
        if w == 0 or h == 0:
            painter.end()
            return
        ratio = w / h
        height_scaled = max(self.height(), h) if h <= self.height() else min(self.height(), h)
        width_scaled = height_scaled * ratio
        if width_scaled > self.width():  # scale if pixmap's width is greater than widget's width
            width_scaled = self.width()  # set pixmap's width to 100% of available space
            height_scaled = width_scaled * 1 / ratio
        y0 = abs(self.height() - height_scaled) * 0.5
        x0 = abs(self.width() - width_scaled) * 0.5
        _pixmap = self.pixmap.scaled(width_scaled, height_scaled, QtCore.Qt.KeepAspectRatio,
                                     QtCore.Qt.SmoothTransformation)  # scale pixmap
        painter.drawPixmap(QRect(x0, y0, width_scaled, height_scaled), _pixmap)  # draw pixmap (image)

        """Get pixmap position (2x2 matrix) [(x0,y0),(x1,y1)]"""
        self.pixmap_coordinates = [[int(x0), int(y0)], [int(x0 + width_scaled), int(y0 + height_scaled)]]

        painter.end()


class ColorWidget(QWidget):
    def __init__(self, parent: QObject = None, **kwargs) -> None:
        super(ColorWidget, self).__init__(parent=parent, **kwargs)
        """Initialize ColorWidget"""
        self.painted = False
        self.text_color = QColor(0, 0, 0, 255)
        self.background = self.palette().base().color().name()
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.copy_text = ''

        self.helper_size = 8

    def set_color(self, color: QColor) -> None:
        """Set background color"""
        self.text_color = QColor(color.fromRgb(*ImageData.luminance_color(color.red(), color.green(), color.blue())))
        self.setStyleSheet(f'background-color: {color.name(QColor.HexRgb)}')
        self.background = self.palette().base().color().name()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.copy_text = 'Click to copy'
        self.repaint()

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self.copy_text = ''
        self.repaint()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.background, mode=cb.Clipboard)
        self.copy_text = 'Copied!'
        self.repaint()

    def paintEvent(self, event: QPaintEvent) -> None:
        # todo: improve performance (cpu expensive)
        """
        It's recommended to reimplement paintEvent()
        A paint event is a request to repaint all or part of a widget.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        if self.painted:
            metrics = QFontMetrics(self.font())
            height = metrics.height()  # line height by current font
            hex_text = metrics.elidedText(str(self.background),
                                          QtCore.Qt.ElideRight, self.width() - 12)
            rgb_text = metrics.elidedText(str(tuple(int(self.background.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))),
                                          QtCore.Qt.ElideRight, self.width())
            # text color based on luminance
            painter.setPen(self.text_color)
            # or text color by invert background color:
            # painter.setPen(ImageData.invert_color(self.palette().base().color().name()))

            painter.drawText(QRect(0, 1, self.width(), height + 1), 133, hex_text)
            font = self.font()
            font.setPointSize(self.helper_size)
            metrics = QFontMetrics(font)
            height = metrics.height()
            painter.setFont(font)
            painter.drawText(QRect(0, self.height() - 4 - height, self.width(), height + 4), 133, rgb_text)
            copy_text = metrics.elidedText(self.copy_text, QtCore.Qt.ElideRight, self.width() - 2)
            painter.setOpacity(0.85)
            painter.drawText(QRect(0, int(self.height() * 0.5) - height + 4, self.width(), height + 4), 133, copy_text)
        # 133 == int(QtCore.Qt.AlignCenter | QtCore.Qt.AlignLeft)
        painter.end()


class ColorPalette(QWidget):
    def __init__(self, parent: QObject = None, **kwargs) -> None:
        super(ColorPalette, self).__init__(parent=parent, **kwargs)
        """Initialize ColorPalette"""
        self.setMaximumHeight(128)
        self.setMinimumHeight(68)
        self.palette_label = QLabel(self)
        self.palette_label.setText('Color Palette')
        self.palette_label.setAlignment(QtCore.Qt.AlignCenter)
        self.palette_label.setMaximumHeight(20)
        self.palette_widget = QWidget(self)

        """Add Layout"""
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 4)
        self.widget_layout.setSpacing(0)
        self.widget_layout.addWidget(self.palette_label)
        self.widget_layout.addWidget(self.palette_widget)

        self.palette_layout = QHBoxLayout(self.palette_widget)
        self.palette_layout.setContentsMargins(0, 0, 0, 4)

        """Color Palette Widgets"""
        self.widgets = [ColorWidget(self.palette_widget) for _ in range(7)]
        for widget in self.widgets:
            self.palette_layout.addWidget(widget)
            self.palette_layout.setAlignment(QtCore.Qt.AlignCenter)
            self.palette_layout.setSpacing(4)

    def paint_widgets(self, colors: list[list]) -> None:
        """
        A method that is called on image upload
        Sets widgets background-colors to most common colors.
        """
        for i, widget in enumerate(self.widgets):
            widget.painted = True
            color = QColor(*colors[min(i, len(colors) - 1)])
            widget.set_color(color)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """A method that is called on resize event"""
        super().resizeEvent(event)
        h = max(int(self.height() * 0.65), 58)  # get size
        h = min(h, (self.width() - 32) // 7)  # prevent overflow

        for widget in self.widgets:
            """Keep widget's aspect ratio (1:1)"""
            widget.setMaximumSize(h, h)
            widget.setMinimumSize(h, h)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        It's recommended to reimplement paintEvent()
        A paint event is a request to repaint all or part of a widget.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)

        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.end()


class Content(QWidget):
    def __init__(self, parent: QObject = None, *args, **kwargs) -> None:
        super(Content, self).__init__(parent=parent, *args, **kwargs)
        """Initialize widgets"""
        self.widget_layout = QVBoxLayout(self)
        self.widget_top = QWidget(self)
        self.widget_top.layout = QHBoxLayout(self.widget_top)
        self.image_picker = ImagePicker(self.widget_top)
        self.color_picker = ColorPicker(self.widget_top)
        self.widget_top.layout.addWidget(self.image_picker)
        self.widget_top.layout.addWidget(self.color_picker)

        """Layout size policy"""
        self.color_palette = ColorPalette(self)  # color palette
        self.widget_layout.addWidget(self.widget_top)
        self.widget_layout.addWidget(self.color_palette)
        self.__set_size_policy()

        """Signals"""
        # false positive warning
        self.image_picker.sgn.speak.connect(self.set_colors)  # PyCharm cannot find reference (PyCharm's fault)
        self.image_picker.pick.connect(self.pick_color)

    @Slot(type(QColor))
    def pick_color(self, color: QColor):
        """Slot that is responsible for picked color"""
        rgb = color.red(), color.green(), color.blue()
        self.color_picker.update_color(*rgb)  # update picked color

    @Slot(type(QPixmap))
    def set_colors(self, pixmap: QPixmap) -> None:
        """Slot that is responsible for color update on image upload"""
        image_data = ImageData(pixmap)  # todo: class variable instead
        palette = image_data.palette  # get image palette
        self.color_palette.paint_widgets(palette)  # update color palette
        r, g, b = palette[0]  # get the most common color
        self.color_picker.update_color(r, g, b)  # set picked color to most common one

    def __set_size_policy(self):
        """sets size policy"""
        vertical_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        vertical_policy.setVerticalStretch(70)

        self.widget_top.setSizePolicy(vertical_policy)

        vertical_policy.setVerticalStretch(30)
        self.color_palette.setSizePolicy(vertical_policy)
        # 70:30 proportion

        horizontal_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        horizontal_policy.setHorizontalStretch(75)  # 75:25 proportion

        self.image_picker.setSizePolicy(horizontal_policy)

        horizontal_policy.setHorizontalStretch(25)
        self.color_picker.setSizePolicy(horizontal_policy)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Reimplement paintEvent() method
        It's recommended to reimplement paintEvent()
        A paint event is a request to repaint all or part of a widget.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.end()


class UiMainWindow(QWidget):
    def __init__(self, parent: QObject = None, **kwargs) -> None:
        super(UiMainWindow, self).__init__(parent=parent, **kwargs)
        """Initialize UiMainWindow class instance"""
        self.widget_layout = QVBoxLayout(self)

        self.header = Header(self)
        self.content = Content(self)

        self.widget_layout.addWidget(self.header)
        self.widget_layout.addWidget(self.content)

        self.__set_size_policy()
        self.__set_style_sheet()

    def __set_style_sheet(self) -> None:
        """A method that applies custom style sheet."""
        with open('./assets/qss/style.qss', 'r', encoding='utf-8') as qss:
            self.setStyleSheet(qss.read())

    def __set_size_policy(self) -> None:
        """Sets widget size policy"""
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(0)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Re-implement paintEvent method"""
        try:
            opt = QStyleOption()
            opt.initFrom(self)
            painter = QPainter(self)
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
            painter.end()
        except KeyboardInterrupt:
            return
