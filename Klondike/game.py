from . import card


class KlondikeDeck:
    def __init__(self):
        self._hidden_deck = card.CardDeck()
        self._shown_deck = card.CardDeck()

    def __repr__(self):
        return f"<{type(self).__qualname__}: hidden={repr(self._hidden_deck)}, shown={repr(self._shown_deck)}>"

    def __str__(self):
        return f"hidden: {self._hidden_deck}, shown: {self._shown_deck}"


class SuitDeck(card.CardDeck):
    def __init__(self, suit: card.CardSuit, full=False):
        self._suit = suit
        super().__init__(full)

    def __put(self, puts_card: card.Card):
        if self._suit == puts_card.suit:
            if (self.deck and puts_card.face.value - self.deck[-1].face.value == 1) or \
                    (not self.deck and puts_card.face == card.CardFace.ACE):
                self._deck.append(puts_card)
            else:
                raise ValueError("Card face is not after deck's last card face")
        else:
            raise ValueError("Card does not match deck")

    def deal(self):
        raise NotImplementedError

    def __repr__(self):
        return f"<{type(self).__qualname__}: " \
               f"[{', '.join([repr(card) for card in self._deck]).strip()}], suit={self._suit}>"


class Game:
    def __init__(self):
        self.base_deck = card.CardDeck(full=True)

        # decks are generated left to right
        self.decks = [KlondikeDeck() for __ in range(7)]
        for i, v in enumerate(self.decks):
            for __ in range(i + 1):
                v._hidden_deck.put(self.base_deck.deal())

            # show one card
            v._shown_deck.put(v._hidden_deck.deal())

        self.foundations = {k.value: SuitDeck(k) for k in card.CardSuit}
