# Sudoku Solver

## Steps

This is a big project.  Most students find it challenging. But it is not 
impossibly challenging:  You can succeed if you start early and work 
systematically.  Don't try skipping forward to bits of code you can 
cut-and-paste; if you do, you will get hopelessly lost. Solve it part by part, 
testing as you go, and making sure you understand each part as you build it. 

This file gives an overview of Sudoku and our approach to solving it. 
Don't skip it!  Then steps to solving it are given in three 
additional HOWTO files.  

* First, [HOWTO Start](HOWTO-START.md) 
    lays a foundation with a board representation, input and output, 
    and a consistency checker.  At the conclusion of this step, you 
    will have a program that distinguishes between a valid Sudoku solution 
    (a complete board that satisfies the rules of Sudoku), an incomplete but 
    possibly solvable board, and a board (whether or not complete) that violates 
    the rules of Sudoku.  
    
* Next, [HOWTO Propagate](HOWTO-PROPAGATE.md) 
    leads you through a partial solver using constraint propagation. 
    This is the most challenging part of the project.  At the 
    conclusion of this step you will have a program that can solve 
    many simple Sudoku puzzles, although it will not be able to solve 
    puzzles that are typically ranked as "intermediate" or "hard". 
    
* Finally, you will add a recursive guess-and-check strategy.  In principle 
    the guess-and-check strategy, together with the consistency checker you 
    constructed in the first step, would be able to solve any Sudoku puzzle. 
    We call it a "brute force" solution.  It would be very slow.  We can do 
    much better, though, by combining it with the constraint propagation 
    step.  When you complete this step, you will have a program that can 
    solve all Sudoku puzzles, and most of them very quickly.  
    With a graphics display it might 
    take several minutes.  With the optional graphics suppressed, I have not
    yet found a puzzle that takes more than a few seconds to solve on a 
    modest laptop computer. This stage of the project is described in 
    [HOWTO Guess](HOWTO-GUESS.md). 
    

## Sudoku Background

Sudoku is a popular logic-based number placement puzzle.
For an example
and a bit of history, see
[the Wikipeda article](http://en.wikipedia.org/wiki/Sudoku)  
One of the interesting bits of history is the role of
of a Sudoku puzzle generating program in popularizing Sudoku.
Creating good puzzles is harder than solving them!

Your program will read a Sudoku board that may be partially
completed.  A board file contains 9 lines of 9 symbols, each of
which is either a digit 0-9 or the 
full-stop symbol '.' (also called 'period'  or 'dot')
to indicate a tile that has not been filled. Your program will first
check for violations of Sudoku rules.  If the board is valid, 
then your program will attempt to solve it.   

*Aside:  While standard sudoku puzzles are 9x9, 
rows and columns of any perfect square length
will work.  In practice, 4x4 is too simple, and 25x25 far too hard. 
Practical puzzle sizes are 9x9 (the standard) and 16x16 
(a more difficult variant, using hexadecimal digits
01234567890ABCDEF).   The rest of 
this HOWTO is written assuming 9x9 puzzles, but in fact our 
solution can be adapted to 16x16 puzzles by changing three 
lines of code in sdk_config.py.*

### The Rules 

A valid Sudoku solution has the following properties:

   * In each of the 9 rows, each digit 1..9 appears
    exactly once.  (No duplicates, and no missing digits.)

   * In each of the 9 columns, each digit 1..9 appears
    exactly once.
 
   * The board can be divided into 9 subregion blocks, each 3x3.
    In each of these blocks, each digit 1..9 appears
    exactly once.
    

If the board contains only the symbols '1' through '9', the pigeonhole
principle ensures that these two properties are equivalent:

  * Each digit appears at least once in a row, column, and block

  * Each digit appears no more than once in a row, column, or block

If the board contains the symbols '1' through '9' and also the
wild-card symbol '.', we say it is incomplete.  We say an incomplete
board is *inconsistent* if any row, column, or block contains more
than one of the symbols '1' through '9', although it may contain
more than one wild-card symbol '.' indicating a choice yet to be
made. 


## The program

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


If there are no duplicated entries in the board (and regardless
  of whether it is complete, with digits only, or has '.'
  characters indicating tiles yet to be filled), your program will
  proceed to the next step.  If there are duplicated elements,
  your program will reject the puzzle. 

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

The [Getting Started](HOWTO-START.md) document describes how to build the 
basic board representation and check for a partially or fully completed 
board that violates the rules of Sudoku.   The board representation makes 
heavy use of *aliasing*, with the same `Tile` objects belonging to multiple 
lists representing rows, columns, and blocks.  This representation reduces 
repetitive code in consistency checking, but its real purpose is to reduce 
repetitive code in the next step, constraint propagation. 


## Completion with constraint propagation

If the board is consistent, then (and only then) your program
will apply two simple constraint propagation 
tactics to fill some of the empty tiles,
then print the resulting board.  These constraints are based
directly on the properties of a completed Sudoku puzzle,
viz., that each symbol must appear once but only once in each
row, column, and block. 

The [constraint propogation HOWTO](HOWTO-PROPAGATE.md) describes how to 
implement these two tactics, called *naked single* and *hidden single*. 
When you have completed it, your program will be able to solve some 
simple Sudoku puzzles completely, and it will be able to fill in some 
tiles in more complex Sudoku puzzles. 

## Recursive Guess-and-Check

In principle we could solve Sudoku puzzles using nothing but guess-and-check. 
We could guess a value for one tile, then attempt to guess a value for another, 
and so on, backing up when we discover that any choice for some tile will lead
to inconsistency.  Sometimes a choice we made early might be bad, but we would
discover the inconsistency only several guesses later, so we might have to retract
several guesses after a great deal of guessing and checking.  This tactic is
perfectly general:  Eventually it will solve any Sudoku puzzle (assuming it
is a valid puzzle with a solution).  It is potentially very slow, though. 

But what if we combined guess-and-check with constraint propagation?  Instead of 
proceeding directly to the next guess, after making one guess we could then do 
as much constraint propagation as possible based on that guess, speeding up 
discovery of inconsistencies as well as helping us make fewer, better guesses. 
That is what we will do in the final part of the Sudoku project, 
described in [the guess-and-check HOWTO](HOWTO-GUESS.md). 

## Next step 

When you have read the basic plan above, you are ready 
to [get started](HOWTO-START.md) coding.





