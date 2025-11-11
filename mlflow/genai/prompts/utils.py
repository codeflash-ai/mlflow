import re
from functools import lru_cache
from typing import Any


def format_prompt(prompt: str, **values: Any) -> str:
    """Format double-curly variables in the prompt template."""
    for key, value in values.items():
        # Escape backslashes in the replacement string to prevent re.sub from interpreting
        # them as escape sequences (e.g. \u being treated as Unicode escape)
        replacement = str(value).replace("\\", "\\\\")
        prompt = _compiled_key_pattern(key).sub(replacement, prompt)
    return prompt


@lru_cache(maxsize=64)
def _compiled_key_pattern(key: str) -> re.Pattern:
    # Compile and cache the regex pattern for a template variable key
    return re.compile(r"\{\{\s*" + re.escape(key) + r"\s*\}\}")
