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


def heuristic_HighestValueDirection(board):
    # Returns the direction that has the highest combined merge value.
    best_score = 0
    for key in commands.keys():
        _, done, points = commands[key](board)
        if done and points > best_score:
            best_score = points
    return best_score
    

def heuristic_PenalizeDistance(matrix):
    # Penalizes board where large tiles are spread out from a (top-left) corner.
    matrix = np.array(matrix)
    score = 0

    # pick a corner (0,0) top-left
    corner_x, corner_y = 0, 0

    for x in range(c.GRID_LEN):
        for y in range(c.GRID_LEN):
            value = matrix[x][y]
            if value > 0:
                # Manhattan distance from corner
                dist = abs(x - corner_x) + abs(y - corner_y)
                # Penalize distance weighted by tile value
                score -= dist * value  

    return score