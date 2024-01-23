# Getting Started with Sudoku

The first part of the Sudoku solver to build is 
a representation of the board, a way to read 
Sudoku boards and to write them, and a 
checker that rejects boards that disobey 
the basic rules of Sudoku (e.g., because a 
tile value is repeated in some row, column, 
or block.)

## Basic Strategy

The instructions below begin with a description 
of Sudoku and of the solving strategy.  
Don't skip it, because the step-by-step 
instructions that follow won't make sense 
if you can't see where you are going. The 
step-by-step instructions begin in a section 
titled "Step 1", which is creating the 
Sudoku `Board` class.  It also describes how
to set up *logging* (very helpful in debugging), 
and once again we set up a Model-View-Controller
structure so that we can have a graphical 
view of the puzzle being solved. 

As in the FiveTwelve project, you will create a 
`Tile` class and a `Board` class, and a `Board` 
object will contain a list of lists of 
`Tile` objects.  The `Tile` objects for 
Sudoku are a good deal more complex than the 
`Tile` objects in FiveTwelve.  Each tile keeps 
track not only of the symbol it currently 
holds, but also of the symbols it *could* hold, 
constrained by the symbols currently held by 
other tiles in the same row, column, or block. 

A `Board` object will not only include a list
of lists of `Tile` objects, but will also 
contain a list containing lists of subsets of the tiles 
grouped in different ways.  You must devise 
part of the code to build these lists.  To 
understand what this structure is and why 
we are building it, be sure to read the 
[supplement on aliasing](https://uo-cis211.github.io/chapters/04_1_Alias).

You will also write a method `is_consistent` 
that determines whether a Sudoku board contains
any duplicate digits in a row, column, or block. 


## The input

Your program will read an input file in the
basic form of the .sdk (Sadman Sudoku) format.
An input file will look like this:

```
...26.7.1
68..7..9.
19...45..
82.1...4.
..46.29..
.5...3.28
..93...74
.4..5..36
7.3.18...
```

If there are duplicated elements, your program will reject the puzzle. 
If there are no duplicated entries in the board (and regardless
  of whether it is complete, with digits only, or has '.'
  characters indicating tiles yet to be filled), your program will
  proceed to the next step.  

For example, suppose the input board contained this:

```
435269781
682571493
197834562
826195347
374682915
951743628
519326874
248957136
963418257
```

Your program should reject this board. 

If you used the display option like this:
```
$ python3 sudoku.py --display boards/board1.sdk
```
then the program will display the board
as it attempts to solve it. 

## Consistency checking
  
Because of the pigeonhole principle of mathematics, if the board contains only the 
  digits 1..9, the following two statements are
  equivalent: 

  *  None of the 9 digits 1..9 appears more than once in a
  row. 

  * Each of the 9 digits 1..9 appear at least once in a row.

It is therefore enough to  check for duplicates.  Checking for
missing entries is similar but slightly more complicated,
particularly since we are allowing "open" tiles with the 
"." symbol. 

## Model View Controller, Again

As in our previous tile game, FiveTwelve, we will use a 
Model-View-Controller architecture for the graphical display. 
In FiveTwelve we always connected the view component to 
the model component, because the game would be difficult and not much
fun if we couldn't see the board.  In Sudoku, on the other hand, 
we may or may not want to watch the puzzle be solved.  The solver is 
much faster than the graphics, so if we care most about speed we may 
run our Sudoku solver without graphics (only printing the solution 
when it is complete).   Other times we may wish to attach the 
graphical display and watch the solution in progress.  The main 
program `sudoku.py` allows both approaches depending on a command-line 
argument.  

## Incremental, but with a plan

Although we will develop our solver incrementally, piece by piece, we 
have a vision of where we are going, including the solution techniques we 
intend to use.  Those solution techniques center on associating with 
each tile a set of *possible values*. We will design with that in 
mind from the beginning, storing in each tile a Python set representing
the candidate values.   

# Step 1: Basic Board

We will create sdk_board.py to hold our Board and Tile classes. 

```python
"""
A Sudoku board holds a matrix of tiles.
Each row and column and also sub-blocks
are treated as a group (sometimes called
a 'nonet'); when solved, each group must contain
exactly one occurrence of each of the
symbol choices.
"""
```

Several basic constants are defined in ```sdk_config.py```. 
That is where we determine the size of the puzzle 
and the symbols to be used in these 
puzzles (digits 1-9 for the 9x9 version of the puzzle). 

```python
from sdk_config import CHOICES, UNKNOWN, ROOT
from sdk_config import NROWS, NCOLS
```

```CHOICES``` will be the symbols (e.g., "123456789"), and
```UNKNOWN``` will be a symbol that indicates a tile that 
has not been solved; we will use "." for that, following 
the standard for puzzle representation set by Sadman Sudoku. 
We describe the size of the puzzle in two ways, for convenience. 
A 9x9 puzzle has 3x3 blocks, so we define that size puzzle as 
having ```NROWS``` and ```NCOLS``` equal 9 but ```ROOT```
(the rows and columns in each block) equal 3.  For a 16x16 puzzle, ROOT 
would be 4 (the square root of 16). 

For debugging it is often handy to have "logging" messages 
that can be turned on or off.  The Python logging package 
provides this.  We could set it to print all debugging 
messages: 

```python
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
```

When we don't want so many messages, we can set it to 
to a lower level of verbosity: 

```python
log.setLevel(logging.INFO)
```

We will use the Model-View-Controller architecture, so we'll need events 
generated in the model component (mostly Tile objects in ```sdk_board.py```)
and acted upon in the view component (```sdk_display.py``). 

```python
# --------------------------------
#  The events for MVC
# --------------------------------

class Event(object):
    """Abstract base class of all events, both for MVC
    and for other purposes.
    """
    pass
```

The view component will register listeners, so we need to 
define a ```Listener``` class that it can use: 

```python
# ---------------
# Listeners (base class)
# ---------------

class Listener(object):
    """Abstract base class for listeners.
    Subclass this to make the notification do
    something useful.
    """

    def __init__(self):
        """Default constructor for simple listeners without state"""
        pass

    def notify(self, event: Event):
        """The 'notify' method of the base class must be
        overridden in concrete classes.
        """
        raise NotImplementedError("You must override Listener.notify")
```

Differently from FiveTwelve, there won't actually be any interesting events 
on the board ... our tiles are not moving around!  All the events that 
will need to be displayed will be from individual tiles.  We'll define two 
of them.  `TileChanged` will be the event that indicates almost 
any change to a tile (either to the value it holds, or to the set 
of candidate values an unsolved tile *might* hold).  We'll distinguish 
one special kind of tile change for when we add the guess-and-check 
part of the solver.  It's nice to be able to visually distinguish 
*solving* a tile from just *guessing* its value, so we'll define a 
different event for changes that are made by guessing. 

To use the `enum.Enum` class, we'll need to import it near 
the beginning of the file: 

```python
import enum
```

Then we can create the enumeration of kinds of events: 

```python
# --------------------------------------
# Events and listeners for Tile objects
# --------------------------------------

class EventKind(enum.Enum):
    TileChanged = 1
    TileGuessed = 2
```

And we can define a class of events that includes 
the enumeration element: 

```python
class TileEvent(Event):
    """Abstract base class for things that happen
    to tiles. We always indicate the tile.  Concrete
    subclasses indicate the nature of the event.
    """

    def __init__(self, tile: 'Tile', kind: EventKind):
        self.tile = tile
        self.kind = kind
        # Note 'Tile' type is a forward reference;
        # Tile class is defined below

    def __str__(self):
        """Printed representation includes name of concrete subclass"""
        return f"{repr(self.tile)}"
```

Listeners that need to receive TileEvents, like our view component, 
will be TileListeners: 

```python
class TileListener(Listener):
    def notify(self, event: TileEvent):
        raise NotImplementedError(
            "TileListener subclass needs to override notify(TileEvent)")
```

Objects that produce TileEvents, on the other hand, will be 
Listenable.  It is not an accident that class ```Listenable``` looks a lot like ```GameElement``` in our 
FiveTwelve project. 

```python
class Listenable:
    """Objects to which listeners (like a view component) can be attached"""

    def __init__(self):
        self.listeners = [ ]

    def add_listener(self, listener: Listener):
        self.listeners.append(listener)

    def notify_all(self, event: Event):
        for listener in self.listeners:
            listener.notify(event)
```

Finally we are ready to define the Tile class.  


We will want it to know 
what row and column it occupies on the board, not because we will use that 
information in solving puzzles, but because it may be useful for the graphical 
display and in debugging.  We also know that if the tile value is unknown, 
we will want to keep track of the possible values that it *could* hold; this
can be represented as a set, which is a built-in type in Python.  If the 
tile value was given at the start, or if we had determined it, should we 
just represent that as a set with one value, or should we separately 
indicate its current value?  Just for for convenience we will keep it in a separate
field.  The value field will always contain either the special value 
UNKNOWN (defined in ```sdk_config.py```) or one of the values in 
CHOICES (also from ```sdk_config.py```).  The ```candidates``` set should 
be consistent with the ```value```.  

```python
# ----------------------------------------------
#      Tile class
# ----------------------------------------------

class Tile(Listenable):
    """One tile on the Sudoku grid.
    Public attributes (read-only): value, which will be either
    UNKNOWN or an element of CHOICES; candidates, which will
    be a set drawn from CHOICES.  If value is an element of
    CHOICES,then candidates will be the singleton containing
    value.  If candidates is empty, then no tile value can
    be consistent with other tile values in the grid.
    value is a public read-only attribute; change it
    only through the access method set_value or indirectly 
    through method remove_candidates.   
    """
```

We could initialize the tile this way: 

```python
    def __init__(self, row: int, col: int, value=UNKNOWN):
        super().__init__()
        assert value == UNKNOWN or value in CHOICES
        self.row = row
        self.col = col
        self.value = value
        if self.value == UNKNOWN:
            self.candidates = set(CHOICES)
        else: 
            self.candidates = { value }
```

However, we will be setting tile values and candidates in other 
places as we solve the puzzle, so we'll factor out that part of the 
initialization into a separate ```set_value``` method: 

```python
    def __init__(self, row: int, col: int, value=UNKNOWN):
        super().__init__()
        assert value == UNKNOWN or value in CHOICES
        self.row = row
        self.col = col
        self.set_value(value)

    def set_value(self, value: str):
        if value in CHOICES:
            self.value = value
            self.candidates = {value}
        else:
            self.value = UNKNOWN
            self.candidates = set(CHOICES)
        self.notify_all(TileEvent(self, EventKind.TileChanged))
```

It will also need a ```__str__``` method and a ```__repr__``` method, which 
I'll leave to you.  The string form of a tile should just be its value 
(which might be the symbol for UNKNOWN or one of the characters from CHOICES). 
It's repr should look like a call to create a tile, e.g., ```Tile(2, 2, '.')```. 

There is one more method we should give a Tile object. When we 
display the tile graphically, we will want to show candidate values 
for unsolved tiles in the form of "pencil marks".  We'll also need 
 to check candidates later for the *hidden single* solution tactic.  
 We'll provide 
a ```could_be``` method that checks whether a particular symbol 
belongs to the candidates set: 

```python
    def could_be(self, value: str) -> bool:
        """True iff value is a candidate value for this tile"""
        return value in self.candidates

```

That's a lot of code to write before any testing.  There isn't much we 
can do with a Tile object yet, but let's start an ```test_sdk.py``` file 
and fill in a few very basic tests. 

```python
"""Test cases for sdk.py"""

import unittest
from sdk_board import *
from sdk_config import *

class TestTileBasic(unittest.TestCase):

    def test_init_unknown(self):
        tile = Tile(3, 2, UNKNOWN)
        self.assertEqual(tile.row, 3)
        self.assertEqual(tile.col, 2)
        self.assertEqual(tile.value, '.')
        self.assertEqual(tile.candidates, set(CHOICES))
        self.assertEqual(repr(tile), "Tile(3, 2, '.')")
        self.assertEqual(str(tile), ".")

    def test_init_known(self):
        tile = Tile(5, 7, '9')
        self.assertEqual(tile.row, 5)
        self.assertEqual(tile.col, 7)
        self.assertEqual(tile.value, '9')
        self.assertEqual(tile.candidates, {'9'})
        self.assertEqual(repr(tile), "Tile(5, 7, '9')")
        self.assertEqual(str(tile), "9")


if __name__ == "__main__":
    unittest.main()
```

I could have broken them down into a larger number of separate test cases, 
but I want to keep it short and seeing only the first error in each of these test cases is ok since I 
can simply debug and repair them one by one. 

Now we can build the most basic version of our Board class, with a way 
to initialize it from a list: 

```python
# ------------------------------
#  Board class
# ------------------------------

class Board(object):
    """A board has a matrix of tiles"""

    def __init__(self):
        """The empty board"""
        # Row/Column structure: Each row contains columns
        self.tiles: List[List[Tile]] = [ ]
        for row in range(NROWS):
            cols = [ ]
            for col in range(NCOLS):
                cols.append(Tile(row, col))
            self.tiles.append(cols)
```

Note that we gave a type annotation on the 
empty list of tiles.  Without the annotation, 
PyCharm would only know that `self.tiles` is some 
kind of list, and would not be able to warn
us if we appended the wrong kind of 
elements.  PyCharm will complain about this 
annotation until we add another import
at the beginning of the file: 

```python
from typing import List
```

We would like to be able to "load" a board from a list of lists, 
as we did for FiveTwelve boards.  However, it is tedious to write 
a value like 
```python
[ ['.', '.', '.', '.', '.', '.', '.', '.', '.'], 
  ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
  ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
  ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
  ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
  ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
  ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
  ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
  ['.', '.', '.', '.', '.', '.', '.', '.', '.']]
```

It would be convenient to also allow the list to 
look like 

```python
[".........", ".........", ".........", 
 ".........", ".........", ".........", 
 ".........", ".........", "........."]
```

Since both ```list``` and ```str``` fit the Python abstract 
type ```Sequence```, we will add 

```python
from typing import Sequence
```

Since we also used the List type annotation 
and we will soon at the Set type as well, 
we might as well consolidate the imports: 

```python
from typing import Sequence, List, Set
```

Then we can specify that any Sequence type, 
including both `str` and `list`, 
can be used to set the tile values: 

```python           
    def set_tiles(self, tile_values: Sequence[Sequence[str]] ):
        """Set the tile values a list of lists or a list of strings"""
        for row_num in range(NROWS):
            for col_num in range(NCOLS):
                tile = self.tiles[row_num][col_num]
                tile.set_value(tile_values[row_num][col_num])
```

Now we can add a bit to our test suite: 

```python
class TestBoardBuild(unittest.TestCase):

    def test_initial_board(self):
        board = Board()
        sample_tile = board.tiles[0][0]
        self.assertEqual(sample_tile.value, '.')
        sample_tile = board.tiles[3][3]
        self.assertEqual(sample_tile.value, '.')
        sample_tile = board.tiles[8][8]
        self.assertEqual(sample_tile.value, '.')

    def test_load_board(self):
        board = Board()
        board.set_tiles(["123456789", "2345678991", "345678912",
                         "456789123", "567891234", "678912345",
                         "789123456", "891234567", "912345678"])
        sample_tile = board.tiles[0][0]
        self.assertEqual(sample_tile.value, '1')
        sample_tile = board.tiles[3][5]
        self.assertEqual(sample_tile.value, '9')
        sample_tile = board.tiles[8][8]
        self.assertEqual(sample_tile.value, '8')
```

We're going to want to read puzzles from files.  I have provided
```sdk_reader.py``` for that purpose.  It uses the 
```set_tiles``` method of ```sdk_board.Board```.  It reads 
boards in a subset of the "Sadman Sudoku" (sdk) format, to give us 
access to lots of sample puzzles. 

```
f = open("data/102-ns1-board.sdk")
board = sdk_reader.read(f)
print(board)
<sdk_board.Board object at 0x108ccfa90>
```

The printed form is not very satisfying.  We'll define a 
```__str__``` method for Board that produces a string in the 
same format as the sdk files we read.   It could probably 
be compressed to one line of code with nested list 
comprehensions, but I don't think I could read and 
understand that. On the other hand, I don't want a 20 line 
 method with nested loops.  Here is a reasonably compact definition 
that is (I think) fairly readable: 

```python
    def __str__(self) -> str:
        """In Sadman Sudoku format"""
        row_syms = [ ]
        for row in self.tiles:
            values = [tile.value for tile in row]
            row_syms.append("".join(values))
        return "\n".join(row_syms)
```

And of course a test case for it ... 

```python
class TestBoardIO(unittest.TestCase):

    def test_read_new_board(self):
        board = sdk_reader.read(open("data/00-nakedsubset1.sdk"))
        as_printed = str(board)
        self.assertEqual(as_printed,
            "32...14..\n9..4.2..3\n..6.7...9\n8.1..5...\n...1.6...\n...7..1.8\n1...9.5..\n2..8.4..7\n..45...31")
```

## Are we ready to solve something? 

So far we've got a representation for the board and for tiles, and we 
can read puzzle files and print them.  Before moving on to 
puzzle solving, it would be reassuring and possibly useful to 
build the simplest thing we can that uses the representation of 
candidate lists in tiles. 

One thing we can build now is a check to see whether a partially 
solved board contains any duplicate tiles in a row, column, or block. 
For each row, column, or block, we can build a set of used symbols.
We could do this in many ways, e.g., by counting how many times each 
symbol appears in the group, and rejecting a group if any of the counts 
is greater than 1. Since we are planning to use *sets* of candidates 
in tiles, we slightly prefer an approach that also uses that representation.  

In pseudocode, we can design an algorithm like this: 

``` 
for each group (row, column, or block): 
    used symbols = { }
    for each tile in the group: 
        if the tile is one of CHOICES (anything but UNKNOWN): 
           if the tile's symbol is already in used symbols: 
               return False (board is not consistent)
           else: 
               add the tile's symbol to the used symbols
return True  (the solved part of the board is ok so far)
```

This doesn't look too bad, but when we start trying to turn it 
into Python, we notice that the line

``` 
for each group (row, column, or block): 
```

is really hard to program in a nice DRY way.  Looping through the rows, and tiles in each row
is easy enough.  Looping through the columns is a bit more complex, but 
not too bad.   Looping through the blocks is a good deal more 
complex, but we can figure it out.   But how in the world do we 
combine those into one loop?  Looping through the rows and looping
through the colunns and looping through the blocks all seem to 
require different logic.  We don't want to write the rest of the 
algorithm three times! 

The prospect of duplicating this logic for each kind of group 
is made doubly unattractive when we consider that we will almost 
certainly need to do something similar for each kind of solution 
tactic we apply.   We want to apply multiple techniques that
treat different kinds of groups (rows, columns, and blocks) in the 
same way. We don't want to duplicate each technique three times!  

## Factoring out group formation

We could make 

``` 
   for each group (row, column, or block):
```

quite simple if we just had a list of groups, where each 
group was a list of the tiles in that group.  We'd still have 
to write the three kinds of loop (one for rows, one for columns, 
and one for blocks), but we could write them just once to build up
the list of groups.  That's what we'll do. 

We will add a new instance variable to the Board representation:  
A list of groups, i.e., a list of lists of tiles.   
We can create it in the constructor. The rows 
can be copied directly from the tiles variable: 

```python
        for row in self.tiles: 
            self.groups.append(row)
```

This is just a copy of self.tiles, but we need the copy because we 
will append additional groups to it.  (Note that ```set_tiles``` 
only changes the values of the tiles, without replacing the Tile objects, 
so it is ok for us to create the groups before the tile values 
have been set.) 

Adding groups for columns is not too difficult.  I'll leave that 
to you.  

The most complex groups to build are the blocks.  For example, 
in a 9x9 board, the blocks are 3x3 with upper left corners at 
(0,0), (0,3), (0,6), (3,0), (3,3), (3,6), (6,0), (6,3), (6,6). 
We want to do this in a way that will also work for other size 
boards.  The ```ROOT``` constant from ```sdk_config.py``` 
gives us the width and height 
of a single block.  The upper left corner of block r,c is 
ROOT * r, ROOT * c, and the tile at position i,j within a block 
is at position ROOT * r + i, ROOT * c + j within the tiles list. 

```python
        for block_row in range(ROOT):
            for block_col in range(ROOT):
                group = [ ] 
                for row in range(ROOT):
                    for col in range(ROOT):
                        row_addr = (ROOT * block_row) + row
                        col_addr = (ROOT * block_col) + col
                        group.append(self.tiles[row_addr][col_addr])
                self.groups.append(group)
```

## How are we going to test this? 

I'm not too worried about the row groups.  The column groups are
a bit more complex, and ought to be tested.  I think I got the logic 
for forming block groups right, but it certainly needs testing. 
But how am I going to do that?   For a 9x9 puzzle, there are 9+9+9 groups; 
I certainly don't want to write a test case in which I manually 
specify what should be in each group (and I wouldn't trust myself
to get it right).  What can I do? 

When we can't directly specify what a result should be, sometimes 
we can specify properties of a result that are easier to check.  We want 
to choose a property that would be likely to be violated if our 
code is buggy.   For example, I know that each tile 
 should appear 
in three different groups (one row, one column, and one block).  If 
I messed up the group formation, it seems likely that I would also 
mess up that property.  So, let's use it to write a test case. 

```python
class TestBoardGroups(unittest.TestCase):

    def test_count_tile_groups(self):
        """Every tile should appear in exactly three groups
        (regardless of board size).
        """
        board = Board()
        counts = { }
        for group in board.groups:
            for tile in group:
                if tile not in counts:
                    counts[tile] = 0
                counts[tile] += 1
        for tile in counts:
            self.assertEqual(counts[tile], 3)        
```

The test case is not perfect.  It's conceivable that I could 
mess up the group formation and still pass the test.  But it's
good enough to give me enough confidence to go on.  

Or so I thought.  In Winter 2019, many student projects passed this 
test but failed later tests because they created duplicate groups. 
Each tile appeared in exactly three groups, but two of those three 
were duplicates!   One of the ways we design test cases is by 
observing prior failures (especially those that were difficult to debug, 
or managed to slip through to the product as shipped to users) and 
devise test cases designed to catch those particular errors or 
errors very much like them.  So, I need to add a test case for 
detecting a group that contains the same Tile objects as any 
other group.  How? 

The obvious approach to checking for duplicates is to build a 
dictionary.  Unfortunately, though, lists cannot be dict keys, 
because they are mutable: 

```
d = { }
d[[1, 2, 3]] = "forbidden"
Traceback (most recent call last):
  File "<input>", line 1, in <module>
TypeError: unhashable type: 'list'
```

Moreover, the list of tiles wouldn't make a good key even if I 
could use it, because I want "duplicate" to mean "contains the same tiles", 
even if they are in a different order. 

What I want is a fingerprint for a group that depends only its contents, 
regardless of order.  Each object in Python, such as a Tile object, 
has a "hash" value that can serve as a fingerprint for that object. 
The default hash value for user-defined objects is its memory address, which is not very random.  However, Python provides 
good built-in hash functions for built-in types including 
tuples.  Since no two `Tile` objects have the same row and 
column, we can use yet another magic method in `Tile` to tell Python 
that the hash value of a `Tile` object should be calculate from 
its row and column: 

```
    def __hash__(self) -> int:
        """Hash on position only (not value)"""
        return hash((self.row, self.col))
```

This hash value will be "random enough" for our purposes. 
 The sum of the hashes of the tiles in a 
group is therefore very unlikely to match the sum of the hashes
of tiles in any other group, unless the two groups contain the 
same tiles.   (This is not necessarily true of
the default hash function based on memory address, 
as I learned the hard way.)  I will exploit this to build a pretty good, pretty 
simple test case: 

```python
    def test_groups_are_distinct(self):
        """Each group should contain a distinct set of tiles.
        (A frequent bug in Winter 2019 CIS 211.)
        """
        board = Board()
        groups_by_hash = { }
        for group in board.groups:
            hash_sum = 0
            for tile in group:
                hash_sum += hash(tile)
            self.assertNotIn(hash_sum, groups_by_hash,
                             msg=f"Oh no, group {group} is a duplicate!")
            groups_by_hash[hash_sum] = group
```

## Detecting duplicates (again)

Now that we have a list of 'groups', we can revisit the 
algorithm we sketched before for detecting duplicate values in 
rows, columns, or blocks: 

``` 
for each group (row, column, or block): 
    used symbols = { }
    for each tile in the group: 
        if the tile is one of CHOICES (anything but UNKNOWN): 
           if the tile's symbol is already in used symbols: 
               return False (board is not consistent)
           else: 
               add the tile's symbol to the used symbols
return True  (the solved part of the board is ok so far)
```

Now it's easy!  The outer loop really is one line of code, 
looping through the groups.  I'll let you write the code for 
an ```is_consistent``` method with this signature: 

```python
    def is_consistent(self) -> bool:
```

Remember that ```{ }``` in Python is the empty dictionary rather than 
the empty set, so you'll need to initialize used_symbols as ```set()```. 

Note that ```is_consistent``` does not indicate which values were repeated. 
Later we may want to augment the ```is_consistent``` method with 
notification of a new event to communicate that information.  For now 
let's just make sure it works with a test case.  We'll want to test 
that accepts a proper, complete or incomplete board, and that it 
can reject a board with duplicate symbols in a row, a column, or a block. 

```python
class TestConsistent(unittest.TestCase):
    """Tests of the 'is_consistent' method"""

    def test_good_complete_board(self):
        """This one is from Wikipedia"""
        board = Board()
        board.set_tiles(["534678912", "672195348", "198342567",
                        "859761423", "426853791", "713924856",
                         "961537284", "287419635", "345286179"])
        self.assertTrue(board.is_consistent())

    def test_good_incomplete(self):
        """From Sadman Sudoku"""
        board = Board()
        board.set_tiles(["...26.7.1", "68..7..9.", "19...45..",
                        "82.1...4.", "..46.29..", ".5...3.28",
                        "..93...74", ".4..5..36", "7.3.18..."])
        self.assertTrue(board.is_consistent())

    def test_bad_column(self):
        board = Board()
        board.set_tiles(["1........", ".........", ".........",
                         ".........", ".........", ".........",
                         "1........", ".........", "........."])
        self.assertFalse(board.is_consistent())

    def test_bad_row(self):
        board = Board()
        board.set_tiles([".........", ".........", ".........",
                         ".........", ".2.....2.", ".........",
                         ".........", ".........", "........."])
        self.assertFalse(board.is_consistent())

    def test_bad_block(self):
        board = Board()
        board.set_tiles([".........", "......1..", "........1",
                         ".........", ".........", ".........",
                         ".........", ".........", "........."])
        self.assertFalse(board.is_consistent())
```

Pro tip:  If your test cases fail, rejecting some consistent 
boards as inconsistent, it helps to add some logging 
to your `is_consistent` method.  The following statement 
helped me: 

```python
   log.debug(f"Duplicate {tile.value} in {group}")
```

Of course yours could differ depending on the variable 
names you use. 

## Are we there yet?

We almost have a running program, but looking in 
`sudoku.py` we can see that our main program needs 
one more method, called `solve`: 

```python
    if board.is_consistent():
        board.solve()
    else:
        print("Board has duplicates; rejected")
    print(board)
```

We can temporarily "stub out" this method in our `Board` 
class: 

```python
    def solve(self):
        """Solve the puzzle!"""
        #FIXME: This will be added in the next step
        return
```

Now we have a simple consistency checker.  If we execute it
on a valid but incomplete board, it will simply print 
that board: 

``` 
$ python3 sudoku.py data/00-nakedsubset1.sdk 
32...14..
9..4.2..3
..6.7...9
8.1..5...
...1.6...
...7..1.8
1...9.5..
2..8.4..7
..45...31
```

If we execute it on an invalid board, it 
will report the inconsistency: 

 ``` 
$ python3 sudoku.py data/bad.sdk 
Board has duplicates; rejected
435269781
682571493
197834562
826195347
374682915
951743628
519326874
248957136
963418257
```

## Onward! 

Our [next step](HOWTO-PROPAGATE.md) will be to 
replace our stubbed-out `solve` method 
with a method that can actually solve 
some puzzles using constraint propagation. 
