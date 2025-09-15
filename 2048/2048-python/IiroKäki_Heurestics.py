import numpy as np
import copy
import constants as c
import logic
import random
from multiprocessing.pool import ThreadPool
import AI_heuristics as AIH


pool = ThreadPool(4)
transposition_table = {}

commands = {c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right}

def EqualNeighbor():
    # Neighbor stuff here
    print("Hello")

def heuristic_HighestValueDirection(board):
    """
    Korjattu versio: palauttaa sen NÄPPÄIMEN, joka tuottaa suurimman points-arvon yhdellä siirrolla.
    (Aiemmin palautti vain best_score.)
    """
    best_score = -1
    best_key = None
    for key in commands.keys():
        _, done, points = commands[key](board)
        if done and points > best_score:
            best_score = points
            best_key = key
    return best_key


def heuristic_PenalizeDistance(matrix):
    """
    Rankaisee tilanteita, joissa isot laatat ovat kaukana valitusta nurkasta (0,0).
    Suurempi (vähemmän negatiivinen) arvo on parempi.
    """
    matrix = np.array(matrix)
    score = 0
    corner_x, corner_y = 0, 0  # vasen yläkulma

    for x in range(c.GRID_LEN):
        for y in range(c.GRID_LEN):
            value = matrix[x][y]
            if value > 0:
                dist = abs(x - corner_x) + abs(y - corner_y)  # Manhattan-etäisyys
                score -= dist * value

    return score


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
    Dynaaminen heuristiikka:
    - Jos tyhjiä ruutuja <= empty_threshold: valitse siirto, joka tuottaa ENITEN MERGEJÄ.
      Tasatilanteessa rikotaan tasapeli pisteillä (tai PenalizeDistance:lla).
    - Muuten: valitse siirto, joka maksisoi PISTEET tältä yhdeltä siirrolta.

    Palauttaa NÄPPÄIMEN.
    """
    empties = int(np.sum(np.array(board) == 0))

    best_key = None
    best_primary = -1
    best_secondary = -10**9  # tiebreaker

    for key in commands.keys():
        succ, done, points = commands[key](board)
        if not done:
            continue

        if empties <= empty_threshold:
            # 1) priorisoi mergejen määrä
            merges = count_potential_merges(board, key)
            # Tiebreak: pisteet tai PenalizeDistance
            if tie_break == "points":
                secondary = points
            else:
                secondary = heuristic_PenalizeDistance(succ)

            if (merges > best_primary) or (merges == best_primary and secondary > best_secondary):
                best_primary = merges
                best_secondary = secondary
                best_key = key

        else:
            # 2) priorisoi points
            primary = points
            # Tiebreak: enemmän tyhjiä tai parempi etäisyysheuristiikka
            secondary = int(np.sum(np.array(succ) == 0))
            if (primary > best_primary) or (primary == best_primary and secondary > best_secondary):
                best_primary = primary
                best_secondary = secondary
                best_key = key

    return best_key