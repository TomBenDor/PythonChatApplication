import re

from PyQt5.QtGui import QValidator


class NameValidator(QValidator):
    def validate(self, string, pos):
        if not re.fullmatch("([A-Za-z]+ ?)*", string):
            return QValidator.Invalid, string, pos
        return QValidator.Acceptable, string.title(), pos
