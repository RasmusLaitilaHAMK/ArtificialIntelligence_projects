import constants as c

def print_results_board(grid_cells, points, win):

    grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
    if win:
            grid_cells[1][2].configure(text="Win!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
    if not win:
            grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
    grid_cells[2][1].configure(text="Points:", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
    grid_cells[2][2].configure(text=points, bg=c.BACKGROUND_COLOR_CELL_EMPTY)


