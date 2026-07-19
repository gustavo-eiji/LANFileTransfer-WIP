import socket
from dispatcher import dispatch_message
from protocol import encode_message, decode_message, Message, MessageType
from pathlib import Path
import os
import struct

# HOST = "192.168.15.2"
# PORT = 50007

TRANSFER_BUFFER_SIZE = 64 * 1024  # 64 KiB

def recv_exact(conn, size: int) -> bytes | None:
    data = b""

    while len(data) < size:
        chunk = conn.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data

### SERVER SIDE ###
class TransferServer:

    def __init__(self, host: str = "", port: int = 50007):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

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
        self.server_socket.settimeout(1.0)

    # accept_connections keeps listening, conn represents one connected client
    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                print(f"{addr} connected")

            except socket.timeout:
                continue

            self.handle_client(conn, addr)

    def handle_client(self, conn, addr):
        print(f"Handling client {addr}")

        with conn:
            while True:
                received_message = self.receive_packet(conn)

                if received_message is None:
                    break

                # print(
                #     f"DEBUG: [{addr}] \n"
                #     f"DEBUG: {received_message.message_type.value} \n"
                #     f"DEBUG: {received_message.payload} \n"
                # )

                if received_message.message_type == MessageType.FILE_OFFER:
                    filename = received_message.payload["filename"]
                    filesize = received_message.payload["filesize"]

                    self.send_packet(
                        conn,
                        Message(MessageType.FILE_ACCEPT, {})
                    )

                    self.receive_file(
                        conn,
                        filename,
                        filesize,
                    )
                    break

                reply_message = dispatch_message(received_message)

                if reply_message is not None:
                    self.send_packet(conn, reply_message)



    def receive_packet(self, conn) -> Message | None:
        # Read the 4-byte message length
        header = recv_exact(conn, 4)

        if header is None:
            return None

        message_length = struct.unpack("!I", header)[0]

        data = recv_exact(conn, message_length)

        if data is None:
            return None

        # Read exactly message_length bytes
        # data = b""
        # while len(data) < message_length:
        #     chunk = conn.recv(message_length - len(data))
        #
        #     if not chunk:
        #         return None
        #
        #     data += chunk

        return decode_message(data)

    def send_packet(self, conn, message: Message) -> None:
        data = encode_message(message)

        header = struct.pack("!I", len(data))

        conn.sendall(header)
        conn.sendall(data)

    def receive_file(self, conn, filename: str, filesize: int):

        received = 0

        with open(filename, "wb") as file:

            while received < filesize:

                remaining = filesize - received

                chunk = conn.recv(
                    min(TRANSFER_BUFFER_SIZE, remaining)
                )

                if not chunk:
                    raise ConnectionError(
                        "Connection lost during transfer."
                    )

                file.write(chunk)

                received += len(chunk)

                print(
                    f"Received {received}/{filesize} bytes"
                )

        print("Transfer complete.")

### CLIENT SIDE ###
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

            if reply is None:
                print("Connection closed.")
                return

            if reply.message_type != MessageType.FILE_ACCEPT:
                print("Transfer rejected.")
                return

            print("Transfer accepted.")

            self.stream_file(
                client_socket,
                path,
            )

            # chunk_number = 0
            # with open(path, "rb") as file:
            #     while True:
            #         chunk = file.read(4096)
            #
            #         if not chunk:
            #             break
            #
            #         chunk_number += 1
            #         print(f"Sending chunk {chunk_number} ({len(chunk)} bytes)")
            #
            #         data_message = Message(
            #             message_type=MessageType.FILE_DATA,
            #             payload={
            #                 "data": base64.b64encode(chunk).decode("ascii")
            #             }
            #         )
            #
            #         self.send_packet(client_socket, data_message)
            #
            # # Send FILE_COMPLETE
            # complete = Message(
            #     message_type=MessageType.FILE_COMPLETE,
            #     payload={}
            # )
            #
            # self.send_packet(client_socket, complete)
            #
            # print("Transfer complete.")

    def receive_packet(self, conn) -> Message | None:
        header = recv_exact(conn, 4)

        if not header:
            return None

        message_length = struct.unpack("!I", header)[0]

        data = recv_exact(conn, message_length)

        if data is None:
            return None

        return decode_message(data)

    def send_packet(self, conn, message: Message) -> None:
        data = encode_message(message)

        header = struct.pack("!I", len(data))

        conn.sendall(header)
        conn.sendall(data)

    def stream_file(self, conn, path):

        sent = 0

        filesize = os.path.getsize(path)

        with open(path, "rb") as file:

            while True:

                chunk = file.read(TRANSFER_BUFFER_SIZE)

                if not chunk:
                    break

                conn.sendall(chunk)

                sent += len(chunk)

                print(
                    f"Sent {sent}/{filesize} bytes"
                )

        print("Transfer complete.")