from . import card
from .base import logger
import itertools


class TableauPile:
    def __init__(self):
        self.hidden_deck = card.HiddenDeck()
        self.shown_deck = card.ShownDeck()

        self.current = 0

    def take(self, n: int = 1) -> card.Card or card.Iterable:
        x = self.shown_deck.take(n)
        if not self.shown_deck and self.hidden_deck:
            self.shown_deck.put(self.hidden_deck.take(1))
        return x

    def put(self, puts_card: card.Card or card.Iterable):
        self.shown_deck.put(puts_card)

    @property
    def deck(self):
        return self.shown_deck.deck

    def __getitem__(self, item):
        return self.shown_deck[item]

    def __repr__(self):
        return f"<{type(self).__qualname__}: hidden={repr(self.hidden_deck)}, shown={repr(self.shown_deck)}>"

    def __str__(self):
        return " ".join(i.short for i in self.iterator_deck)

    def __len__(self):
        return len(self.hidden_deck) + len(self.shown_deck)

    @property
    def iterator_deck(self):
        return [*self.hidden_deck, *self.shown_deck]

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= len(self.iterator_deck):
            raise StopIteration
        else:
            self.current += 1
            return self.iterator_deck[self.current - 1]


class SuitDeck(card.CardDeck):
    def __init__(self, suit: card.CardSuit, full=False):
        self._suit = suit
        super().__init__(full)

    def __put(self, puts_card: card.Card):
        if self._suit == puts_card.suit:
            if puts_card.face == card.CardFace.ACE if not self.deck else \
                    puts_card.face.value - self.deck[-1].face.value == 1:
                self._deck.append(puts_card)
            else:
                raise ValueError("Card face is not after deck's last card face")
        else:
            raise ValueError("Card does not match deck")

    def take(self, n=0):
        raise NotImplementedError

    def __repr__(self):
        return f"<{type(self).__qualname__}: " \
            f"[{', '.join([repr(i) for i in self._deck]).strip()}], suit={self._suit}>"


class MoveError(Exception):
    pass


class Game:
    def __init__(self):
        self.stock_deck = card.StockDeck(full=True)

        # decks are generated left to right
        self.decks = [TableauPile() for __ in range(7)]
        for i, v in enumerate(self.decks):
            for __ in range(i + 1):
                v.hidden_deck.put(self.stock_deck.take())
            # show one card
            v.shown_deck.put(v.hidden_deck.take())
        self.foundations = [SuitDeck(k) for k in card.CardSuit]
        self.hand_deck = card.CardDeck()

    def debug(self):
        logger.debug(f"stock deck: {self.stock_deck}")

        x = '\n'.join(["deck " + str(i + 1) + ": " + str(v) for i, v in enumerate(self.decks)])
        logger.debug(f"TableauPile: \n{x}")

        logger.debug(f"foundations: {self.foundations}")
        logger.debug(f"hand: {self.hand_deck}")

    def move_info(self):
        print("""XX CN    CN CN CN CN

CN XX XX XX XX XX XX
   CN XX XX XX XX XX
      CN XX XX XX XX
         CN XX XX XX
            CN XX XX
               CN XX
                  CN""")

    def place(self, take_number: int, take_index: int, put_index: int):
        to_take = self.decks
        to_put = self.decks

        if take_index == put_index:
            # y tho
            raise MoveError("cannot take and put to the same deck")

        if take_index == 0:
            if take_number > 1:
                raise MoveError("can only take 1 card at a time from the main deck")
            to_take = self.stock_deck

        if take_index ^ 0b10000 < 0b10000:
            to_take = self.foundations
            take_index ^= 0b10000

        if put_index == 0:
            raise MoveError("cannot place cards into main deck")

        if put_index ^ 0b10000 < 0b10000:
            to_put = self.foundations
            put_index ^= 0b10000

        if self.peek_verify(put_index, to_take[take_index].deck[-1]):
            self.hand_deck.put(to_take[take_index].take(take_number))
            to_put[put_index].put(self.hand_deck.take(card.MAX_CARDS))
            return self
        else:
            raise MoveError("invalid move")

    def peek_verify(self, deck_index: int, peeked_card: card.Card) -> bool:
        if self.decks[deck_index]:
            return self.decks[deck_index][-1].face.value - peeked_card.face.value == 1 \
                   and not peeked_card.suit.is_same_color(self.decks[deck_index][-1].suit)
        else:
            return card.CardFace.KING == peeked_card.face.value

    def is_finished(self) -> bool:
        return any(len(i) for i in self.foundations)

    def __bool__(self) -> bool:
        return not self.is_finished()
