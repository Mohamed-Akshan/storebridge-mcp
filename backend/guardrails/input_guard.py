MAX_MESSAGE_LENGTH = 1800
MAX_HISTORY_MESSAGES = 18


def validate_messages(messages):
    if not messages or messages[-1].role != "user":
        raise ValueError("The latest message must come from the user")

    if len(messages) > MAX_HISTORY_MESSAGES:
        raise ValueError("Start a new conversation to continue")

    for message in messages:
        if message.role not in ("user", "assistant"):
            raise ValueError("Unsupported message role")

        if not message.content.strip() or len(message.content) > MAX_MESSAGE_LENGTH:
            raise ValueError("Invalid message length")
