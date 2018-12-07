import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

from . import parser
from . import game

if __name__ == '__main__':
    game_obj = game.Game()
    parser_obj = parser.CommandParser(game_obj)

    while True:
        cmd = input(" >>> ")
        parser_obj._parse_(cmd)

        if not game_obj:
            break

    print("done")
