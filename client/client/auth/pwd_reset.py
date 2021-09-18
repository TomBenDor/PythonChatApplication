from PyQt5 import QtWidgets, QtCore

from .email_validation import EmailValidationForm
from ..utils import styles
from ..utils.styles import get_font
from ..utils.widgets import BaseDialog, Entry


class ForgotPassword(BaseDialog):
    title = "Forgot Password"
    size = (400, 220)

    def __init__(self, client):
        super(ForgotPassword, self).__init__()

        self.client = client

        self.entry = Entry(self,
                           rect=(25, 100, 350, 40),
                           max_length=15,
                           regex="[A-Za-z][A-Za-z0-9]*",
                           text="Enter your username",
                           help="Username")

        self.submit_button = QtWidgets.QPushButton(self)
        self.submit_button.setText("Submit")
        self.submit_button.setFont(get_font(14, False))
        self.submit_button.setGeometry(QtCore.QRect(180, 180, 90, 30))
        self.submit_button.setStyleSheet(styles.button_style)
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.reset_password)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText("Cancel")
        self.cancel_button.setFont(get_font(14, False))
        self.cancel_button.setGeometry(QtCore.QRect(285, 180, 90, 30))
        self.cancel_button.setStyleSheet(styles.default_button_style)
        self.cancel_button.clicked.connect(self.close)

        self.on_enter(self.submit_button.click)

    def typing(self):
        self.submit_button.setEnabled(len(self.entry.text()) > 0)

    def reset_password(self):
        if self.client.execute({"command": "username_exists", "parameters": {"username": self.entry.text()}}):
            self.hide()
            self.reset_password_form = ResetPassword(self.client, self.entry.text())
            self.reset_password_form.exec_()
            self.close()
        else:
            self.entry.show_error("Username does not exist")


class ResetPassword(BaseDialog):
    title = "Password Reset"
    size = (400, 280)

    def __init__(self, client, username):
        super().__init__()

        self.client = client
        self.username = username

        self.email_validation = EmailValidationForm(self.client,
                                                    apply_command=None,
                                                    send_command={'command': "send_validation_email",
                                                                  'parameters': {'username': self.username}})
        self.hide()
        self.email_validation.exec_()
        self.code = self.email_validation.result

        self.password_entry = Entry(self,
                                    rect=(25, 100, 350, 40),
                                    regex="[^\\s].+",
                                    text="Choose your new password",
                                    help="Password",
                                    echo_mode=QtWidgets.QLineEdit.Password)

        self.password_confirmation_entry = Entry(self,
                                                 rect=(25, 160, 350, 40),
                                                 regex="[^\\s].+",
                                                 text="Confirm your password",
                                                 help="Password confirmation",
                                                 echo_mode=QtWidgets.QLineEdit.Password)

        self.submit_button = QtWidgets.QPushButton(self)
        self.submit_button.setText("Reset")
        self.submit_button.setFont(get_font(14, False))
        self.submit_button.setGeometry(QtCore.QRect(285, 240, 90, 30))
        self.submit_button.setStyleSheet(styles.button_style)
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.submit)

        self.on_enter(self.submit_button.click)

    def typing(self):
        self.submit_button.setEnabled(
                len(self.password_confirmation_entry.text()) > 0 and len(self.password_entry.text()) > 0)

    def submit(self):
        data = {
            'username': self.username,
            'password': self.password_entry.text(),
            'password_confirmation': self.password_confirmation_entry.text(),
            'code': self.code
        }

        errors = self.client.execute({'command': "reset_password", 'parameters': data})

        if errors:
            for field, error in errors.items():
                self.__dict__[f"{field}_entry"].show_error(error)
        else:
            self.hide()

            self.result = "ok"
