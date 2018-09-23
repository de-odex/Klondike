from typing import Iterable

from . import card


class KlondikeDeck(card.CardDeck):
    def __repr__(self):
        if self._deck:
            return repr(self._deck[-1])
        else:
            return "Empty deck"

    def put(self, puts_card: card.Card or Iterable):
        try:
            puts_card = iter(puts_card)
            for i in puts_card:
                self._deck.append(i)
        except TypeError:
            self._deck.append(puts_card)


class Game:
    def __init__(self):
        self.decks = {}
