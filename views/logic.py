import math

import PIL.ImageQt
from PySide6.QtGui import QPixmap, QColor
from PIL import Image, ImageQt


class ImageData:
    def __init__(self, pixmap: QPixmap) -> None:
        """Initialize ImageData Instance"""
        self.pixmap = pixmap
        self.colors = self.get_colors()  # get image palette

    def get_colors(self) -> list:
        """Gets colors by pixel"""
        # cpu expensive
        original = ImageQt.fromqpixmap(self.pixmap)  # image from QPixmap
        ratio = original.width / original.height
        if original.width > 500:  # reduce image size
            original = original.resize((500, int(500 * ratio)))  # ~ 0.015 per call
        print(f'processing image, reduced size: {original.size}')

        reduced = original.convert("P", palette=PIL.Image.ADAPTIVE)  # ~ 0.054 per call
        # converts color palette

        palette = reduced.getpalette()
        palette = [palette[3 * n:3 * n + 3] for n in range(256)]
        color_count = sorted([(palette[m], n) for n, m in reduced.getcolors()], key=lambda x: x[1],
                             reverse=True)  # sort colors by count
        colors = [i for i, _ in color_count]
        return colors

    @classmethod
    def luminance_color(cls, r: int, g: int, b: int) -> tuple[int, int, int]:
        """Returns color luminance as a rgb tuple (r, g, b)"""
        # todo: reduce calls
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return (248, 248, 248) if luminance <= 0.5 else (0, 0, 0)

    @classmethod
    def invert_color(cls, color: str) -> str:
        """Inverts given color (input: hex), returns hex"""
        table = str.maketrans(
            '0123456789abcdef',
            'fedcba9876543210')
        return color.lower().translate(table).upper()

    @classmethod
    def color_distance(cls, color1: list[int, int, int] | tuple[int, int, int],
                       color2: list[int, int, int] | tuple[int, int, int]) -> float:
        """Calculate weighted distance"""
        r = (color1[0] + color2[0]) * 0.5
        dr = color1[0] - color2[0]
        dg = color1[1] - color2[1]
        db = color1[2] - color2[2]
        return math.sqrt((2 + r * 0.00390625) * (dr ** 2) + 4 * (dg ** 2) + (2 + (255 - r) * 0.00390625) * (db ** 2))

    @property
    def palette(self) -> list:
        """returns image palette"""
        return self.colors

    @property
    def dominant_color(self) -> QColor:
        """Returns dominant color"""
        if not self.colors:
            return QColor()
        return QColor(*self.colors[0])  # unpacks the first color

