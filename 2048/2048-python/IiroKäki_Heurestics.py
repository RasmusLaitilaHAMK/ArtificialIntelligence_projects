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

