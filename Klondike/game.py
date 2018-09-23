from . import card


class KlondikeDeck(card.CardDeck):
    def __repr__(self):
        if self._deck:
            return repr(self._deck[-1])
        else:
            return "Empty deck"


class Game:
    def __init__(self):
        self.decks = []
