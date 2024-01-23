"""Configuration -
Isolate to the extent possible values that
control choices we could make in variations
on the game, such as the dimension (9x9 vs 16x16, etc),
symbols, etc.
"""

# ---------  Configuration of the model component ----------
# Dimension of board.  In principle we could
# do 9x9, 16x16, 25x25, etc.
# 9x9 (root=3) and 16x16 (root=4)
# are probably the only practical choices.
ROOT = 3
NROWS = ROOT * ROOT
NCOLS = ROOT * ROOT
NBLOCKS = ROOT * ROOT

# The set of symbols we can use must
# be the same as the number of rows, columns,
# and blocks.
CHOICES = "123456789"
PENCIL = ["123", "456", "789"]
# For 16x16, it would be
#CHOICES =  "0123456789ABCDEF"
#PENCIL = ["0123", "4567", "890A", "BCDE"]

# One symbol, not in Choices, for Unknown
UNKNOWN = "."

# ---------- Configuration of the graphical view component ---

# Display options
# Color scheme:  White background,
#  beige for unknown cells, green for known,
#  pink for the group we're currently working on
COLOR_BACKGROUND = "#ffffff"  # White
COLOR_KNOWN = "#ccffcc"       # Green
COLOR_UNKNOWN = "#ffffcc"     # Beige
COLOR_WORKING = "#ffccff"     # Pink





