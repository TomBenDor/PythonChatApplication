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

![image](https://user-images.githubusercontent.com/36517134/133907968-3fdae622-1f76-47bb-84c9-d268b5bc8d93.png)

![image](https://user-images.githubusercontent.com/36517134/133907971-97a90648-359b-496e-8cb1-027f0f60bc89.png)

![image](https://user-images.githubusercontent.com/36517134/133907979-9e13fc3a-68db-4f09-8b46-c1fbe53389bd.png)

![image](https://user-images.githubusercontent.com/36517134/133907985-778f9163-998a-4ea4-81a5-a3cf4231d7c6.png)

![image](https://user-images.githubusercontent.com/36517134/133907987-2f2e5708-04ee-4e2a-86e8-1b81f8c410ab.png)

![image](https://user-images.githubusercontent.com/36517134/133907989-41cc974a-6b67-4328-9fee-ab393b325fad.png)
