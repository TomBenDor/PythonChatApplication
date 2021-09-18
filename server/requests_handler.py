import os
import random
import re
from _thread import start_new_thread
from email.headerregistry import Address
from email.message import EmailMessage

from client import Client
from utils import send_email, encrypt, mutex, QueryExecutor


# Require login before using this command.
def login_required(function):
    def inner(*args, **kwargs):
        self: RequestsHandler = args[0]
        if not self.client.is_authenticated:
            return "ERROR: You must log in before using this command."

        return function(*args, **kwargs)

    return inner


class RequestsHandler:
    validation_codes = {}

    def __init__(self, client: Client, clients: list[Client]):
        self.client = client
        self.clients = clients

        # Opening SQL connection.
        self.execute_query = QueryExecutor("database/database.db")

        self.rooms = ["Sports", "Gaming", "Food"]  # Available rooms.

    def handle(self, request: dict):
        command, params = request.get('command'), request.get('parameters', {})

        # Supported commands:
        supported = {
            "activate_user": self.activate_user,
            "login": self.login,
            "signup": self.signup,
            "send_validation_email": self.send_validation_email,
            "send_message": self.send_message,
            "enter_room": self.enter_room,
            "get_online": self.get_online,
            "reset_password": self.reset_password,
            "username_exists": self.username_exists,
            "get_rooms": self.get_rooms,
        }

        # Running selected command.
        return supported.get(command, lambda **kwargs: f"ERROR: Unknown command {command}.")(**params)

    @mutex
    def login(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')

        # If username exists.
        if user := self.execute_query("SELECT password, isActive, name FROM tblUsers WHERE username=?",
                                      [username]):
            # Getting the user's details.
            encrypted_password, active, name = user[0]
            # Validating password.
            if encrypted_password == encrypt(password):
                # Verifying that the user was activated.
                if not active:
                    return {'errors': {'username': 'Username is not active'}}
                # Checking if the client is already connected.
                for client in self.clients:
                    if client.is_authenticated and client.username == username:
                        return {'errors': {'username': 'You are already connected via another client'}}

                # Logging in.
                self.client.username = username
                self.client.name = name
                return {'errors': {}, 'data': {'name': name}}
            return {'errors': {'password': 'Incorrect password'}}
        return {'errors': {'username': 'Username does not exist'}}

    @login_required
    def send_message(self, **kwargs):
        msg = kwargs.get("message")

        # Removing spaces around the message.
        if isinstance(msg, str):
            msg = msg.strip()

        # Verifying client is in a room and message not empty.
        if not self.client.room or not msg:
            return

        for client in self.clients:
            if client.is_authenticated and client.room == self.client.room:
                try:
                    # Sending the message.
                    client.send({"type": "message",
                                 "data": {"message": msg, "username": self.client.username, "name": self.client.name}})
                except:
                    self.remove_client(client)

    @mutex
    def remove_client(self, client: Client):
        if client in self.clients:
            self.clients.remove(client)
            # Notifying that the client is no longer connected.
            self.notify_all_client_entered(client, room="None")

    def notify_all_client_entered(self, client: Client, **kwargs):
        room = kwargs.get("room")

        for c in self.clients:
            if c.is_authenticated:
                try:
                    c.send({"type": "client_entered", "data": {"room": room, "username": client.username}})
                except:
                    self.remove_client(client)

    @login_required
    def enter_room(self, **kwargs):
        room = kwargs.get("room")

        if room in self.rooms:
            self.client.room = room
            self.notify_all_client_entered(self.client, room=room)

    @login_required
    def get_online(self):
        result = []
        for client in self.clients:
            if client.is_authenticated and client.room is not None:
                result.append({"room": client.room, "username": client.username})
        return result

    @login_required
    def get_rooms(self):
        return self.rooms

    @mutex
    def signup(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        password_confirmation = kwargs.get('password_confirmation')
        name = kwargs.get('name')
        email = kwargs.get('email')
        phone_number = kwargs.get('phone_number')

        errors = {}

        if len(username) < 5:
            errors['username'] = "Username is too short"

        if not re.fullmatch("[A-Za-z][A-Za-z0-9]*", username):
            errors['username'] = "Invalid username"  # Client forcing this regex.

        if not re.fullmatch("([A-Za-z]+ ?)*", name):
            errors['name'] = "Invalid name"  # Client forcing this regex.

        if self.execute_query("SELECT username from tblUsers WHERE username=?", [username]):
            errors['username'] = "Username already in use"

        self.validate_password(errors, password, password_confirmation)

        if len(name) < 6:
            errors['name'] = "Name is too short"

        if not re.fullmatch(r"[a-z0-9.\-]+@([a-z\-]+\.[a-z]+)+", email):
            errors['email'] = "Invalid email address"

        if self.execute_query("SELECT username from tblUsers WHERE email=?", [email]):
            errors['email'] = "Email address already in use"

        if not re.fullmatch("05[02458][0-9]{7}", phone_number):
            errors['phone_number'] = "Phone number must contain exactly 10 digits"

        if not errors:
            encrypted_password = encrypt(password)
            self.execute_query("INSERT INTO tblUsers VALUES (?, ?, ?, ?, 0, ?)",
                               [username, name, email, encrypted_password, phone_number])
        return errors

    @staticmethod
    def validate_code(username, code):
        assert code == RequestsHandler.validation_codes[username], f"Wrong validation code {code}"
        # Invalidating the validation code so that it will only be used ones.
        del RequestsHandler.validation_codes[username]

    def send_validation_email(self, **kwargs):
        username = kwargs.get('username')

        name, email_address = \
            self.execute_query("SELECT name, email FROM tblUsers WHERE username=?", [username])[0]
        # Generating the code.
        code = RequestsHandler.validation_codes.get(username, str(random.randint(100000, 999999)))
        RequestsHandler.validation_codes[username] = code

        email = EmailMessage()
        email['Subject'] = "Email Validation - Chat Application"
        email['From'] = Address(addr_spec=os.environ.get("EMAIL_ADDRESS"), display_name="Chat Application")
        email['To'] = Address(addr_spec=email_address, display_name=name)

        msg = f"Hey {name}!\n" \
              f"To validate that this email address belongs to you,\n" \
              f"please enter {code} in the email validation window."
        email.set_content(msg)

        # Sending the email.
        start_new_thread(send_email, (email,))

        # Returning the hashed code.
        # This is not necessary but used by the client to quickly validate the code.
        return encrypt(code)

    @staticmethod
    def validate_password(errors, password, password_confirmation):
        if not re.findall(r"[a-zA-Z]", password):
            errors['password'] = "Password must contain at least one letter"
        if not re.findall(r"\d", password):
            errors['password'] = "Password must contain at least one digit"
        if len(password) < 8:
            errors['password'] = "Password must contain at least 8 characters"
        if password != password_confirmation:
            errors['password_confirmation'] = "Passwords do not match"

    def reset_password(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        password_confirmation = kwargs.get('password_confirmation')
        code = kwargs.get('code')

        errors = {}
        self.validate_password(errors, password, password_confirmation)

        if not errors:
            self.validate_code(username, code)
            self.execute_query("UPDATE tblUsers SET password=? WHERE username=?", [encrypt(password), username])

        return errors

    def username_exists(self, **kwargs):
        username = kwargs.get('username')

        return len(self.execute_query("SELECT username FROM tblUsers WHERE username=?", [username])) > 0

    def activate_user(self, **kwargs):
        username = kwargs.get('username')
        code = kwargs.get('code')  # Validation code generated by send_validation_email.

        self.validate_code(username, code)

        # Code is valid, activating the user.
        self.execute_query("UPDATE tblUsers SET isActive=1 WHERE username=?", [username])
