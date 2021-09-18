import os

from PyQt5 import QtGui

colors = {'red': '#E02828', 'blue': '#2d8cff', 'gray': '#747487', 'black': '#414155'}


def entry_style(error=False):
    return f"""
        QLineEdit {{
            color: {colors['black']};
            border-radius: 10px;
            border-style: outset;
            border-width: 1px;
            border-color: {colors['red' if error else 'gray']};
        }}
        QLineEdit:focus {{border-color: {colors['red' if error else 'blue']}}}
"""


button_style = """
        QPushButton {
            background-color:  #0E71EB;
            border-radius: 10px;
            padding: 6px;
            color: white;
            font: bold 14px;
        }
        QPushButton:disabled {
            background-color: #E4E4ED;
            color: #BABACC;
        }
        QPushButton:hover  {
            background-color: #2681F2
        }
        QPushButton:pressed  {
            background-color: #0C63CE
        }
"""

text_button_style = f"""
        QPushButton {{
            background-color:  white;
            border-radius: 10px;
            padding: 6px;
            color: {colors['blue']};
            font: bold 14px;
        }}
        QPushButton:disabled {{
            background-color: white;
            color: #BABACC;
        }}
        QPushButton:hover  {{
            background-color: #E7F1FD;
            color: #2681F2;
            font: 14px;
        }}
        QPushButton:pressed  {{
            background-color: #D7E6F9;
            color: #0C63CE;
        }}
"""

default_button_style = f"""
        QPushButton {{
            background-color:  white;
            border: 1px solid #747487;
            border-radius: 10px;
            padding: 6px;
            color: {colors['black']};
        }}
        QPushButton:disabled {{
            border: 0px;
            background-color: #E4E4ED;
            color: #BABACC
        }}
        QPushButton:hover  {{
            background-color: #F6F7F9;
        }}
        QPushButton:pressed  {{
            background-color: #E4E4ED;
        }}
"""

list_style = f"""
        QListWidget {{
            background-color: transparent;
            border: 1px solid;
            border-color: {colors['gray']} none none none;
            outline: none;
        }}
        QListWidget::item:selected {{
            background : #5B86E5;
        }}
        QListWidget::item:hover:!selected {{
            background : rgba(200, 200, 200, 100);
        }}
"""

main_frame_style = f"""
    QFrame#frame {{
        background-color: qlineargradient( x1:0 y1:0, x2:1 y2:1, stop:0 #36D1DC, stop:1 #5B86E5);
        border: 1px solid;
        border-color: none none none {colors['gray']};
    }}
"""


def get_font(size: int, bold: bool, font="Lato") -> QtGui.QFont:
    for file in os.listdir('fonts/Lato'):
        QtGui.QFontDatabase.addApplicationFont(f"fonts/Lato/{file}")

    font = QtGui.QFont(font)
    font.setPixelSize(size)
    font.setBold(bold)

    return font
