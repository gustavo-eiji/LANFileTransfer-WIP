import base64
import socket
from dispatcher import dispatch_message
from protocol import encode_message, decode_message, Message, MessageType
from pathlib import Path
import os
import struct

# HOST = "192.168.15.2"
# PORT = 50007

def recv_exact(conn, size: int) -> bytes | None:
    data = b""

    while len(data) < size:
        chunk = conn.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data

class TransferServer:

    def __init__(self, host: str = "", port: int = 50007):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.running = False

    def start(self):
        self.running = True
        # reserves a port on your computer
        self.server_socket.bind((self.host, self.port))
        # Waits for a client
        self.server_socket.listen()
        print("Listening...")
        self.accept_connections()

    def stop(self) -> None:
        self.running = False
        self.server_socket.close()

    # accept_connections keeps listening, conn represents one connected client
    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                print(f"{addr} connected")

            except OSError:
                break

            self.handle_client(conn, addr)

    # WIP, currently method 'handle_client' may be 'static'
    def handle_client(self, conn, addr):
        print(f"Handling client {addr}")

        with conn:
            while True:
                received_message = self.receive_packet(conn)

                if received_message is None:
                    break

                print(
                    f"DEBUG: [{addr}] \n"
                    f"DEBUG: {received_message.message_type.value} \n"
                    f"DEBUG: {received_message.payload} \n"
                )

                reply_message = dispatch_message(received_message)

                if reply_message is not None:
                    self.send_packet(conn, reply_message)



    def receive_packet(self, conn) -> Message | None:
        # Read the 4-byte message length
        header = recv_exact(conn, 4)

        if not header:
            return None

        message_length = struct.unpack("!I", header)[0]

        # Read exactly message_length bytes
        data = b""
        while len(data) < message_length:
            chunk = conn.recv(message_length - len(data))

            if not chunk:
                return None

            data += chunk

        return decode_message(data)

    def send_packet(self, conn, message: Message) -> None:
        data = encode_message(message)

        header = struct.pack("!I", len(data))

        conn.sendall(header)
        conn.sendall(data)


class TransferClient:
    def send_message(self, host: str, port: int, message: Message) -> Message:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))

            self.send_packet(client_socket, message)

            reply = self.receive_packet(client_socket)

            return reply


    def send_file(self, path: str, host: str, port: int) -> bytes | None:

        filename = Path(path).name
        filesize = os.path.getsize(path)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))

            # Send FILE_OFFER
            offer = Message(
                message_type=MessageType.FILE_OFFER,
                payload={"filename": filename, "filesize": filesize}
            )

            self.send_packet(client_socket, offer)

            reply = self.receive_packet(client_socket)

            if reply.message_type != MessageType.FILE_ACCEPT:
                print("Transfer rejected.")

                return

            print("Transfer accepted.")

            # Send FILE_DATA Messages

            chunk_number = 0
            with open(path, "rb") as file:
                while True:
                    chunk = file.read(4096)

                    if not chunk:
                        break

                    chunk_number += 1
                    print(f"Sending chunk {chunk_number} ({len(chunk)} bytes)")

                    data_message = Message(
                        message_type=MessageType.FILE_DATA,
                        payload={
                            "data": base64.b64encode(chunk).decode("ascii")
                        }
                    )

                    self.send_packet(client_socket, data_message)

            # Send FILE_COMPLETE
            complete = Message(
                message_type=MessageType.FILE_COMPLETE,
                payload={}
            )

            self.send_packet(client_socket, complete)

            print("Transfer complete.")

    def receive_packet(self, conn) -> Message | None:
        header = recv_exact(conn, 4)

        if not header:
            return None

        message_length = struct.unpack("!I", header)[0]

        data = b""
        while len(data) < message_length:
            chunk = conn.recv(message_length - len(data))

            if not chunk:
                return None

            data += chunk

        return decode_message(data)

    def send_packet(self, conn, message: Message) -> None:
        data = encode_message(message)

        header = struct.pack("!I", len(data))

        conn.sendall(header)
        conn.sendall(data)
