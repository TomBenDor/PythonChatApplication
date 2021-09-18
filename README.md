# Python Chat Application

Simple chat application using Python for desktop.

## Features

* Multiple clients
* Multiple chat rooms
* Authentication system
  * Login
  * Sign up
  * Forgot password
* Email validation

## Communication

The Server-Client communication is via the `smart_socket`:

```python
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
```

Which uses pickle to serialize JSON objects and send it to the client.

## UI

The user interface was done using PyQt5.

The authentication design was inspired by Zoom software for desktop.

Responsive design, the main window is fully resizable.

### Demos

![](.\demos\login.jpg)

![](.\demos\login-filled.jpg)

![](.\demos\login-error.jpg)

![](.\demos\signup.jpg)

![](.\demos\welcome.jpg)

![](.\demos\room.jpg)
