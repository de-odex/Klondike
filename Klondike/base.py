import logging

from . import game

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    game = game.Game()
    logger.debug(game.base_deck)
    logger.debug([str(i) for i in game.decks])
    logger.debug(game.foundations)