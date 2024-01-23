"""
Reading and writing Sudoku boards.  We use the minimal
subset of the SadMan Sudoku ".sdk" format,
see http://www.sadmansoftware.com/sudoku/faq19.php

Author: M Young, January 2018
"""

import sdk_board
from sdk_config import NROWS
from typing import List, Union
from io import IOBase

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



class InputError(Exception):
    pass


def read(f: Union[IOBase, str],
         board: sdk_board.Board=None) -> sdk_board.Board:
    """Read a Sudoku board from a file.  Pass in a path
    or an already opened file.  Optionally pass in a board to be
    filled.
    """
    if isinstance(f, str):
        log.debug("Reading from string")
        f = open(f, "r")
    else:
        log.debug(f"Reading from file {f}")
    if board is None:
        board = sdk_board.Board()
    values = []
    for row in f:
        row = row.strip()
        log.debug(f"Reading row |{row}|")
        values.append(row)
        if len(row) != NROWS:
            raise InputError("Puzzle row wrong length: {}"
                             .format(row))
    log.debug(f"Read values: {values}")
    if len(values) != NROWS:
        raise InputError("Wrong number of rows in {}"
                         .format(values))
    board.set_tiles(values)
    f.close()
    return board




