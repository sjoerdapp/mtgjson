"""
MTGJSON container for rulings
"""
from typing import Any, Dict

from ..utils import to_camel_case


class MtgjsonRulingObject:
    """
    Ruling object
    """

    date: str
    text: str

    def __init__(self, date: str, text: str) -> None:
        self.date = date
        self.text = text

    def for_json(self) -> Dict[str, Any]:
        """
        Support json.dumps()
        :return: JSON serialized object
        """
        return {
            to_camel_case(key): value
            for key, value in self.__dict__.items()
            if "__" not in key and not callable(value)
        }
