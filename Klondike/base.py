import logging

from . import game

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    game = game.Game()

    game.take(1, int(input("take from where: "))).put(int(input("put where: ")))

