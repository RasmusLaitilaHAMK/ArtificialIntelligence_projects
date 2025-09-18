import numpy as np
import copy
import constants as c
import logic
import random
from multiprocessing.pool import ThreadPool
import RasmusLaitila_Heurestics as LH
import IiroKäki_Heurestics as KH

pool = ThreadPool(4)
transposition_table = {}

commands = {c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right}

# ---------------------------------------------------------------------
# UUSI: Merge-potentiaalin helperit (evaliin ja/tai policyyn)
#  - nämä eivät riko mitään vanhaa; niitä vain kutsutaan evaluate_boardissa
# ---------------------------------------------------------------------

def _count_potential_merges_line(line):
    """
    Poista nollat ja laske peräkkäiset samat (yksi merge per pari).
    Tämä on 2048-mergejen 'potentiaali' yhdellä linjalla.
    """
    tiles = [v for v in line if v != 0]
    merges = 0
    i = 0
    while i < len(tiles) - 1:
        if tiles[i] == tiles[i+1]:
            merges += 1
            i += 2  # nämä yhdistyvät -> ohita molemmat
        else:
            i += 1
    return merges

def _get_lines_for_direction(board, key):
    """
    Palauta rivit/sarakkeet siinä järjestyksessä, johon suuntaan oltaisiin liikkumassa.
    Tämän avulla arvioidaan merge-potentiaalia ilman, että tarvitsee muuttaa peliä.
    """
    a = np.array(board)
    lines = []

    if key == c.KEY_LEFT:
        for r in range(c.GRID_LEN):
            lines.append(list(a[r, :]))
    elif key == c.KEY_RIGHT:
        for r in range(c.GRID_LEN):
            lines.append(list(a[r, ::-1]))
    elif key == c.KEY_UP:
        for cidx in range(c.GRID_LEN):
            lines.append(list(a[:, cidx]))
    elif key == c.KEY_DOWN:
        for cidx in range(c.GRID_LEN):
            lines.append(list(a[::-1, cidx]))

    return lines

def count_potential_merges(board, key):
    """
    Kuinka monta mergeä tämä SIIRTO (key) todennäköisesti tuottaa (arvio)?
    """
    total = 0
    for line in _get_lines_for_direction(board, key):
        total += _count_potential_merges_line(line)
    return total

def eval_merge_potential_over_moves(board):
    """
    EVAL-KOMPONENTTI: paras (max) merge-potentiaali yli kaikkien neljän suunnan.
    Tämä palauttaa NUMEERISEN arvon -> voidaan käyttää evaluate_boardissa.
    """
    best = 0
    for k in commands.keys():
        best = max(best, count_potential_merges(board, k))
    return best

# (Lisäpolicy, jos haluat käyttää erikseen kun lauta on täynnä.)
def heuristic_DynamicMergePriority(board, empty_threshold=5, tie_break="points"):
    """
    Policy-heuristiikka: palauttaa NÄPPÄIMEN.
    - Kun tyhjiä <= kynnys -> priorisoi mergejen määrää (tasapeli pisteillä)
    - Muuten -> priorisoi tämän siirron pisteitä
    """
    empties = int(np.sum(np.array(board) == 0))

    best_key = None
    best_primary = -1
    best_secondary = -10**9

    for k in commands.keys():
        succ, done, points = commands[k](board)
        if not done:
            continue

        if empties <= empty_threshold:
            merges = count_potential_merges(board, k)
            secondary = points if tie_break == "points" else int(np.sum(np.array(succ) == 0))
            if (merges > best_primary) or (merges == best_primary and secondary > best_secondary):
                best_primary = merges
                best_secondary = secondary
                best_key = k
        else:
            primary = points
            secondary = int(np.sum(np.array(succ) == 0))
            if (primary > best_primary) or (primary == best_primary and secondary > best_secondary):
                best_primary = primary
                best_secondary = secondary
                best_key = k

    return best_key


def AI_play(matrix, max_depth):
    
    # scores = pool.starmap( score_toplevel_move, [(key, matrix, max_depth) for key in commands.keys()] )

    # max_index = np.argmax(np.array(scores))
    # keys = list(commands.keys())

    # return keys[max_index]

    bestscore=-1000000
    best_key=None
  
    for key in commands.keys():
        tmp_score = score_toplevel_move(key, matrix, max_depth)
        if tmp_score>bestscore:
            bestscore = tmp_score
            best_key = key

    return best_key


def score_toplevel_move(key, board, max_depth):
    """
    Entry Point to score the first move.
    """
    newboard = commands[key](board)[0]

    if board == newboard:
        return -1000000

    # With many empty tiles calculation of many nodes would take to long and not improve the selected move
    # Less empty tiles allow for a deeper search to find a better move
    if max_depth == -1:
        empty_tiles = sum(sum(np.array(newboard)==0))

        if empty_tiles > 12:
            max_depth = 1
            
        elif empty_tiles > 7:
            max_depth = 2
            
        elif empty_tiles > 4:
            max_depth = 3
            
        elif empty_tiles >= 1:
            max_depth = 4
            
        elif empty_tiles >= 0:
            max_depth = 6
        else:
            max_depth = 2

    score = calculate_chance(newboard, 0, max_depth)
    return score


def calculate_chance(board, curr_depth, max_depth):
    """
    EXPECTIMAX: CHANCE-solmu (satunnaislaatan lisäys).
    - Jos syvyys täynnä -> palauta leaf-eval (evaluate_board)
    - Muuten: käy läpi kaikki tyhjät paikat ja laske odotusarvo
      E = (1/n)*sum_i [ 0.9*V(lauta+2 ruutuun i) + 0.1*V(lauta+4 ruutuun i) ],
      missä n = tyhjien ruutujen määrä.
    """
    if curr_depth >= max_depth:
        return evaluate_board(board)
  
    possible_boards_2 = []
    possible_boards_4 = []

    for x in range(c.GRID_LEN):
        for y in range(c.GRID_LEN):
            if board[x][y] == 0:
                new_board = copy.deepcopy(board)
                new_board[x][y] = 2
                possible_boards_2.append(new_board)

                new_board = copy.deepcopy(board)
                new_board[x][y] = 4
                possible_boards_4.append(new_board)

    # Ei tyhjiä -> ei spawnia -> simppeli arvio (tai voisi kutsua calculate_max)
    if not possible_boards_2:  # (jos 2-lista tyhjä, myös 4-lista on tyhjä)
        return n_empty_tiles(board)

    # Oikea odotusarvon jakaja: n (tyhjien määrä). 0.9/0.1 painot sisällä jo.
    n = len(possible_boards_2)
    expected_sum = 0.0

    # HUOM: tässä kasvatetaan syvyyttä chance-haarassa; jos haluat että vain MAX kasvattaa,
    # muuta (curr_depth + 1) -> curr_depth
    for nb in possible_boards_2:
        expected_sum += 0.9 * calculate_max(nb, curr_depth + 1, max_depth)
    for nb in possible_boards_4:
        expected_sum += 0.1 * calculate_max(nb, curr_depth + 1, max_depth)

    return expected_sum / n


def calculate_max(board, curr_depth, max_depth):
    """
    EXPECTIMAX: MAX-solmu (AI:n vuoro).
    Kokeile kaikki neljä suuntaa, hyppää chance-solmuun ja ota paras arvo.
    """
    if curr_depth >= max_depth:
        return evaluate_board(board)

    best_score = 0.0
        
    for key in commands.keys():
        successor = commands[key](board)[0]
        if board == successor:
            continue
        score = calculate_chance(successor, curr_depth + 1, max_depth)
        if best_score < score:
            best_score = score

    return best_score


def evaluate_board(board):
    """
    Combines multiple heuristics into one evaluation score.
    Higher is better.

    HUOM: Tämä on leaf-eval (Expectimaxin lehtisolmuissa). 
    Lisää/piirrä painoja oman tiimin maun mukaan, mutta pidä arvot NUMEERISINA.
    """
    score = 0.0

    # 1) Tiimin oma heuristiikka (LH) – pitää mukana kuten pyysit
    score += LH.heuristic_HighestValueDirection(board) * 1.0

    # 2) Merge-potentiaali yli kaikkien suuntien (NUMEERINEN komponentti)
    #    -> EI tarvi 'key'-muuttujaa, joten tämä toimii leaf-evalissa
    score += 0.5 * eval_merge_potential_over_moves(board)

    # 3) Pieni boonus vapaasta tilasta (yleensä parantaa elinikää)
    score += 0.1 * n_empty_tiles(board)

    # 4) Halutessa voit testata myös etäisyysrangaistusta (kommentoituna, koska sanoit sen laskeneen scorea):
    # score += LH.heuristic_PenalizeDistance(board) * 0.6

    return score


## Heuristics (vanhat pidetty, ei poistettu)
def n_empty_tiles(matrix):
    return sum(sum(np.array(matrix) == 0))

# Random Choice
def heuristic_random():
    tmp = [c.KEY_UP, c.KEY_DOWN, c.KEY_RIGHT, c.KEY_LEFT]
    key = tmp[random.randint(0, 3)]
    return key

# A Sample Heuristic
def heuristic_empty_tile(matrix):
    best_score = -1
    return_key = None

    for key in commands.keys():
        game, done, points = commands[key](matrix)

        if not done:
            pass

        if done:
            n_empty = n_empty_tiles(game)
            if n_empty > best_score:
                best_score = n_empty
                return_key = key

    return return_key