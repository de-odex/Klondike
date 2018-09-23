import logging

from . import card, game

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    base_deck = card.CardDeck(full=True)

    test = game.KlondikeDeck()

    test2 = card.Card("QH")
    # card = test.deal()
    logger.debug(test)
    logger.debug(len(test))
