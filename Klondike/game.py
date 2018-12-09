import itertools
from collections import namedtuple

from . import card
from .base import logger


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

    def verify(self, verify_card: card.Card) -> bool:
        if self.shown_deck:
            logger.debug(f"card is less than floor: {self.shown_deck[-1].face.value - verify_card.face.value == 1}")
            logger.debug(f"card of different color: {not verify_card.suit.is_same_color(self.shown_deck[-1].suit)}")
            return self.shown_deck[-1].face.value - verify_card.face.value == 1 \
                   and not verify_card.suit.is_same_color(self.shown_deck[-1].suit)
        else:
            logger.debug(f"card is king: {card.CardFace.KING == verify_card.face.value}")
            return card.CardFace.KING == verify_card.face.value

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

    def short_iter(self):
        hi = self.hidden_deck.short_iter()
        si = self.shown_deck.short_iter()
        if not self.hidden_deck and not self.shown_deck:
            return hi
        else:
            return [*(hi if hi != ["[]"] else []), *(si if si != ["[]"] else [])]

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= len(self.iterator_deck):
            self.current = 0
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
                raise ValueError("card face is not after deck's last card face")
        else:
            raise ValueError("card does not match deck")

    def verify(self, verify_card: card.Card) -> bool:
        if self._deck:
            logger.debug(f"card is greater than floor: {self._deck[-1].face.value - verify_card.face.value == -1}")
            logger.debug(f"card is same suit as pile: {verify_card.suit == self._suit}")
            return self._deck[-1].face.value - verify_card.face.value == -1 \
                   and verify_card.suit == self._suit
        else:
            logger.debug(f"card is ace: {card.CardFace.ACE == verify_card.face}")
            logger.debug(f"card is same suit as pile: {verify_card.suit == self._suit}")
            return card.CardFace.ACE == verify_card.face and verify_card.suit == self._suit

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

        self.move_info()

    def debug(self):
        logger.debug(f"stock deck: {self.stock_deck}")

        x = '\n'.join(["deck " + str(i + 1) + ": " + str(v) for i, v in enumerate(self.decks)])
        logger.debug(f"TableauPile: \n{x}")

        logger.debug(f"foundations: {self.foundations}")
        logger.debug(f"hand: {self.hand_deck}")

    def move_info(self):
        lines = [
            ["XX", self.stock_deck[-1].short, "  ",
             *(v[-1].short if v else f"X{card.CardSuit.list()[i][0].upper()}" for i,v in enumerate(self.foundations))],
            [""],
            [f"d{i}" for i in range(1,8)]
        ]

        for i in itertools.zip_longest(*(x.short_iter() for x in self.decks), fillvalue="  "):
            lst = []
            for j in i:
                lst.append(j)
            lines.append(lst)

        logger.debug(f"lines: {lines}")
        print("\n".join(" ".join(i) for i in lines))

    def place(self, take_number: int, take_index: int, put_index: int):
        to_take = self.decks
        to_put = self.decks

        if take_index == put_index:
            # y tho
            raise MoveError("cannot take and put to the same deck")

        if take_index == -1:
            if take_number > 1:
                raise MoveError("can only take 1 card at a time from the main deck")
            to_take = [self.stock_deck]
        elif take_index ^ 0b10000 < 0b10000:
            to_take = self.foundations
            take_index ^= 0b10000

        if put_index == -1:
            raise MoveError("cannot place cards into main deck")
        elif put_index ^ 0b10000 < 0b10000:
            to_put = self.foundations
            put_index ^= 0b10000

        logger.debug(f"put: {to_put}, index: {put_index}")
        logger.debug(f"take: {to_take}, index: {take_index}")
        logger.debug(f"how many? {take_number}")
        logger.debug(f"put deck: {to_put[put_index]}, take deck: {to_take[take_index]}")

        if to_put[put_index].verify(to_take[take_index].deck[-take_number]):
            self.hand_deck.put(to_take[take_index].take(take_number))
            to_put[put_index].put(self.hand_deck.take(card.MAX_CARDS))
            return self
        else:
            raise MoveError("invalid move")

    def is_finished(self) -> bool:
        return any(len(i) == 13 for i in self.foundations)

    def __bool__(self) -> bool:
        return not self.is_finished()
