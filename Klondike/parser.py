from pyparsing import *

from .base import logger
from .game import Game, MoveError


class ConversionException(Exception):
    pass


def text2int(textnum, numwords={}):
    if textnum == "a":
        return 1

    # taken from https://stackoverflow.com/a/598322
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)

    ordinal_words = {'first': 1, 'second': 2, 'third': 3, 'fifth': 5, 'eighth': 8, 'ninth': 9, 'twelfth': 12}
    ordinal_endings = [('ieth', 'y'), ('th', '')]

    textnum = textnum.replace('-', ' ')

    current = result = 0
    for word in textnum.split():
        if word in ordinal_words:
            scale, increment = (1, ordinal_words[word])
        else:
            for ending, replacement in ordinal_endings:
                if word.endswith(ending):
                    word = "%s%s" % (word[:-len(ending)], replacement)

            if word not in numwords:
                raise ConversionException("Illegal word: " + word)

            scale, increment = numwords[word]

        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def list2text(lst):
    try:
        if type(lst) == str:
            raise TypeError
        iter(lst)
        return ' '.join(lst)
    except TypeError:
        return lst


def parse_number(number):
    try:
        return text2int(list2text(number))
    except ConversionException:
        return int(list2text(number))


class CommandParser:
    def __init__(self, game_obj):
        self.game_obj: Game = game_obj
        self.command_list = [func for func in dir(self) if
                             callable(getattr(self, func)) and not (func.startswith("_") or func.endswith("__"))]

        # command (must have whitespace to separate) and everything else
        self.cmd = oneOf(self.command_list) + \
                   (Suppress(White()) + restOfLine ^ (Suppress(Empty()) ^ Suppress(White())))

        logger.debug(self.command_list)

    def _parse_(self, command):
        try:
            parsed = self.cmd.parseString(command, parseAll=True)
            getattr(self, parsed[0])(parsed)
        except ParseException as e:
            logger.exception("")
            print(f"Invalid command: {command}\nException: {e}")
        except Exception as e:
            logger.exception("")
            print(f"Command error: {command}\nException: {e}")

    _cards = oneOf(["card", "cards"])
    _card_start = OneOrMore(~_cards + Word(alphanums)).setResultsName('card_amount') + \
                  Suppress(_cards)

    def debug(self, parsed):
        self.game_obj.debug()

    def place(self, parsed):
        deck_identifier_parser = lambda name: Or(
                [Suppress("deck") + Word(alphanums).setResultsName(f'deck_identifier_{name}'),
                 Suppress("the") + Word(alphanums).setResultsName(f'deck_identifier_{name}') + Suppress("deck")])

        place = self._card_start + Suppress("from") + deck_identifier_parser("1") + \
                Suppress("into") + deck_identifier_parser("2")
        parsed = place.parseString(parsed[1])

        deck_identifier = (parse_number(parsed.deck_identifier_1) if parsed.deck_identifier_1 != "main" else 0,
                           ["clubs", "diamonds", "hearts", "spades"].index(parsed.deck_identifier_2) + 0b10000
                           if any(parsed.deck_identifier_1 == i for i in ["clubs", "diamonds", "hearts", "spades"])
                           else parse_number(parsed.deck_identifier_2))
        card_amount = parse_number(parsed.card_amount)

        if len(self.game_obj.decks[deck_identifier[0] - 1].deck) < card_amount:
            raise MoveError("not enough cards to take")

        self.game_obj.place(card_amount, deck_identifier[0] - 1, deck_identifier[1] - 1)
        self.info("")

    def draw(self, parsed):
        self.game_obj.stock_deck.pass_card()

        self.info("")

    def info(self, parsed):
        self.game_obj.move_info()

    def help(self, parsed):
        raise NotImplementedError
