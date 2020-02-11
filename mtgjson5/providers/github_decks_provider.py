"""
Decks via GitHub 3rd party provider
"""
import itertools
import logging
import multiprocessing
import pathlib
from typing import Any, Dict, Iterator, List, Union

import requests
import simplejson as json
from singleton_decorator import singleton

from ..classes import MtgjsonMetaObject
from ..classes.mtgjson_deck import MtgjsonDeckObject
from ..compiled_classes import MtgjsonStructuresObject
from ..consts import OUTPUT_PATH
from ..providers.abstract_provider import AbstractProvider

LOGGER = logging.getLogger(__name__)


@singleton
class GithubDecksProvider(AbstractProvider):
    """
    GithubDecksProvider container
    """

    decks_api_url: str = "https://raw.githubusercontent.com/taw/magic-preconstructed-decks-data/master/decks.json"
    all_printings_file: pathlib.Path = OUTPUT_PATH.joinpath(
        f"{MtgjsonStructuresObject().all_printings}.json"
    )
    all_printings_cards: Dict[str, Any]

    def __init__(self) -> None:
        """
        Initializer
        """
        super().__init__(self._build_http_header())

    def _build_http_header(self) -> Dict[str, str]:
        """
        Construct the Authorization header
        :return: Authorization header
        """
        return {}

    def download(self, url: str, params: Dict[str, Union[str, int]] = None) -> Any:
        """
        Download content from GitHub
        :param url: Download URL
        :param params: Options for URL download
        """
        session = requests.Session()

        response = session.get(url)
        self.log_download(response)

        return response.json()

    def iterate_precon_decks(self) -> Iterator[MtgjsonDeckObject]:
        """
        Iterate the pre-constructed headers file to generate
        full MTGJSON deck objects
        :return: Iterator of a deck object
        """
        if not self.all_printings_file.is_file():
            LOGGER.error("Unable to construct decks. AllPrintings not found")
            return

        if self.all_printings_file.stat().st_size <= 2000:
            LOGGER.error("Unable to construct decks. AllPrintings not fully formed")
            return

        with self.all_printings_file.open() as file:
            self.all_printings_cards = json.load(file)

        for deck in self.download(self.decks_api_url):
            this_deck = MtgjsonDeckObject()
            this_deck.name = deck["name"]
            this_deck.set_sanitized_name(this_deck.name)
            this_deck.code = deck["set_code"].upper()
            this_deck.type = deck["type"]
            this_deck.release_date = deck["release_date"]
            this_deck.meta = MtgjsonMetaObject()

            with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
                this_deck.main_board = list(
                    itertools.chain.from_iterable(
                        pool.map(build_single_card, deck["cards"])
                    )
                )
                this_deck.side_board = list(
                    itertools.chain.from_iterable(
                        pool.map(build_single_card, deck["sideboard"])
                    )
                )

            yield this_deck


def build_single_card(card: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Given a card, add components necessary to turn it into
    an enhanced MTGJSON card
    :param card: Card to enhance
    :return: List of enhanced cards in set
    """
    cards = []
    set_to_build_from = GithubDecksProvider().all_printings_cards[
        card["set_code"].upper()
    ]
    for mtgjson_card in set_to_build_from["cards"]:
        if "//" in card["name"]:
            if card["number"][-1].isalpha():
                card["number"] = card["number"][:-1]

        if mtgjson_card["number"] == card["number"] or (
            mtgjson_card.get("multiverseId", "zNone") == card.get("multiverseid")
        ):
            mtgjson_card["count"] = card["count"]
            mtgjson_card["isFoil"] = card["foil"]
            cards.append(mtgjson_card)

    if not cards:
        LOGGER.warning(f"No matches found for {card}")

    return cards
