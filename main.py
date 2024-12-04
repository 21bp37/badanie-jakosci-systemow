from PySide6 import QtGui
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import QApplication, QMainWindow
import sys  # import sus
from views import UiMainWindow

import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)


class UI(QMainWindow):
    def __init__(self, app=None, *args, **kwargs) -> None:
        super(UI, self).__init__(*args, **kwargs)
        self.setWindowTitle("apka")
        self.setWindowIcon(QIcon("./assets/images/icon3.png"))
        if app:
            size = app.primaryScreen().size() * 0.6
            self.resize(size)
        self.setMinimumSize(620, 344)
        self.ui:'UiMainWindow' = UiMainWindow(self)
        self.setCentralWidget(self.ui)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        super().keyPressEvent(event)
        if event.matches(QtGui.QKeySequence.Paste):
            print('Paste ui')
            self.ui.content.image_picker.paste()

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        print('mousePressEvent')
        # print(ev.pos())

def main():
    app = QApplication(sys.argv)
    ui = UI(app)
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
