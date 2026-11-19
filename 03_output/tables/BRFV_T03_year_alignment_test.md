# BRFV_T03_year_alignment_test

| signal | n_firms |
| --- | --- |
| entry: first score year minus first priced fiscal year = 0 | 717 |
| entry: first score year minus first priced fiscal year = 1 | 160 |
| exit: last score year minus last fiscal year = 0 | 77 |
| exit: last score year minus last fiscal year = 1 | 627 |
| first row in the first priced fiscal year: rows | 717 |
| first row in the first priced fiscal year: rows with a score other than zero | 16 |
| the same firms one year later: rows | 637 |
| the same firms one year later: rows with a score other than zero | 36 |
| row one year after the last priced fiscal year: rows | 627 |
| row one year after the last priced fiscal year: rows with a score other than zero | 0 |
| the same firms one year earlier: rows | 589 |
| the same firms one year earlier: rows with a score other than zero | 35 |
| verdict: fiscal (basis: the rows after the last fiscal year are empty); configured: fiscal | 1,581 |

December year-end firms only. The first four rows count firms by the gap between score years and priced fiscal years. The next eight rows count how many boundary rows carry any score: a row with no filing behind it has all scores at zero. See the docstring of brfv_04_build_panel.py.
