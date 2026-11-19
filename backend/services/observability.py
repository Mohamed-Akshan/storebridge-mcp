
from pathlib import Path

from dotenv import load_dotenv
from langfuse import get_client
from langfuse.langchain import CallbackHandler


# Load environment variables from project root.
load_dotenv(
    Path(__file__).resolve().parents[2] / ".env"
)


def graph_config():
    return {
        "callbacks": [
            CallbackHandler()
        ]
    }


def check_langfuse():
    langfuse = get_client()

    return langfuse.auth_check()
