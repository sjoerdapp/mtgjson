"""
MTGJSON container for holding an individual card
"""
import re
from typing import Any, Dict, List

from ..classes.mtgjson_meta import MtgjsonMetaObject
from ..utils import to_camel_case


class MtgjsonDeckObject:
    """
    MTGJSON's container for a card
    """

    code: str
    main_board: List[Dict[str, Any]]  # MtgjsonCardObject
    meta: MtgjsonMetaObject
    name: str
    side_board: List[Dict[str, Any]]  # MtgjsonCardObject
    release_date: str
    type: str
    file_name: str

    def __init__(self) -> None:
        pass

    def set_sanitized_name(self, name: str) -> None:
        """
        Turn an unsanitary file name to a safe one
        :param name: Unsafe name
        """
        word_characters_only_regex = re.compile(r"[^\w]")
        capital_case = "".join(x for x in name.title() if not x.isspace())

        self.file_name = word_characters_only_regex.sub("", capital_case)

    def for_json(self) -> Dict[str, Any]:
        """
        Support json.dumps()
        :return: JSON serialized object
        """
        skip_keys = {"file_name"}

        return {
            to_camel_case(key): value
            for key, value in self.__dict__.items()
            if "__" not in key and not callable(value) and key not in skip_keys
        }
