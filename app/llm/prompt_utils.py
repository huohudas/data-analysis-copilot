import re
from typing import Any


def render_prompt(template: str, **kwargs: Any) -> str:
    rendered = template

    for key, value in kwargs.items():
        placeholder = f"__{key.upper()}__"
        rendered = rendered.replace(placeholder, str(value))

    unresolved = re.findall(r"__([A-Z0-9_]+)__", rendered)
    if unresolved:
        unresolved = sorted(set(unresolved))
        raise ValueError(f"Unresolved prompt placeholders: {', '.join(unresolved)}")

    return rendered
