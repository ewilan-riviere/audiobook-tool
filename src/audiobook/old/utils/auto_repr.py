"""Mixin to add an automatic and intelligent `__repr__` to classes"""

from typing import Any
from datetime import datetime


class AutoRepr:
    """Mixin to add an automatic and intelligent `__repr__` to classes"""

    def __repr__(self):
        def format_val(v: Any):
            # Si la valeur est un datetime, on la formate en string
            if isinstance(v, datetime):
                return f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
            # Sinon, on utilise le format standard (!r ajoute les guillemets si besoin)
            return repr(v)

        # On génère la liste des attributs
        attributes = [f"{k}={format_val(v)}" for k, v in self.__dict__.items()]

        # Retourne le nom de la classe avec les attributs formatés
        return f"{self.__class__.__name__}(\n  " + ",\n  ".join(attributes) + "\n)"
