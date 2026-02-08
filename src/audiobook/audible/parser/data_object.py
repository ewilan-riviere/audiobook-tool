import html
from typing import Any, Dict, List, Union
from audiobook.common import AutoRepr


class DataObject(AutoRepr):
    def __getattr__(self, name: str) -> Any:
        # On lève une AttributeError au lieu de renvoyer None
        # pour signaler proprement l'absence de la clé
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"'{name}' non trouvé dans {self}")

    def __init__(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            clean_key: str = key.replace("@", "")

            if isinstance(value, dict):
                setattr(self, clean_key, DataObject(value))  # type: ignore
            elif isinstance(value, list):
                val_list: List[Union["DataObject", Any]] = [
                    DataObject(i) if isinstance(i, dict) else i for i in value  # type: ignore
                ]
                setattr(self, clean_key, val_list)
            else:
                val: Any = html.unescape(value) if isinstance(value, str) else value
                setattr(self, clean_key, val)

    def deep(self, path: str, default: Any = None) -> Any:
        """
        Permet de faire : data.deep("aggregateRating.ratingValue")
        """
        keys = path.split(".")
        current = self
        for key in keys:
            current = getattr(current, key, None)
            if current is None:
                return default
        return current
