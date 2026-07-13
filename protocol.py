from dataclasses import dataclass
from enum import Enum
import json
from typing import Any

class MessageType(Enum):
    PING = "PING"
    PONG = "PONG"
    TEXT = "TEXT"

    FILE_OFFER = "FILE_OFFER"
    FILE_ACCEPT = "FILE_ACCEPT"
    FILE_REJECT = "FILE_REJECT"

    FILE_DATA = "FILE_DATA"
    FILE_COMPLETE = "FILE_COMPLETE"

    ERROR = "ERROR"

@dataclass
class Message:
    message_type: MessageType
    payload: dict[str, Any]

def encode_message(message: Message) -> bytes:
    # Serialize a Message object into UTF-8 encoded JSON bytes.
    data = {
        "type": message.message_type.value,
        "payload": message.payload,
    }

    return json.dumps(data).encode("utf-8")

def decode_message(raw_data: bytes) -> Message:
    # Deserialize UTF-8 encoded JSON bytes into a Message object.
    data = json.loads(raw_data.decode("utf-8"))

    return Message(
        message_type=MessageType(data["type"]),
        payload=data["payload"],
    )