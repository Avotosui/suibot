# Genetic Algorithm Tetris AI (Tetris Demon)
Open-source implementation of a headless Tetris engine and heuristic-based AI player, with a genetic algorithm framework for evolving evaluation weights. 

# Features & Architecture
- Headless Engine: A lightweight, non-graphical Tetris simulation optimized for high-speed training cycles.
- Heuristic Evaluation: Current AI decision-making utilizes hand-tuned weights for aggregate height, bumpiness, and hole density.
- Placement Control System: The AI currently outputs target coordinates and rotation states, abstracting the micro-movement inputs. 

# Roadmap/Goals
1. Genetic Algorithm Integration: Implement evolutionary strategies to automate weight optimization (replacing current hand-tuned values).
2. SRS Implementation: Integrate the Super Rotation System (SRS) standard into the headless engine for tournament-accurate mechanics.
3. Input Translation Layer: Build a move interpreter to translate abstract AI "placement" decisions into specific keyboard inputs (Left, Right, CW, CCW).
4. Computer Vision Interface: Develop a screen reader to allow the AI to interface with external Tetris clients. 

# Getting Started
Prerequisites: Python 3.x

# Usage
Run main.py to initialize the headless environment and visualize the current heuristic player's performance. 

# Contributing
This is a personal research project focused on reinforcement learning and genetic algorithms. Feedback is welcome; please open an issue or contact me directly. 

# Contact
Maintainer: @Avotosui
Email: avotosui@gmail.com