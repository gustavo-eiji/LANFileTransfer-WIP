from protocol import Message, MessageType

current_filename: str | None = None

def dispatch_message(message: Message) -> Message | None:
    if message.message_type == MessageType.TEXT:
        return handle_text(message)

    if message.message_type == MessageType.PING:
        return handle_ping(message)

    if message.message_type == MessageType.FILE_OFFER:
         return handle_file_offer(message)

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
    # global current_filename

    filename = message.payload["filename"]
    filesize = message.payload["filesize"]

    print(f"Incoming file: {filename}\n")
    print(f"Size: {filesize}")

    return Message(
        message_type=MessageType.FILE_ACCEPT,
        payload={}
    )
