# Adding Guess-and-Check to Sudoku

If you completed the naked_single and hidden_single solution 
techniques, you have a solver that can very quickly solve 
some puzzles.  However, there are other puzzles that it just 
can't solve. 

We could add a bunch of other solution techniques: 
[XY-Wing](http://www.sadmansoftware.com/sudoku/xywing.php), 
[Swordfish](http://www.sadmansoftware.com/sudoku/swordfish.php), 
[Forcing Chains](http://www.sadmansoftware.com/sudoku/forcingchain.php), 
etc.   Or we could resort to *guess-and-check*, also known 
as *trial and error* or *brute force*.

By itself, guess-and-check can solve any Sudoku puzzle, but it 
could be very slow.  We might make several guesses before we 
discover that the first guess we made was wrong.  Then we would 
back up and try again with a different guess.  Eventually we 
would make all the right guesses and solve the board.  The 
number of guesses we would have to make could, at worst, be 
an exponential function of the number of tiles with unknown values. 

Consider the most brutish of brute force techniques:  We could simply
make a guess for each of the unknown tiles, using no other 
information.   How many guesses are possible?  Suppose there are 
*20* open tiles and 9 choices; that is *9^20* potential combinations, 
a rather large number.  So we clearly don't want absolute brute force. 
We want to apply just a bit of brute force where needed. 

## Brute force and constraint propagation

Our naked single and hidden single techniques propagate 
constraints:  They use existing tile values to limit the choices 
to be considered for other tiles.  Sometimes they can constrain 
the potential choices to one value, and choose that value.  But 
even when they can't limit the possible values to just one, they 
can greatly cut down the number of choices we need to consider. 
Moreover, they can quickly check the consequences of a choice. 


### Fail fast

Once we have resorted to guess-and-check, we could proceed using just 
guess-and-check for all tiles.  However, our naked single and hidden
single techniques work much faster than guess-and-check.   If we 
can continue to use them between guesses, they can help us determine
much more quickly whether a guess was correct. 

### Choose wisely

Suppose we have used naked single and hidden single as long as they 
made progress, but reached a state at which there are still several 
unsolved tiles.  We need to make a guess at the value of at least 
one of those tiles.  Suppose one of the unsolved tiles has 7 candidate 
values, and another unsolved tile has just 3 candidate values.  
Even if we initially make the wrong guess, and have to guess again, 
we'll be much better off guessing a value for the tile with just 
3 candidate values. In general, when forced to guess, we should 
choose a tile with as few candidates as possible.

# Recursive guessing

Our current ```solve``` method can't solve all puzzles, although it solves 
some puzzles quickly.  Since it applies constraint propagation, 
let's rename it ```propagate``` and add a new ```solve``` method 
that calls it: 

```python
    def solve(self):
        """General solver; guess-and-check 
        combined with constraint propagation.
        """
        self.propagate()
        
    def propagate(self):
        """Repeat solution tactics until we
        don't make any progress, whether or not
        the board is solved.
        """
        progress = True
        while progress:
            progress = self.naked_single()
            self.hidden_single()
        return
```

We haven't added any guess-and-check technique yet.  We've just 
rearranged the code a little so that our solver can use the 
```propagate``` method (our old ```solve``` method) as one 
step.   At this point our program should pass exactly the same 
tests and solve exactly the same puzzles as it did before. 

Now we want to add the guess-and-check.  There is one big 
difference from what we have done so far:  Since we could 
guess wrong, we must consider the possibility of 
creating an inconsistent board, even if the original board 
was solvable.  We'll make our 'solve' method return a boolean
value.  True will mean that the board was solved.  False will 
mean, not only that we didn't solve it, but also that 
*it cannot be solved*, probably because of some wrong 
guess made earlier. 
 
The logic, 
expressed in pseudocode, should be something like this: 

```
solve() -> bool: 
    propagate constraints. 
    if board is solved, return True
    if board is inconsistent, return False
    otherwise: 
        save the state of the board
        select a tile to guess values for 
        for each value the tile could hold: 
            set the tile to that value
            if solve(): 
                return True
            else: 
                restore the board to saved state
        # Tried all the possibilities; none worked 
        return False
```

When we design an algorithm like this, we need to think 
carefully about things that could be wrong.  Could it 
ever be an infinite loop?   Could it ever get the wrong 
answer, or fail to get an answer? 

Our constraint propagation methods, naked single and hidden single,
were written with the assumption that we were working with a 
correct puzzle with exactly one solution.  Now we are guessing
values, and if we guess wrong (which we sometimes will!) we may
create boards that cannot be solved.  When naked single eliminates 
candidates, it might discover that the set of values a tile could 
have is empty.  When hidden single counts the number of tiles 
that could hold a value, the number might be zero.  Will this 
cause a problem? 

We can reason about it this way:  Even if naked single or 
hidden single make some mistakes (e.g., eliminating candidates 
they should not, or setting a bad tile value), eventually they 
will reach a point where the board is either full or they can't 
choose values for any more tiles.  If the board is full, either 
it is a solution (and is_consistent returns True) or it 
contains bad choices.  The worst that can happen is that 
we might continue to make guesses when we should recognize that 
the board is unsolvable.  So if naked single or hidden single eliminate
some candidates or choose some tile values that they shouldn't, 
it might slow the solver down, but it won't break it. 

We can't have an infinite loop because the board will be filled up 
either by guessing or by naked single and hidden single. 

## Selecting a tile to guess

As we noted above, our solver will be faster if we choose 
a tile with few candidates.  We can write a loop to choose 
the unsolved tile (one with value UNKNOWN) with the smallest 
number of candidates.   Its header might look like this: 

```python
    def min_choice_tile(self) -> Tile: 
        """Returns a tile with value UNKNOWN and 
        minimum number of candidates. 
        Precondition: There is at least one tile 
        with value UNKNOWN. 
        """
```

I'll leave the code to you.   How shall we test it?  
It's easy to to check that the returned tile has value 
UNKNOWN.   Testing that it is among the UNKNOWN tiles with 
a minimum number of candidates is a little harder, but we 
can do it by creating a board with a single best choice: 

```python
    def test_choose_min_tile(self):
        board = Board()
        # We want a predictable, single "best" tile to be chosen,
        # so we'll create a board in which all the 'unknown' tiles
        # have many candidates but exactly one tile has exactly
        # two candidates. It will be easiest to see this if we
        # lay out the board as a matrix.
        board.set_tiles(["....5....",
                         "....4....",
                         ".........",
                         ".........",
                         "123....89",
                         ".........",
                         ".........",
                         ".........",
                         "........."])
        # Tile (4,4) should have just 6,7 as candidates.
        # First we have to remove others with naked_single
        board.naked_single()
        # Then we can make the choice.
        tile = board.min_choice_tile()
        self.assertEqual(tile.value, ".")
        self.assertEqual(tile.row, 4)
        self.assertEqual(tile.col, 4)
        self.assertEqual(tile.candidates, set(["6", "7"]))
```

## Saving and restoring state 

What about the lines in our pseudocode that tell us to 
save the state of the board and restore it?  How can we 
do that? 

The full state of the board includes not only the tile values, 
but also the candidates for each tile.  We could create another 
data structure to save it all.  However, we can get by with less. 
If we save just the tile values, and not the candidates for 
each tile, the candidates will be restored by the first call to 
```naked_single```.  We already have a method ```set_tiles``` to 
set the tile values (and appropriate starting candidate lists) from 
a list of strings.  That can work as the ```restore``` method. 
All we need is to add a method to create a list of strings 
from the board. 

Notice that we almost already have this method.  Consider the 
```__str__```  method of class Board: 

```python
    def __str__(self) -> str:
        """In Sadman Sudoku format"""
        row_syms = [ ]
        for row in self.tiles:
            values = [tile.value for tile in row]
            row_syms.append("".join(values))
        return "\n".join(row_syms)
```

This method creates a list of strings, and then joins 
the strings together with newlines.  Let's just factor out 
the part we need: 

```python
    def __str__(self) -> str:
        """In Sadman Sudoku format"""
        return "\n".join(self.as_list())


    def as_list(self) -> List[str]:
        """Tile values in a format compatible with 
        set_tiles.
        """
        row_syms = [ ]
        for row in self.tiles:
            values = [tile.value for tile in row]
            row_syms.append("".join(values))
        return row_syms
```

We can easily test this: 

```python
    def test_save_restore(self):
        """as_list and set_tiles should work as saving and
        restoring board state.
        """
        board = Board()
        tiles_list = ["......12.", "24..1....", "9.1..4...",
                        "4....365.", "....9....", ".364....1",
                        "...1..5.6", "....5..43", ".72......"]
        board.set_tiles(tiles_list)
        saved = board.as_list()
        self.assertEqual(tiles_list, saved)
```

There is one more line in the pseudocode that we haven't 
considered: 

```python
    if board is solved, return True
```

Since we already have a method for determining whether a full 
board is consistent, all we need is to add a loop through the 
tiles to determine whether all of the tiles have values from 
CHOICES.  Its signature will look like this: 

```python
    def is_complete(self) -> bool:
        """None of the tiles are UNKNOWN.  
        Note: Does not check consistency; do that 
        separately with is_consistent.
        """
```
I'll leave that code to you. 

When I first gave this project as an assignment, 
I thought `is_complete` was too simple to be 
worth a test case.  I was wrong.  I saw many
students spend a lot of time debugging other code
when the real bug was in `is_complete`.  Even 
simple code can be buggy!   Fortunately the 
test cases can also be simple: 

```python
    def test_is_complete(self):
        board = Board()
        tiles_list = [
            "687539124"
            ,"243718965"
            ,"951264387"
            ,"419873652"
            ,"725691438"
            ,"836425791"
            ,"394182576"
            ,"168957243"
            ,"572346819"]
        board.set_tiles(tiles_list)
        self.assertTrue(board.is_complete())

    def test_is_not_complete(self):
        board = Board()
        tiles_list = [
            "687539124"
            , "243718965"
            , "951264387"
            , "419873652"
            , "725691.38"
            , "836425791"
            , "394182576"
            , "168957243"
            , "572346819"]
        board.set_tiles(tiles_list)
        self.assertFalse(board.is_complete())
``` 

Now we have everything we need to turn that solver 
pseudocode into Python code.  Which I'll also leave to you. 

Here's a test case that requires guess-and-check to solve: 

    def test_guess_check(self):
        """From data/evil.sdk"""
        board = Board()
        board.set_tiles(["....5..1.", "2........", "5.19..48.",
                         "6...1.24.", "8.......7", ".23.4...1",
                         ".69..28.3", "........4", ".4..8...."])
        board.solve()
        solution = ["497856312", "286134795", "531927486",
                    "675319248", "814265937", "923748561",
                    "169472853", "758693124", "342581679"]
        self.assertEqual(board.as_list(), solution)

# Recap

To add recursive guess-and-check to our Sudoko solver, 
we completed the following steps: 

* Refactored the ```solve``` method.  The old ```solve```
is now one step of the new ```solve```.  We move almost 
all of its logic into ```propagate``` and leave 
just a call to ```propagate```. 

* The next several steps were preparation 
for building the new logic of 'solve':
    * We wrote a method to select the tile 
    with the minimum number of candidates. 
    * We wrote a method to make a copy 
    of the board state as a list of strings, 
    so that we can use it together with 
    ```set_tiles``` to save and restore board state. 
    We got this by refactoring the ```__str__``` method. 
    * We write a method to determine whether 
    the board is complete.  Together with 
    ```is_consistent```, this method can tell us 
    whether the board has been solved. 

* Then we used the building blocks to 
create the new logic of ```solve```, 
recursively searching for a complete 
puzzle solution.  

# Victory is ours! 

We now have a Sudoku solver that can tackle the 
toughest puzzles.  If we run it with the `-d` 
option for graphics, sometimes it will seem quite 
slow as it makes guesses, discovers they are wrong, 
and tries other guesses.  Most of this slowness, 
though, is in the graphics.  I dare you to find 
a puzzle that it cannot solve in five seconds, 
even on a slow laptop. 

## Next steps

There is no next step.  However, here's something 
to think about:  How would you modify this program 
so that instead of solving a puzzle, it generated 
a good puzzle with exactly one solution?  Could you 
make it generate puzzles at different levels of 
difficulty?  Think in terms of extending the 
recursive guess-and-check.  If you spend at least 
an hour thinking about it, whether you solve it or 
not, let's discuss it. 