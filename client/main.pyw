import socket
import sys

from PyQt5 import QtWidgets

from client.auth import create_credentials
from client.auth.login import LoginForm
from client.chat.application import Chat
from smart_socket import Socket

IP = "127.0.0.1"
PORT = 65432
TESTING = True  # Set this False to remember credentials.


class Client(Socket):
    def __init__(self, sock):
        super().__init__(sock)

        self.username = None
        self.name = None

    def login(self, username: str, password: str) -> str:
        response = self.execute({'command': "login", 'parameters': {'username': username, 'password': password}})

        if not response['errors']:
            self.username = username
            self.name = response.get('data', {}).get('name')

        return response['errors']


def main():
    with socket.create_connection((IP, PORT)) as client:
        client = Client(client)

        app = QtWidgets.QApplication(sys.argv)

        if TESTING:
            # Opening login form.
            form = LoginForm(client)
            form.show()
            app.exec_()
        else:
            # Getting credentials from cache.
            create_credentials(client)

        # If user didn't login:
        if client.username is None:
            return

        # Opening the main chat window.
        win = Chat(client)
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
