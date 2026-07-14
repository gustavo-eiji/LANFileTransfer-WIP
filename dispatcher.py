import base64
from protocol import Message, MessageType

current_filename: str | None = None

def dispatch_message(message: Message) -> Message | None:
    if message.message_type == MessageType.TEXT:
        return handle_text(message)

    if message.message_type == MessageType.PING:
        return handle_ping(message)

    if message.message_type == MessageType.FILE_OFFER:
         return handle_file_offer(message)

    if message.message_type == MessageType.FILE_DATA:
        return handle_file_data(message)

    if message.message_type == MessageType.FILE_COMPLETE:
        return handle_file_complete(message)

    raise ValueError(f"Message type not supported: {message.message_type}")

def handle_text(message: Message) -> Message:

    return Message(
        message_type=MessageType.TEXT,
        payload={"text": "Server received: " + message.payload["text"]}
    )

def handle_ping(message: Message) -> Message:
    return Message(
        message_type=MessageType.PONG,
        payload={"text": "PONG"}
    )

def handle_file_offer(message: Message) -> Message:
    global current_filename

    current_filename = message.payload["filename"]
    filesize = message.payload["filesize"]
    print(f"Incoming file: {current_filename}\n")
    print(f"Size: {filesize}")

    return Message(
        message_type=MessageType.FILE_ACCEPT,
        payload={"text":"Preparing to receive offer..."}
    )

def handle_file_data(message: Message) -> Message | None:
    global current_filename

    chunk = base64.b64decode(message.payload["data"])

    # "ab" append binary -> Every incoming chunk gets appended to the end of the file.
    with open(current_filename, "ab") as file:
        file.write(chunk)

    return None

def handle_file_complete(message: Message) -> None:
    print("Transfer finished.")
    return None

# def handle_file_accept(message: Message) -> Message:
#     ...