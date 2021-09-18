import json
import socket


class Socket:
    """
    Socket enhancement to enable sending unlimited-size messages and using the json module.
    """

    def __init__(self, sock: socket.socket):
        self.socket = sock

    def send(self, data) -> None:
        data = json.dumps(data).encode()

        self.socket.sendall(data)
        self.socket.send(b"<done>")

    def receive(self):
        data = b""
        while not data.endswith(b"<done>"):
            data += self.socket.recv(1024)
        data = data[:-6]

        return json.loads(data)

    def execute(self, command):
        self.send(command)
        return self.receive()
