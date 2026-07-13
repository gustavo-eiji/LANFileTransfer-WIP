from transfer import TransferClient
from protocol import Message, MessageType

HOST = "127.0.0.1"
PORT = 50007

client = TransferClient()

message = Message(
    message_type=MessageType.TEXT,
    payload={
        "text": "Hello from the client!"
    }
)

client.send_message(HOST, PORT, message)