import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial import distance

from datasets.data import problem_set3x3, problem_set, lightsout4

def find_closest_string(strings):
    length = len(strings[0])
    min_dist = 1000
    min_string = None

    for i in range(int(2 ** length)):
        bits = [int(a) for a in format(i, f"0{length}b")]
        dist = sum([distance.hamming(bits, s) for s in strings])
        if dist < min_dist:
            min_dist = dist
            min_string = bits

    return min_string, min_dist


def board2_bitstrings(asteroid_boards, board_size=4):
    strings = []

    for ast_idx in asteroid_boards:
        board = np.zeros((board_size, board_size), dtype=np.uint8)
        for idx in ast_idx:
            board[int(idx[0]), int(idx[1])] = 1
        strings.append(board.flatten().tolist())

    return strings


def kbits(n, k):
    import itertools

    result = []
    for bits in itertools.combinations(range(n), k):
        s = [0] * n
        for bit in bits:
            s[bit] = 1
        result.append(s)

    return result


def compute_uncovered_tiles(beamstring):
    board_size = len(beamstring) // 2
    vertical = np.array(beamstring[:board_size])
    horizontal = np.array(beamstring[board_size:])

    coord2num = lambda i, j: board_size * i + j

    uncovered_v = vertical == 0
    uncovered_h = horizontal == 0

    uncovered_tiles = []

    for i, h in enumerate(uncovered_h):
        for j, v in enumerate(uncovered_v):
            if v and h:
                uncovered_tiles.append(coord2num(i, j))

    return uncovered_tiles


def plot_boards(asteroid_boards, board_size=4):

    num_boards = len(asteroid_boards)
    num_subplots = int(np.sqrt(num_boards))

    fig, axes = plt.subplots(nrows=num_subplots, ncols=num_subplots)
    for ax, ast_idx in zip(axes.flatten(), asteroid_boards):

        board = np.zeros((board_size, board_size), dtype=np.uint8)
        for idx in ast_idx:
            board[int(idx[0]), int(idx[1])] = 1

        ax.imshow(board)

    plt.show()


def compute_switch_edges(board_size=3):

    coord2num = lambda i, j: board_size * i + j
    edges = {}

    for i in range(board_size):
        for j in range(board_size):
            e = {
                coord2num(i, j),
                coord2num(max(0, i - 1), j),
                coord2num(min(board_size - 1, i + 1), j),
                coord2num(i, max(0, j - 1)),
                coord2num(i, min(board_size - 1, j + 1))
                }
            edges[coord2num(i, j)] = sorted(list(e))

    return edges


if __name__ == "__main__":

    closest_string, closest_dist = find_closest_string(lightsout4)
    print(closest_string, closest_dist)

    print(compute_switch_edges())
    print(compute_switch_edges(2))

    plot_boards(problem_set)
    print(board2_bitstrings(problem_set))

    plot_boards(problem_set3x3, board_size=3)

    print(compute_uncovered_tiles([1, 1, 0, 0, 0, 0]))
    print(compute_uncovered_tiles([1, 0, 0, 1, 0, 0, 1, 0]))

    uncovered_tiles = []
    for b in kbits(8, 3):
        print(f"{b}: {compute_uncovered_tiles(b)}")
        tiles = [0] * 16
        for bit in compute_uncovered_tiles(b):
            tiles[bit] = 1
        uncovered_tiles.append("".join([str(t) for t in tiles]))

    for n, ut in enumerate(sorted(uncovered_tiles)):
        print(f"{n+1}:\t{ut}")
