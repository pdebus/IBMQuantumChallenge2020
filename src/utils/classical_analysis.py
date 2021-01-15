
from datasets.data import *

from board_tools import plot_boards, board2_bitstrings

if __name__ == "__main__":
    problems = [problem_set, q1, q2, q3]

    for p in problems:
        plot_boards(p)