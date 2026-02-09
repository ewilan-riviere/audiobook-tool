from typing import Any
from yaml import SafeDumper, ScalarNode


class BlockStyleDumper(SafeDumper):
    """Dumper personnalisé pour forcer le style bloc sur les chaînes multilignes."""

    def represent_scalar(self, tag: str, value: Any, style: Any = None) -> ScalarNode:
        # Si la valeur contient un saut de ligne, on FORCE le style '|'
        if isinstance(value, str) and "\n" in value:
            style = "|"
        return super().represent_scalar(tag, value, style)  # type: ignore
