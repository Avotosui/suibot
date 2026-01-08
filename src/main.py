import time
import os
from tetris_engine import TetrisGame
from ai_player import GeneticPlayer

def print_board(game):
    # clear the screen (cls for windows, clear for mac/linux)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"Score: {game.score}")
    print("+" + "-" * (game.width * 2) + "+")
    
    for row in game.board:
        line = "|"
        for cell in row:
            # draw [] for blocks and . for empty space
            line += "[]" if cell else " ."
        line += "|"
        print(line)
        
    print("+" + "-" * (game.width * 2) + "+")

def main():
    # create game
    game = TetrisGame()
    
    # hand-coded weights
    manual_weights = {
        "lines": 100.0,      # We REALLY want to clear lines
        "height": -2.0,      # We dislike height
        "holes": -10.0,      # We HATE holes
        "bumpiness": -1.0    # We prefer a flat surface
    }
    player = GeneticPlayer(manual_weights)
    
    # game loop
    while not game.game_over:
        # ask the AI for the best move, which returns (column, rotation)
        move = player.get_best_move(game)
        
        # if AI returns None, it means no moves are possible (Game Over)
        if not move:
            print("AI gave up (No moves possible)")
            break
            
        col, rot = move
        
        # executes moves
        reward = game.step(col, rot)
        
        # print board
        print_board(game)
        
        # time between frames
        time.sleep(0.5)

    print(f"GAME OVER! Final Score: {game.score}")

if __name__ == "__main__":
    main()