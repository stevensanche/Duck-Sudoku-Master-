"""Sudoku solver with optional displays"""

import argparse
import sdk_display
import sdk_reader

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def cli() -> object:
    """Get arguments from command line"""
    parser = argparse.ArgumentParser(description="Sudoku solver")
    parser.add_argument("-d", "--display", help="Graphical display",
                        action="store_true")
    parser.add_argument("file", type=argparse.FileType('r'))
    args = parser.parse_args()
    return args


def main():
    args = cli()
    board = sdk_reader.read(args.file)
    if args.display:
        display = sdk_display.Board(board, 800, 800)
        # pause = input("Press enter to continue")
    if board.is_consistent():
        # Pause if there is a display
        if args.display:
            input("Press enter to solve")
        board.solve()
        assert board.is_consistent()
    else:
        print("Board has duplicates; rejected")
    print(board)

    if args.display:
        input("Press enter to shut down")
        display.close()



if __name__ == "__main__":
    main()
