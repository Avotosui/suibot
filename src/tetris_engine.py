from settings import MATRIX_HEIGHT, MATRIX_WIDTH, PIECE_PREVIEW_AMOUNT, NORMAL_SPAWN_POSITION_X, NORMAL_SPAWN_POSITION_Y, I_PIECE_SPAWN_POSITION_X, I_PIECE_SPAWN_POSITION_Y, LINES_CLEARED_FOR_NEXT_LEVEL, B2B_MULTIPLIER, COMBO_BONUS, MAX_LEVEL, SHAPES, SRS_TABLE
import random
from collections import deque


class TetrisGame:
    def __init__(self):
        self.score = 0
        self.level = 1 # start at level 1
        self.lines_cleared = 0
        
        self.previous_difficulty = False
        self.combo = -1
        
        self.game_over = False
        
        self.current_piece_key = None
        self.held_piece_key = None
        
        self.board = Board()
        
        self.bag = []
        
        self.spawn_piece() 
    
    def step(self, move_tuple, swap_hold): 
        # (x, y, r, piece_key, T-spin (if T-piece))
        # r: 0 = no rotation, 1 = 90 degrees cw, 2 = 180 degrees cw, 3 = 270 degrees cw
        # T-spin: 0 = no t-spin, 1 = t-spin mini, 2 = t-spin (normal)
        
        if(swap_hold): # change piece
            self.hold_piece()
        
        # unpack move data
        x, y, r, piece_key, T_spin = move_tuple
        
        # place piece onto board
        self.board.lock_piece(x, y, r, piece_key)
        
        # clear lines
        current_lines_cleared = self.board.clear_lines()
        
        base_points = 0
        is_difficult = False
        
#       --------------------------STANDARD CLEARS--------------------------
        if(T_spin == 0): 
            if(current_lines_cleared == 0): # Nothing
                pass
            elif(current_lines_cleared == 1): # Single
                base_points = 100
            elif(current_lines_cleared == 2): # Double
                base_points = 300
            elif(current_lines_cleared == 3): # Triple
                base_points = 500
            elif(current_lines_cleared == 4): # Tetris
                base_points = 800
                is_difficult = True
#       --------------------------T-SPIN MINIS--------------------------
        elif(T_spin == 1): 
            if(current_lines_cleared == 0): # T-Spin Mini (No Lines Cleared)
                base_points = 100
            elif(current_lines_cleared == 1): # T-Spin Mini Single
                base_points = 200
                is_difficult = True
            elif(current_lines_cleared == 2): # T-Spin Mini Double
                base_points = 400
                is_difficult = True
#       --------------------------T-SPINS--------------------------
        elif(T_spin == 2): 
            if(current_lines_cleared == 0): # T-Spin (No Lines Cleared)
                base_points = 400
                is_difficult = True
            elif(current_lines_cleared == 1): # T-Spin Single
                base_points = 800
                is_difficult = True
            elif(current_lines_cleared == 2): # T-Spin Double
                base_points = 1200
                is_difficult = True
            elif(current_lines_cleared == 3): # T-Spin Triple
                base_points = 1600
                is_difficult = True
        
        move_score = base_points * self.level # score from base and level
        
        # combo
        if(current_lines_cleared > 0):
            self.combo += 1
        else:
            self.combo = -1
        
#       --------------------------BONUSES--------------------------
        # Back-to-Back Bonus (only happens if both current and previous are difficult)
        if(is_difficult and self.previous_difficulty): 
            move_score = int(B2B_MULTIPLIER * move_score)
            self.previous_difficulty = True
        else: 
            self.previous_difficulty = False
        
        if(self.combo > 0): 
            move_score += COMBO_BONUS * self.combo * self.level
            
        self.score += move_score
        
        # level calculation
        self.lines_cleared += current_lines_cleared
        self.level = min(1 + (self.lines_cleared // LINES_CLEARED_FOR_NEXT_LEVEL), MAX_LEVEL)
        
        # spawn next piece
        self.spawn_piece()
        
        return self.score
    
    def spawn_piece(self):
        # refills the bag if it has less than 7 pieces
        if len(self.bag) < 7: 
            new_bag = ['I', 'O', 'T', 'J', 'L', 'S', 'Z']
            random.shuffle(new_bag)
            self.bag.extend(new_bag)
            
        # take a random piece out of the bag
        self.current_piece_key = self.bag.pop(0)
        
        if(self.current_piece_key == 'I'): 
            if(not is_valid_position(self.board, I_PIECE_SPAWN_POSITION_X, I_PIECE_SPAWN_POSITION_Y, 0, self.current_piece_key)): 
                self.game_over = True
        elif(self.current_piece_key is not None): 
            if(not is_valid_position(self.board, NORMAL_SPAWN_POSITION_X, NORMAL_SPAWN_POSITION_Y, 0, self.current_piece_key)): 
                self.game_over = True
        
    def hold_piece(self): 
        temp_pk = self.current_piece_key
        if(self.held_piece_key is None): # first time taking a piece out
            self.held_piece_key = self.bag.pop(0)
        
        # swap (type shiii)
        self.current_piece_key = self.held_piece_key
        self.held_piece_key = temp_pk
        
    
    def get_piece_preview(self): 
        return self.bag[:PIECE_PREVIEW_AMOUNT]
    
    def return_board_state(self, move_tuple): 
        x, y, r, pk, T_spin = move_tuple
        self.board.lock_piece(x, y, r, pk)
        result = [row[:] for row in self.board.board]
        self.board.unlock_piece(x, y, r, pk)
        return result
    
    

class Board: 
    def __init__(self, height=MATRIX_HEIGHT, width=MATRIX_WIDTH): 
        self.height = height
        self.width = width
        self.board = [[0] * width for _ in range(height)]
        
    def lock_piece(self, x, y, rotation, piece_key): 
        actual_piece = get_piece_shape(piece_key, rotation)
        
        for r, row in enumerate(actual_piece): 
            for c, val in enumerate(row): 
                if val:
                    self.board[y + r][x + c] = 1
                    
    def unlock_piece(self, x, y, rotation, piece_key): 
        actual_piece = get_piece_shape(piece_key, rotation)
        
        for r, row in enumerate(actual_piece): 
            for c, val in enumerate(row): 
                if val:
                    self.board[y + r][x + c] = 0
                    
    def clear_lines(self): 
        # clears all rows of only 1s
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        
        lines_cleared = self.height - len(new_board)
        for i in range(lines_cleared): 
            new_board.insert(0, [0] * self.width)
            
        self.board = new_board
        
        return lines_cleared



class MoveScanner: 
    def get_all_legal_moves(self, game, piece_key): 
        board = game.board
        pk = piece_key
        moves = []
        
        start_x = NORMAL_SPAWN_POSITION_X
        start_y = NORMAL_SPAWN_POSITION_Y
        start_r = 0

        if(pk == 'I'): 
            start_x = I_PIECE_SPAWN_POSITION_X
            start_y = I_PIECE_SPAWN_POSITION_Y
        
        # BFS setup
        queue = deque()
        last_move_queue = deque()
        visited = set()
        
        queue.append((start_x, start_y, start_r))
        visited.add((start_x, start_y, start_r))
        last_move_queue.append(None)
        
        while(queue): 
            cur_x, cur_y, cur_r = queue.popleft() 
            last_move = last_move_queue.popleft()
            
            directions = [
                [-1, 0, 0], # left
                [1, 0, 0], # right
                [0, 1, 0] # down
            ]
            
            for dx, dy, dr in directions: 
                new_x, new_y, new_r = cur_x + dx, cur_y + dy, cur_r + dr
                
                if((new_x, new_y, new_r) not in visited): 
                    if(is_valid_position(board, new_x, new_y, new_r, pk)): 
                        visited.add((new_x, new_y, new_r))
                        queue.append((new_x, new_y, new_r))
                        if(dx == 0 and dy == 1): 
                            last_move_queue.append('M') 
                        else: 
                            last_move_queue.append('M') # movement (L or R)
                    elif(dx == 0 and dy == 1): 
                        if(pk == 'T'): # special thing for T-spins
                            if(last_move == 'LR'): 
                                T_spin = self.check_t_spin(board, cur_x, cur_y, cur_r, pk)
                                if(T_spin >= 1): 
                                    moves.append((cur_x, cur_y, cur_r, pk, 2)) # automatic t-spin (final kick + t-spin mini OR t-spin = t-spin)
                                else: 
                                    moves.append((cur_x, cur_y, cur_r, pk, T_spin)) # NO t-spin
                            elif(last_move == 'R'): 
                                T_spin = self.check_t_spin(board, cur_x, cur_y, cur_r, pk)
                                moves.append((cur_x, cur_y, cur_r, pk, T_spin))
                            else: 
                                moves.append((cur_x, cur_y, cur_r, pk, 0)) # NO T-spin (last move wasn't a rotation)
                        else: 
                            # for normal pieces (no T-spins)
                            moves.append((cur_x, cur_y, cur_r, pk, 0)) # final move found (cuz it can't move down no more :skull:)
            
            rot_directions = [-1, 1] # CCW and CW
            
            for dr in rot_directions: 
                new_r = (cur_r + dr) % 4
                
                kicks = SRS_TABLE[pk][cur_r][new_r]
                
                for i, kick in enumerate(kicks): 
                    dx, dy = kick[0], kick[1]
                    new_x, new_y = cur_x + dx, cur_y + dy
                    
                    if(is_valid_position(board, new_x, new_y, new_r, pk)): 
                        if((new_x, new_y, new_r) not in visited): 
                            visited.add((new_x, new_y, new_r))
                            queue.append((new_x, new_y, new_r))
                            if(i == len(kicks) - 1): 
                                last_move_queue.append("LR") # rotation fit on LAST KICK
                            else: 
                                last_move_queue.append("R") # last move for this new appended placement-to-visit was a rotation
                        break # possible rotation found OR already visited the possible kick -> end kick testing
        
        return moves
    
    
    def check_t_spin(self, board, start_x, start_y, start_r, piece_key): 
        # returns 0 if NO t-spin
        # returns 1 if Mini t-spin
        # returns 2 if T-spin
        
        to_check = [(0,0), (2,0), (2,2), (0,2)]
        for rot in range(start_r): 
            to_check.append(to_check.pop(0))
        # first two in to_check will always be front corners, last two will always be back corners
        
        front_corners_occupied = 0
        back_corners_occupied = 0
        for i, candidate in enumerate(to_check): 
            x, y = candidate
            board_x = start_x + x
            board_y = start_y + y
            if(board_x < 0 or board_x >= board.width or board_y < 0 or board_y >= board.height): 
                # if the corner is out of bounds, it counts as a block
                if(i < 2): 
                    front_corners_occupied += 1
                else: 
                    back_corners_occupied += 1
            else: 
                if(board.board[board_y][board_x] == 1): 
                    # if the corner actually has a block
                    if(i < 2): 
                        front_corners_occupied += 1
                    else: 
                        back_corners_occupied += 1
                    
        if(front_corners_occupied == 2 and back_corners_occupied >= 1): 
            return 2 # T-spin
        elif(front_corners_occupied >= 1 and back_corners_occupied == 2): 
            return 1 # mini T-spin
        return 0
    
    
def is_valid_position(board, start_x, start_y, start_rot, piece_key): 
    # checks if a piece fits at (target_x, target_y) coordinates
    # returns False if it hits the wall, hits the floor, or intersects with another block
    actual_piece = get_piece_shape(piece_key, start_rot)
    
    for y, row in enumerate(actual_piece): 
        for x, cell in enumerate(row): 
            if cell: 
                board_x = start_x + x
                board_y = start_y + y

                # check board boundaries
                if board_x < 0 or board_x >= board.width:
                    return False
                if board_y >= board.height:
                    return False

                # check overlap with other blocks
                if board_y >= 0:
                    if board.board[board_y][board_x] == 1:
                        return False
    return True            
    
def get_piece_shape(pk, rotation): # does NOT return offsets, MUST do offsets later for rotations (for I and O pieces)
    result = SHAPES[pk]
    
    # matrix clockwise rotation code found online
    for i in range(rotation % 4): 
        result = [list(row) for row in zip(*result[::-1])]
        
    return result
  
# T-spin debugging
# 37 moves, 3 t-spins (2 normal, 1 mini)
  
# def debug(): 
#     board = Board()
#     board.board = [
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
#         [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
#         [1, 1, 1, 1, 1, 0, 1, 1, 1, 1]
#     ]
    
#     scanner = MoveScanner()
#     moves = scanner.get_all_legal_moves(board, 'T')
#     print(len(moves))

# if __name__ == "__main__": 
#     debug()