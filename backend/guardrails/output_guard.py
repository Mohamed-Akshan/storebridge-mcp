
import ast
import json


FALLBACK_ANSWER = (
    "I'm sorry, I couldn't verify the information just now. "
    "Please try your question again."
)


def extract_text(value):
    """Extract readable text from AI response content."""

    if value is None:
        return ""

    if isinstance(value, str):
        text = value.strip()

        # Some providers return serialized content blocks.
        if text.startswith(("[", "{")) and len(text) < 50000:

            try:
                parsed = json.loads(text)

            except (ValueError, TypeError):
                try:
                    parsed = ast.literal_eval(text)

                except (ValueError, SyntaxError, MemoryError):
                    return text

            if isinstance(parsed, (list, dict)):
                extracted = extract_text(parsed)

                if extracted:
                    return extracted

        return text

    if isinstance(value, list):
        parts = []

        for item in value:
            text = extract_text(item)

            if text:
                parts.append(text)

        return "\n\n".join(parts)

    if isinstance(value, dict):
        block_type = value.get("type")

        if block_type in ("text", "output_text"):
            return extract_text(value.get("text", ""))

        if "content" in value:
            return extract_text(value["content"])

        if "output" in value:
            return extract_text(value["output"])

        if "answer" in value:
            return extract_text(value["answer"])

        return ""

    # Support SDK response objects.
    if hasattr(value, "content"):
        return extract_text(value.content)

    if hasattr(value, "text"):
        return extract_text(value.text)

    return ""


def check_answer(answer):
    """Return clean, safe-to-display assistant text."""

    text = extract_text(answer).strip()

    if not text:
        return FALLBACK_ANSWER

    return text[:16000]
