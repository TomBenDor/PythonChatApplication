import socket
from _thread import start_new_thread

from client import Client
from requests_handler import RequestsHandler

IP = "127.0.0.1"
PORT = 65432

clients = []


def main():
    with socket.create_server((IP, PORT)) as server:
        server.listen()

        while True:
            client, address = server.accept()
            client = Client(client)
            clients.append(client)
            start_new_thread(handle_client, (client,))


def handle_client(client: Client):
    handler = RequestsHandler(client, clients)

    while True:
        try:
            request = client.receive()
        except ConnectionResetError:
            handler.remove_client(client)
            break

        try:
            response = handler.handle(request)
        except Exception as e:
            raise e
        else:
            if response is not None:
                client.send(response)


if __name__ == '__main__':
    main()
