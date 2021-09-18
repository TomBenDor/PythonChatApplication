from PyQt5 import QtWidgets, QtCore

from ..utils import styles
from ..utils.styles import get_font, colors
from ..utils.widgets import BaseDialog, Entry


class EmailValidationForm(BaseDialog):
    title = "Email Validation"
    size = (400, 200)

    def __init__(self, client, send_command, apply_command):
        super(EmailValidationForm, self).__init__()

        self.client = client
        self.send_command = send_command
        self.apply_command = apply_command

        self.code = "<not initialized>"

        self.send_email()

        self.label = QtWidgets.QLabel(f"Enter the code we sent to your email.", self)
        self.label.setStyleSheet(f"color: {colors['black']}")
        self.label.setFont(get_font(14, False, "Lato Light"))
        self.label.move(25, 75)

        self.resend_label = QtWidgets.QLabel(f"Didn't get the email?", self)
        self.resend_label.setStyleSheet(f"color: {colors['black']}")
        self.resend_label.setFont(get_font(14, False, "Lato Light"))
        self.resend_label.move(25, 170)
        self.resend_label.adjustSize()
        self.resend_label.setVisible(False)

        self.resend_button = QtWidgets.QPushButton(self)
        self.resend_button.setText("Resend")
        self.resend_button.setFont(get_font(14, True))
        self.resend_button.setGeometry(QtCore.QRect(150, 164, 57, 29))
        self.resend_button.setStyleSheet(styles.text_button_style)
        self.resend_button.setVisible(False)

        self.resend_button.clicked.connect(self.resend)

        self.entry = Entry(self, rect=(25, 110, 350, 40), text="Enter the validation code",
                           help="Validation code",
                           regex="[0-9]*",
                           max_length=6)

        QtCore.QTimer.singleShot(10000, self.no_email)

    def typing(self):
        if self.entry.encrypted == self.code:
            if self.apply_command:
                self.apply_command['parameters'] = self.apply_command.get('parameters', {})
                self.apply_command['parameters'].update(code=self.entry.text())
                self.client.send(self.apply_command)
            self.result = self.entry.text()
        elif self.entry.text():
            self.entry.show_error("Wrong code")

    def send_email(self):
        self.code = self.client.execute(self.send_command)

    def resend(self):
        self.resend_button.setEnabled(False)

        QtCore.QTimer.singleShot(60000, self.no_email)

        self.send_email()

    def no_email(self):
        self.resend_button.setVisible(True)
        self.resend_button.setEnabled(True)
        self.resend_label.setVisible(True)
