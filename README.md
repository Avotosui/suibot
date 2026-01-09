# Genetic Algorithm Tetris AI (Tetris Demon)

This is a headless Tetris engine with an AI player that uses a genetic algorithm to tune its heuristic weights. It’s mainly a personal project for learning more about game AI and genetic algorithms.

## Project Features

- Headless Tetris engine  
  A non-graphical Tetris simulator that runs fast and makes it easier to test ideas without worrying about rendering.

- Heuristic-Based AI  
  The AI decides where to place pieces using simple board features like height, bumpiness, holes, and lines cleared. Each feature has a weight that affects how good a move looks.

- Genetic Algorithm  
  A genetic algorithm is used to automatically adjust those heuristic weights based on how well the AI performs, instead of tuning them by hand.

- Placement-Based cControl  
  The AI picks a rotation and x-position, instead of using movement keys, and the engine places the piece there. 

## Future plans

- Add SRS support  
  Implement the Super Rotation System so rotations behave more like modern Tetris.

- Translate placements into real inputs  
  Convert the AI’s placement decisions into actual keyboard inputs like left, right, rotate, and drop.

- Play on external Tetris clients  
  Use basic computer vision so the AI can read the screen and play games outside of the built-in engine.

## Getting started

**Requirements:** Python 3.x

Run `main.py` to see the current AI play in the headless engine. 
Run `trainer.py` if you wish to train your own genetic AI player (will override best_brain.json if it's better). 

## Notes

This project is mostly for my personal experimentation and learning. The code is still evolving, and a lot of things can definitely be improved.

## Contact

Maintainer: @Avotosui  
Email: avotosui@gmail.com