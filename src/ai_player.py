from tetris_engine import TetrisGame, MoveScanner
import random

# Mutation stats
BASE_MUTATION_RATE = 0.1
BASE_MUTATION_STEP = 2.0

# Height penalty
HEIGHT_PENALTY_TOGGLE = True
HEIGHT_PENALTY_EXPONENT = 2.5

class BoardEvaluator: 
    def get_score(self, board, weights): 
        width = len(board[0])
        heights = []
        for x in range(width):
            h = self._get_col_height(board, x)
            heights.append(h)
            
        # get raw stats
        agg_height = self.calculate_aggregate_height(board, heights)
        holes = self.calculate_holes(board, heights)
        bumpiness = self.calculate_bumpiness(heights)
        wells = self.calculate_wells(heights)
        lines = self.count_completed_lines(board)
        
        # extra penalties
        height_penalty = 0
        if HEIGHT_PENALTY_TOGGLE: 
            height_penalty = self._calculate_height_penalty(heights)
            
        
        # move score
        score = 0
        
        # multiply raw stats by weights and sum it
        score += agg_height * weights.get("height", 0)
        score += holes * weights.get("holes", 0)
        score += bumpiness * weights.get("bumpiness", 0)
        score += wells * weights.get("wells", 0)
        score += lines * weights.get("lines", 0)
        
        # score penalties
        score -= height_penalty
        
        return score
    
    
    def calculate_aggregate_height(self, board, heights): 
        return sum(heights)
                
    
    def calculate_holes(self, board, heights): 
        holes = 0
        width = len(board[0])
        board_height = len(board)
        
        for x in range(width):
            col_height = heights[x]
            
            # empty column = skip
            if col_height == 0:
                continue
                
            # check from top down
            start_y = board_height - col_height
            for y in range(start_y, board_height):
                if board[y][x] == 0:
                    holes += 1
                    
        return holes
    
    def calculate_bumpiness(self, heights): 
        total_bumpiness = 0
        
        # sums the absolute difference between adjacent columns
        for i in range(len(heights) - 1): 
            total_bumpiness += abs(heights[i + 1] - heights[i])
            
        return total_bumpiness
    
    def calculate_wells(self, heights):
        side_well_count = 0
        other_well_count = 0
        
        # check for number of wells (which is where its at least 4 blocks deeper than neighboring columns)
        for i in range(len(heights)): 
            left_height = heights[i - 1] if i > 0 else 20
            right_height = heights[i + 1] if i < len(heights) - 1 else 20
            
            well_depth = min(left_height, right_height) - heights[i]

            if well_depth >= 4:
                if i == 0 or i == len(heights) - 1:
                    side_well_count += 1
                else:
                    other_well_count += 1

        # only one well on the side
        if side_well_count == 1 and other_well_count == 0:
            return 1
        
        # more than one well, penalizeeeeeeeeeeeeeeee
        total_wells = side_well_count + other_well_count
        if total_wells >= 1: 
            return -1 * total_wells
        return 0
    
    def count_completed_lines(self, board): 
        return sum([1 for row in board if all(row)])
    
    def _get_col_height(self, board, x):
        # helper to find the height of a specific column x
        height = len(board)
        for y in range(height):
            if board[y][x] != 0:
                return height - y
        return 0
    
    def _calculate_height_penalty(self, heights): 
        total_penalty = 0
        exponent = HEIGHT_PENALTY_EXPONENT
        
        for height in heights: 
            if(height > 5): # don't reward stacking super high (> 5)
                total_penalty += ((height - 5) ** exponent)
            
        return total_penalty




class GeneticPlayer: 
    def __init__(self, weights):
        self.weights = weights
        self.scanner = MoveScanner()
        self.evaluator = BoardEvaluator()
        
    def get_best_move(self, game):
        # use MoveScanner to get all options
        moves = self.scanner.get_all_legal_moves(game)
        
        best_score = -float('inf')
        best_move = None
        
        # use BoardEvaluator to score possible moves
        for move in moves: 
            # get board_state
            board_state = game.return_board_state(move)
            
            # calculate score
            score = self.evaluator.get_score(board_state, self.weights)
            
            # track winning move
            if score > best_score: 
                best_score = score
                best_move = move
                
        if best_move is None: 
            return None
            
        return best_move
    
    def get_genome(self): 
        return self.weights
    

# helper functions for generating, crossing over, and mutating weights
def generate_random_genome(): 
    return {
        "height": random.uniform(-50, 0),
        "holes": random.uniform(-50, 0), 
        "bumpiness": random.uniform(-50, 0),
        "wells": random.uniform(0, 50),
        "lines": random.uniform(0, 50)
    }

def crossover(parent1_weights, parent2_weights): 
    child_weights = {}
    
    for key in parent1_weights: 
        if(random.random() > 0.5): # 50% chance to inherit each parent's weights
            child_weights[key] = parent1_weights[key]
        else: 
            child_weights[key] = parent2_weights[key]
    return child_weights

def mutate(weights, mutation_rate=BASE_MUTATION_RATE, mutation_step = BASE_MUTATION_STEP): 
    mutated_weights = weights.copy() 
    
    for key in mutated_weights: 
        if(random.random() < mutation_rate): 
            mutated_weights[key] += random.uniform(-mutation_step, mutation_step)
    
    return mutated_weights