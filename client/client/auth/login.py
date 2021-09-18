from PyQt5 import QtWidgets, QtGui, QtCore

from .email_validation import EmailValidationForm
from .pwd_reset import ForgotPassword
from .signup import SignUpForm
from ..utils import styles
from ..utils.styles import colors, get_font
from ..utils.widgets import BaseDialog, Entry


class LoginForm(BaseDialog):
    title = "Login"
    size = (400, 300)

    def __init__(self, client):
        super().__init__()

        self.client = client

        self.username_entry = Entry(self,
                                    rect=(25, 100, 350, 40),
                                    max_length=15,
                                    regex="[A-Za-z][A-Za-z0-9]*",
                                    text="Enter your username",
                                    help="Username")

        self.password_entry = Entry(self,
                                    rect=(25, 160, 350, 40),
                                    regex="[^\\s].+",
                                    text="Enter your password",
                                    help="Password",
                                    echo_mode=QtWidgets.QLineEdit.Password)

        self.forgot_password = self.password_entry.addAction(QtGui.QIcon('images/forgot_password.png'),
                                                             QtWidgets.QLineEdit.TrailingPosition)
        self.forgot_password.setIconText("I forgot my password")
        self.forgot_password.triggered.connect(self.reset_password)

        self.login_button = QtWidgets.QPushButton(self)
        self.login_button.setText("Login")
        self.login_button.setFont(get_font(14, False))
        self.login_button.setGeometry(QtCore.QRect(285, 240, 90, 30))
        self.login_button.setStyleSheet(styles.button_style)
        self.login_button.setEnabled(False)

        self.login_button.clicked.connect(self.login)

        self.signup_button = QtWidgets.QPushButton(self)
        self.signup_button.setText("Sign Up")
        self.signup_button.setFont(get_font(14, False))
        self.signup_button.setGeometry(QtCore.QRect(170, 264, 63, 29))
        self.signup_button.setStyleSheet(styles.text_button_style)

        self.signup_button.clicked.connect(self.signup)

        self.signup_label = QtWidgets.QLabel("Don't have an account?", self)
        self.signup_label.setStyleSheet(f"color: {colors['black']}")
        self.signup_label.setFont(get_font(14, False, "Lato Light"))
        self.signup_label.move(25, 270)
        self.signup_label.adjustSize()

        self.signup_form = SignUpForm(self.client, self)

        self.on_enter(self.login_button.click)

    @property
    def data(self):
        return {
            'username': self.username_entry.text(),
            'password': self.password_entry.text(),
        }

    @property
    def fields(self):
        return self.username_entry, self.password_entry

    def typing(self):
        self.login_button.setEnabled(all(len(e.text()) > 0 for e in self.fields))

    def signup(self):
        self.hide()
        self.signup_form.exec_()
        self.show()

    def login(self):
        errors = self.client.login(self.username_entry.text(), self.password_entry.text())
        if errors.get('username') == "Username is not active":
            self.hide()
            self.email_confirmation = EmailValidationForm(self.client,
                                                          apply_command={'command': "activate_user",
                                                                         'parameters': {'username':
                                                                                            self.username_entry.text()}},
                                                          send_command={'command': "send_validation_email",
                                                                        'parameters': {
                                                                            'username':
                                                                                self.username_entry.text()}})
            self.email_confirmation.exec_()
            self.login()
            self.result = self.email_confirmation.result
        if errors:
            for field, error in errors.items():
                self.__dict__[f"{field}_entry"].show_error(error)
        else:
            self.result = "ok"

    def reset_password(self):
        self.hide()
        self.forgot_password_form = ForgotPassword(self.client)
        self.forgot_password_form.exec_()
        self.show()
