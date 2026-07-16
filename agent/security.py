import re

def sanitize_llm_input(text: str) -> str:
    """Sanitize input before sending to Groq to prevent prompt injection."""
    if not text:
        return ""
    # Remove system prompt-like instructions
    sanitized = re.sub(r"(?i)(ignore previous instructions|system prompt|you are |forget everything)", "", text)
    # Basic escaping
    sanitized = sanitized.replace("{", "{{").replace("}", "}}")
    return sanitized.strip()

def validate_email(email: str) -> bool:
    """Basic email validation regex."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))
