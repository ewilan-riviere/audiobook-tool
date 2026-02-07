from typing import Any
from datetime import datetime


class AutoRepr:
    """Mixin pour ajouter un __repr__ automatique aux classes."""

    def __repr__(self) -> str:
        def format_val(v: Any) -> str:
            # Gestion spécifique pour datetime
            if isinstance(v, datetime):
                return f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
            # repr(None) retournera la chaîne 'None' sans guillemets, ce qui est standard
            return repr(v)

        # Génération de la liste des attributs présents dans l'instance
        attributes = [f"{k}={format_val(v)}" for k, v in self.__dict__.items()]

        return f"{self.__class__.__name__}(\n  " + ",\n  ".join(attributes) + "\n)"
