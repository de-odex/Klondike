from pyparsing import *

from .base import logger


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


def split_iter(to_split, seps):
    x = to_split
    for i in seps:
        x = '|'.join(x.split(i))
    return [s.strip() for s in x.split("|") if s.strip()]


class CommandParser:
    def __init__(self, game_obj):
        self.game_obj = game_obj
        self.command_list = [func for func in dir(self) if
                             callable(getattr(self, func)) and not (func.startswith("_") or func.endswith("__"))]

        # command (must have whitespace to separate) and everything else
        self.cmd = oneOf(self.command_list) + \
                   (Suppress(White()) + restOfLine ^ (Suppress(Empty()) ^ Suppress(White())))

        logger.debug(self.command_list)

    def _parse_many_(self, commands):
        # try:
        # take a card from the second deck and then put the card into the second deck
        # take a card from the fifth deck and put it into the fifth deck
        # take 2 cards from the first deck then put them into deck 4
        parsed = split_iter(commands, ['and', 'then'])
        for i in parsed:
            try:
                self._parse_(i)
            except ParseException as e:
                logger.exception("")
                print(f"Invalid commands: {i}\nException: {e}")
            except Exception as e:
                print(f"Command error: {i}\nException: {e}")

    def _parse_(self, command):
        parsed = self.cmd.parseString(command, parseAll=True)
        getattr(self, parsed[0])(parsed)

    _cards = oneOf(["card", "cards"])
    _cards_put = oneOf(["them", "the", "these"])
    _card_start = OneOrMore(~_cards + Word(alphanums)).setResultsName('card_amount') + \
                  Suppress(_cards)
    _card_end = Or([
        Suppress("deck") + Word(alphanums).setResultsName('deck_identifier'),
        Suppress("the") + Word(alphanums).setResultsName('deck_identifier') + Suppress("deck")
    ])

    def take(self, parsed):
        # test these:
        # take 3 cards from deck 2
        # take twenty two cards from deck 2
        # take a card from the second deck

        take = self._card_start + Suppress("from") + self._card_end
        parsed = take.parseString(parsed[1])

        card_amount = parse_number(parsed.card_amount)
        deck_identifier = parse_number(parsed.deck_identifier)

        self.game_obj.take(card_amount, deck_identifier - 1)

    def put(self, parsed):
        put = ((Optional(self._cards_put) + Optional(self._cards)) ^ Literal("it")) + \
              Suppress(oneOf(["in to", "into"])) + self._card_end
        parsed = put.parseString(parsed[1])

        deck_identifier = parse_number(parsed.deck_identifier)

        self.game_obj.put(deck_identifier - 1)

    def help(self, parsed):
        pass
