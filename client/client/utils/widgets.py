import hashlib

from PyQt5 import QtWidgets, QtCore, QtGui

from .styles import get_font, colors, entry_style


class BaseDialog(QtWidgets.QDialog):
    title = None
    size = (400, 300)

    def __init__(self):
        super(BaseDialog, self).__init__()

        self._result = None

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(self.size[0] + 10, self.size[1] + 10)
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(5, 5, *self.size)
        self.frame.setStyleSheet("background-color: white; border-radius: 30px")
        self.frame.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        effect = QtWidgets.QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(0)
        self.frame.setGraphicsEffect(effect)

        self.close_button = QtWidgets.QPushButton(self)
        self.close_button.setIcon(QtGui.QIcon("images/close_button.png"))
        self.close_button.resize(QtCore.QSize(40, 40))
        self.close_button.setGeometry(self.width() - 50, 10, 40, 40)
        self.close_button.setStyleSheet("background-color: transparent")
        self.close_button.clicked.connect(exit)

        self.oldPos = self.pos()

        if self.title:
            self.title_label = QtWidgets.QLabel(self.title, self)
            self.title_label.move(0, 25)
            self.title_label.setFont(get_font(30, False, "Lato Black"))
            self.title_label.setStyleSheet("color: #414155")
            self.title_label.setAlignment(QtCore.Qt.AlignLeft)
            self.title_label.setContentsMargins(25, 5, 10, 5)
            self.title_label.adjustSize()

    def on_enter(self, value):
        for key in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            shortcut = QtWidgets.QShortcut(key, self)
            shortcut.activated.connect(value)

    def typing(self):
        raise NotImplementedError(f"{self.__class__.__name__}.typing() is not implemented!")

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, r):
        self._result = r
        self.close()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
        super(BaseDialog, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        super(BaseDialog, self).mouseMoveEvent(event)


class Entry(QtWidgets.QLineEdit):
    def __init__(self, parent, *,
                 rect,
                 text="",
                 help="",
                 strip=False,
                 max_length=30,
                 echo_mode=0,
                 validator=None,
                 regex=".*",
                 font=16):
        super().__init__(parent)

        self.strip = strip
        self.error = False
        self.help = help

        self.setGeometry(QtCore.QRect(*rect))
        self.setFont(get_font(font, False))
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setTextMargins(10, 5, 10, 5)

        self.setStyleSheet(entry_style())
        self.setPlaceholderText(text)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.label = QtWidgets.QLabel(help, parent)
        self.label.move(rect[0] + 10, rect[1] - 7)
        self.label.setContentsMargins(5, 0, 5, 0)
        self.label.setFont(get_font(12, False))
        self.label.setStyleSheet(f"color: {colors['black']}; background-color: transparent")
        self.label.adjustSize()
        self.label.hide()

        self.setMaxLength(max_length)
        self.setEchoMode(echo_mode)
        if validator:
            self.validator_ = validator(self.parent())
            self.setValidator(self.validator_)
        else:
            self.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(regex)))

        self.textChanged.connect(self.typing)
        self.textChanged.connect(parent.typing)

    @property
    def encrypted(self):
        return hashlib.sha256(self.text().encode()).hexdigest()

    def typing(self):
        self.label.setVisible(len(self.text()) > 0 and len(self.label.text()) > 0)

        if self.error:
            self.hide_error()

    def show_error(self, txt):
        self.setStyleSheet(entry_style(True))
        self.error = True
        self.label.setText(txt)
        self.label.adjustSize()
        self.label.setStyleSheet(f"color: {colors['red']}; background-color: 'white'")
        self.label.setVisible(True)

    def hide_error(self):
        self.setStyleSheet(entry_style(False))
        self.error = False
        self.label.setText(self.help)
        self.label.adjustSize()
        self.label.setStyleSheet(f"color: {colors['blue']}; background-color: 'white'")

    def focusOutEvent(self, a0: QtGui.QFocusEvent) -> None:
        super(Entry, self).focusOutEvent(a0)

        self.label.setStyleSheet(f"color: {colors['red' if self.error else 'black']}; background-color: 'white'")

        if self.strip:
            self.setText(self.text().strip())

    def focusInEvent(self, a0: QtGui.QFocusEvent) -> None:
        super(Entry, self).focusInEvent(a0)

        self.label.setStyleSheet(f"color: {colors['red' if self.error else 'blue']}; background-color: 'white'")
