import socket
from protocol import encode_message, decode_message, Message


# HOST = "192.168.15.2"
# PORT = 50007

class TransferServer:

    def __init__(self, host: str = "", port: int = 50007):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def start(self):
        # reserves a port on your computer
        self.server_socket.bind((self.host, self.port))
        # Waits for a client
        self.server_socket.listen()
        print("Listening...")
        self.accept_connections()

    def stop(self) -> None:
        self.server_socket.close()

    # accept_connections keeps listening, conn represents one connected client
    def accept_connections(self):
        while True:
            # (!) Currently accept() waits indefinitely for a client (!)
            # Requires running flag and exception handling if threads are introduced
            conn, addr = self.server_socket.accept()
            print(f"{addr} connected")
            self.handle_client(conn, addr)

    # WIP, currently method 'handle_client' may be 'static'
    def handle_client(self, conn, addr):
        print(f"Handling client {addr}")

        with conn:
            while True:
                data = conn.recv(4096)

                if not data:
                    break

                received_message = decode_message(data)
                ### DEBUG ###
                print(
                    f"[{addr}] "
                    f"{received_message.message_type.value} "
                    f"{received_message.payload}"
                )
                ### DEBUG ###

                reply_message = encode_message(received_message)

                conn.sendall(reply_message)


class TransferClient:
    def send_message(self, host: str, port: int, message: Message) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))

            encoded = encode_message(message)
            client_socket.sendall(encoded)

            reply = client_socket.recv(1024)
            reply_message = decode_message(reply)

            print(reply_message)
            #print(reply_message.payload)
            #print(reply_message.message_type)