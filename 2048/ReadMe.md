This is a HAMK - project about creating an algorithm with heurestics, that can achieve as high as possible reward in a 2048 game.

---

### Notes: ###

Average score without heurestics - average: 765.6, median: 740

Goal for finalized score: 2500+

**Heurestics used**

Those in the Source code:

1. Amount of empty tiles
2. random input
3. High score

Those that were created in the project:

1. If same number is neighbor - Rasmus
2. Prioritize merging higher score tiles -  Iiro
3. Prioritize direction with the highest combined total point value - Rasmus
4. Similar number tiles around - Iiro
5. Put top score in corner - Rasmus - **negative impact on result**
6. Penalize large distance - Rasmus - **negative impact on result**
7. If no move creates a combination move to a cirection that has a possibility of having a combination next turn -  Iiro

**Combinations**
1. Amount of tiles left & prioritise highest score with move - Iiro
    If not many tiles left empty, prioritise combining small numbers to make space


## Results ##

New average: 9321.6
New median: 8341.2
New best: 15812


