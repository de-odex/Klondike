import enum
import random
from typing import Iterable


class CardFace(enum.Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    def __str__(self):
        """
        String representation of a PlayingCardFace.
        """
        return str(self.value)

    def repr_word(self):
        """
        The word for the face of a PlayingCard.
        """
        values = ("ace", "two", "three",
                  "four", "five", "six",
                  "seven", "eight", "nine",
                  "ten", "jack", "queen",
                  "king")
        return values[self.value - 1]

    def repr_char(self):
        """
        Character representation of a PlayingCardFace.
        """
        values = ("A", "2", "3", "4", "5", "6", "7", "8",
                  "9", "T", "J", "Q", "K")
        return values[self.value - 1]

    @staticmethod
    def match_value(value):
        """
        Method to match a character to the first letter of the string
        representation of a PlayingCardSuit and return the instance of
        the PlayingCardSuit. This is a convenience method to allow the
        constructor of the PlayingCard class to accept a string.
        """
        for face in CardFace:
            if face.repr_char() == value:
                return face


class CardSuit(enum.Enum):
    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    HEARTS = "hearts"
    SPADES = "spades"

    @staticmethod
    def match_char(char):
        """
        Method to match a character to the first letter of the string
        representation of a PlayingCardSuit and return the instance of
        the PlayingCardSuit. This is a convenience method to allow the
        constructor of the PlayingCard class to accept a string.
        """
        if char[0].upper() == "C":
            return CardSuit.CLUBS
        if char[0].upper() == "D":
            return CardSuit.DIAMONDS
        if char[0].upper() == "H":
            return CardSuit.HEARTS
        if char[0].upper() == "S":
            return CardSuit.SPADES

    def is_same_color(self, other):
        """
        Method to check whether one suit is the same as another.
        """
        self_color = "black" if self in [CardSuit.CLUBS, CardSuit.SPADES] else "red"
        other_color = "black" if other in [CardSuit.CLUBS, CardSuit.SPADES] else "red"

        return self_color == other_color


class Card:
    """
    A PlayingCard represents a standard card in a
    standard 52-card deck.
    """

    def __init__(self, suit=None, face=None):
        """
        Constructs a PlayingCard. The suit can be a PlayingCardSuit or
        a one-character string that matches the first letter of the
        defined suits. The face value can be a PlayingCardFace or a
        number that maps to the defined face values.
        """
        if suit:
            if type(suit) == CardSuit:
                self.__suit = suit
            elif type(suit) == str:
                self.__suit = CardSuit.match_char(suit)
        else:
            raise ValueError

        if face:
            if type(face) == CardFace:
                self.__face = face
            elif type(face) == str:
                self.__face = CardFace.match_value(face)
        else:
            if suit and type(suit) == str:
                self.__suit = CardSuit.match_char(suit[1])
                self.__face = CardFace.match_value(suit[0])
            else:
                raise ValueError

    def __str__(self):
        return self.__face.repr_word() + " of " + self.__suit.value

    def __repr__(self):
        return f"<{type(self).__qualname__}: face={self.__face.repr_word()}, suit={self.__suit.value}>"

    @property
    def short(self):
        return self.__face.repr_char() + self.__suit.value.upper()[0]

    @property
    def face(self):
        return self.__face

    @property
    def suit(self):
        return self.__suit

    def __lt__(self, other: lambda: Card):
        return self.face.value < other.face.value

    def __gt__(self, other: lambda: Card):
        return self.face.value > other.face.value

    def __eq__(self, other: lambda: Card):
        return self.face.value == other.face.value


class CardDeck:
    def __init__(self, full=False):
        self._deck = []

        if full:
            self.fill()
            self.shuffle()

    def fill(self):
        for suit in CardSuit:
            for face in CardFace:
                self._deck.append(Card(suit, face))

    def clear(self):
        self._deck = []

    def shuffle(self):
        random.shuffle(self._deck)

    def deal(self) -> Card:
        return self._deck.pop()

    def put(self, puts_card: Card or Iterable):
        try:
            puts_card = iter(puts_card)
            for i in puts_card:
                self.__put(i)
        except TypeError:
            self.__put(puts_card)

    def __put(self, puts_card: Card):
        self._deck.append(puts_card)

    @property
    def deck(self) -> list:
        return self._deck

    def __len__(self):
        return len(self._deck)

    def __str__(self):
        if self._deck:
            if len(self._deck) <= 5:
                return ', '.join([str(i) for i in self._deck])
            return ' '.join([i.short for i in self._deck])
        else:
            return "Empty deck"

    def __repr__(self):
        return f"<{type(self).__qualname__}: [{', '.join([repr(card) for card in self._deck]).strip()}]>"
