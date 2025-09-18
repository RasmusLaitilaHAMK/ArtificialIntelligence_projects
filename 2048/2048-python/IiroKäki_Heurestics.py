import numpy as np
import copy
import constants as c
import logic
import random
from multiprocessing.pool import ThreadPool
import AI_heuristics as AI


pool = ThreadPool(4)
transposition_table = {}

commands = {c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right}

# ---------- UUSI: Merge-priorisointi kun lauta on “täynnä” ----------

def _count_potential_merges_line(line):
    """
    Apuri yhdelle riville/sarakkeelle:
    Poista nollat, laske peräkkäiset samat (yksi merge per pari).
    """
    tiles = [v for v in line if v != 0]
    merges = 0
    i = 0
    while i < len(tiles) - 1:
        if tiles[i] == tiles[i+1]:
            merges += 1
            i += 2  # nämä yhdistyvät, ohitetaan molemmat
        else:
            i += 1
    return merges

def _get_lines_for_direction(board, key):
    """
    Palauttaa listan 'linjoja' (rivit tai sarakkeet oikeassa järjestyksessä)
    sen mukaan, mihin suuntaan ollaan liikkumassa.
    - Vasemmalle: rivit vasemmalta oikealle
    - Oikealle: rivit oikealta vasemmalle
    - Ylös: sarakkeet ylhäältä alas
    - Alas: sarakkeet alhaalta ylös
    """
    a = np.array(board)
    lines = []

    if key == c.KEY_LEFT:
        for r in range(c.GRID_LEN):
            lines.append(list(a[r, :]))

    elif key == c.KEY_RIGHT:
        for r in range(c.GRID_LEN):
            lines.append(list(a[r, ::-1]))  # käänteinen rivi

    elif key == c.KEY_UP:
        for cidx in range(c.GRID_LEN):
            lines.append(list(a[:, cidx]))  # sarake ylhäältä alas

    elif key == c.KEY_DOWN:
        for cidx in range(c.GRID_LEN):
            lines.append(list(a[::-1, cidx]))  # sarake alhaalta ylös

    return lines

def count_potential_merges(board, key):
    """
    Kuinka monta mergeä (yhdistymistä) tämä siirto todennäköisesti tuottaa,
    arvioituna ennen varsinaista siirtoa (logiikka kuten 2048:ssa).
    """
    total_merges = 0
    lines = _get_lines_for_direction(board, key)
    for line in lines:
        total_merges += _count_potential_merges_line(line)
    return total_merges


def heuristic_DynamicMergePriority(board, empty_threshold=5, tie_break="points"):
    """
    Dynamic heuristic (score version for search tree):
    - If empties <= threshold: reward merges primarily, tiebreak with points.
    - Otherwise: reward points primarily, tiebreak with empty spaces.
    
    Returns a numeric score (higher is better).
    """
    empties = int(np.sum(np.array(board) == 0))

    best_score = -1e9  # start with very low

    for key in commands.keys():
        succ, done, points = commands[key](board)
        if not done:
            continue

        if empties <= empty_threshold:
            # prioritize merges
            merges = count_potential_merges(board, key)
            if tie_break == "points":
                score = merges * 1000 + points
            else:
                score = merges * 1000 + AI.heuristic_PenalizeDistance(succ)

        else:
            # prioritize points
            n_empty = int(np.sum(np.array(succ) == 0))
            score = points * 1000 + n_empty

        if score > best_score:
            best_score = score

    return best_score
