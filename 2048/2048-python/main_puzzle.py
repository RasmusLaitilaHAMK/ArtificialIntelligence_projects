from tkinter import Frame, Label, CENTER
import random
import logic
import constants as c
import helpers as h
import sys
import AI_heuristics as AI

sys.setrecursionlimit(10**6)


"""Function that generates a random position withing the grid"""
def gen():
    return random.randint(0, c.GRID_LEN - 1)


class GameGrid(Frame):
    """Method to close the game window"""
    def close_game(self):
        self.destroy()
        self.master.destroy()

    def __init__(self, draw = True, max_depth = 2):
        self.max_depth = max_depth
        self.draw = draw
        Frame.__init__(self)
        self.game_over = False      # Is the game over
        self.start = True           # Has the game started
        self.points = 0             # Keep track of the points

        self.grid()                 # Initialize the grid
        self.master.title('2048')   # Set the title for the game window
        
        self.done = False           # Flag to check if move is done

        """Map the key presses to the movement function from the constants file"""
        self.commands = {
            c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right
        }

        self.grid_cells = []                        # List to store the grid cells
        self.init_grid()                            # Initialize the grid cells
        self.matrix = logic.new_game(c.GRID_LEN)    # Create a new game "matrix"
        self.history_matrixs = []                   # List to store the previous matrixes
        self.update_grid_cells()                    # Update the grid cells with the current matrix

        self.update_view()  # Update the view

        """Create a background Frame for the game with specified color, width and height"""
    def init_grid(self):
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME,width=c.SIZE, height=c.SIZE)
        background.grid()   # Place the created Frame to the grid
        
        for i in range(c.GRID_LEN): # Loop trough each row of the grid
            grid_row = []           # Create an empty list to store the current  game state

            """We loop trough the each column of the grid and then create a frame for each cell, with specified settings"""
            for j in range(c.GRID_LEN):
                cell = Frame(background, bg=c.BACKGROUND_COLOR_CELL_EMPTY, width=c.SIZE / c.GRID_LEN, height=c.SIZE / c.GRID_LEN )
                # Add some padding to the cell frame
                cell.grid(row=i, column=j, padx=c.GRID_PADDING, pady=c.GRID_PADDING)
                # Create a label to display the tile number
                t = Label(master=cell, text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY, justify=CENTER, font=c.FONT, width=5, height=2)
                t.grid()                        # Place the label in the cell frame
                grid_row.append(t)              # Add the label to the current row list
            self.grid_cells.append(grid_row)    # Add the current row list to the grid cells list

    def update_grid_cells(self):
        for i in range(c.GRID_LEN):             # Loop the rows
            for j in range(c.GRID_LEN):         # Loop the columns
                new_number = self.matrix[i][j]  # Get the value of the cell from the matrix
                if new_number == 0:             # If the value is 0, set the label text and background color to empty
                    self.grid_cells[i][j].configure(text="",bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                    
                # If the cell does have a value, set the label, text and colors accordingly
                else:
                    self.grid_cells[i][j].configure(text=str(new_number), bg=c.BACKGROUND_COLOR_DICT[new_number], fg=c.CELL_COLOR_DICT[new_number] )


    def update_view(self):
        if not self.game_over and self.start:       # If the game just started            
            self.start = False                      # Set the start to False
            self.update_grid_cells()                # Update the grid cells
            if self.draw:
                 self.update()

        elif not self.game_over:            # If the game isn't over
            key = AI.AI_play(self.matrix, self.max_depth)    # Get the next move from the AI --- Important stuff for project starts from here

            self.matrix, done, points = self.commands[key](self.matrix) # Execute the move and get the result
            self.points += points   # Add points from the move
            if done:                # If a move was done
                self.done = True    # Set to true
                self.matrix = logic.add_two(self.matrix)    # Add a new tile to the matrix
                self.history_matrixs.append(self.matrix)    # Record the last move
                self.update_grid_cells()                    # Update the grid cells
                if logic.game_state(self.matrix) == 'win':
                    h.print_results_board(self.grid_cells, self.points, win = True)
                    self.game_over = True     
                    if self.draw:
                         self.after(1000, self.update())
                         self.destroy()
             
                if logic.game_state(self.matrix) == 'lose':
                    h.print_results_board(self.grid_cells, self.points, win = False)
                    self.game_over = True

                    if self.draw:
                         self.after(1000, self.update())
                         self.destroy()

                if self.draw:
                     self.update()

        if not self.game_over:  # If the game isn't over
            self.update_view()


#  =========================  MAIN FUNCTION  =============================
import pandas as pd

def main():

    draw = True
    sims = 5
    max_depth = -1

    print("Max Depth = ", max_depth)

    sim_results = pd.DataFrame(columns=['Game Parameters', 'Score'])
  
    for heuristic in ["empty_tile_heuristics"]:

        for i in range(0, sims):
            print(i)
            game_grid = GameGrid(draw, max_depth=max_depth)
            tmp = {"Game Parameters": heuristic,
                "Score" : game_grid.points}
            df_tmp = pd.DataFrame(tmp, index = [i])
            sim_results = pd.concat([sim_results, df_tmp])

    print(sim_results)
    print(sim_results["Score"].mean())

if __name__ == "__main__":
    main()

