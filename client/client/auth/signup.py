from PyQt5 import QtWidgets, QtCore

from .email_validation import EmailValidationForm
from ..utils.styles import button_style, text_button_style, colors, get_font
from ..utils.valildators import NameValidator
from ..utils.widgets import Entry, BaseDialog


class SignUpForm(BaseDialog):
    title = "Sign Up"
    size = (400, 500)

    def __init__(self, client, login):
        super().__init__()

        self.client = client
        self.login = login

        self.signup_button = QtWidgets.QPushButton(self)
        self.signup_button.setText("Sign Up")
        self.signup_button.setFont(get_font(14, False))
        self.signup_button.setGeometry(QtCore.QRect(285, 440, 90, 30))
        self.signup_button.setStyleSheet(button_style)
        self.signup_button.setEnabled(False)
        self.signup_button.clicked.connect(self.signup)

        self.name_entry = Entry(self,
                                rect=(25, 100, 170, 40),
                                max_length=20,
                                validator=NameValidator,
                                text="Enter your name",
                                help="Full name",
                                strip=True)

        self.username_entry = Entry(self,
                                    rect=(205, 100, 170, 40),
                                    max_length=15,
                                    regex="[A-Za-z][A-Za-z0-9]*",
                                    text="Choose username",
                                    help="Username")

        self.email_entry = Entry(self,
                                 rect=(25, 160, 350, 40),
                                 regex=r"[a-z0-9\.-]+@[a-z0-9\.-]+",
                                 text="Enter your email address",
                                 help="Email address")

        self.phone_number_entry = Entry(self,
                                        rect=(25, 220, 350, 40),
                                        regex="05[02458][0-9]{7}",
                                        text="Enter your phone number",
                                        help="Phone number")

        self.password_entry = Entry(self,
                                    rect=(25, 280, 350, 40),
                                    regex="[^\\s].+",
                                    text="Choose password",
                                    help="Password",
                                    echo_mode=QtWidgets.QLineEdit.Password)

        self.password_confirmation_entry = Entry(self,
                                                 rect=(25, 340, 350, 40),
                                                 regex=r"[^\\s].+",
                                                 text="Confirm your password",
                                                 help="Password confirmation",
                                                 echo_mode=QtWidgets.QLineEdit.Password)

        self.login_button = QtWidgets.QPushButton(self)
        self.login_button.setText("Login")
        self.login_button.setFont(get_font(14, False))
        self.login_button.setGeometry(QtCore.QRect(180, 464, 50, 29))
        self.login_button.setStyleSheet(text_button_style)
        self.login_button.clicked.connect(self.close)

        self.login_label = QtWidgets.QLabel("Already have an account?", self)
        self.login_label.setStyleSheet(f"color: {colors['black']}")
        self.login_label.setFont(get_font(14, False, "Lato Light"))
        self.login_label.move(25, 470)
        self.login_label.adjustSize()

        self.on_enter(self.signup_button.click)

    @property
    def fields(self):
        return (self.name_entry,
                self.username_entry,
                self.email_entry,
                self.phone_number_entry,
                self.password_entry,
                self.password_confirmation_entry)

    def typing(self):
        self.signup_button.setEnabled(all(len(e.text()) > 0 for e in self.fields))

    def signup(self):
        data = {
            'username': self.username_entry.text(),
            'name': self.name_entry.text(),
            'email': self.email_entry.text(),
            'phone_number': self.phone_number_entry.text(),
            'password': self.password_entry.text(),
            'password_confirmation': self.password_confirmation_entry.text()
        }

        errors = self.client.execute({'command': "signup", 'parameters': data})

        if errors:
            for field, error in errors.items():
                self.__dict__[f"{field}_entry"].show_error(error)
        else:
            self.login.signup_button.setVisible(False)
            self.login.signup_label.setVisible(False)
            self.login.username_entry.setText(self.username_entry.text())

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

            self.result = self.email_confirmation.result
