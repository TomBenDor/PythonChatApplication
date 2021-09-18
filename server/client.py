from smart_socket import Socket


class Client(Socket):
    def __init__(self, sock):
        super(Client, self).__init__(sock)

        self.room = None
        self._username = None
        self.name = None

    @property
    def is_authenticated(self):
        return self.username is not None

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if self.is_authenticated:
            raise Exception("Client is already authenticated.")
        self._username = value
