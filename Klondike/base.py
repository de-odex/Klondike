import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

from . import parser
from . import game

if __name__ == '__main__':
    parser_obj = parser.CommandParser(game.Game())

    while True:
        cmd = input(" >>> ")
        parser_obj._parse_(cmd)
