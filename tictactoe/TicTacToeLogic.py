'''
Board class for the game of TicTacToe.
Default board size is 3x3.
Board data:
  1=white(O), -1=black(X), 0=empty
  first dim is column , 2nd is row:
     pieces[0][0] is the top left square,
     pieces[2][0] is the bottom left square,
Squares are stored and manipulated as (x,y) tuples.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the board for the game of Othello by Eric P. Nichols.

'''
# from bkcharts.attributes import color
class Board():

    # list of all 8 directions on the board, as (x,y) offsets
    __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]
    __directions_next = [(2,2),(1,2),(0,2),(-1,2),(-2,2), (2,-2),(1,-2),(0,-2),(-1,-2),(-2,-2), (2,1),(2,0),(2,-1), (-2,1),(-2,0),(-2,-1)]

    # @param n - number of cells
    def __init__(self, n):

        "Set up initial board configuration."

        self.n = n
        # Create the empty board array.
        self.pieces = [None]*self.n
        for i in range(self.n):
            self.pieces[i] = [0]*self.n

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def is_valid(self, x_pos, y_pos):
        if x_pos < 0 or y_pos < 0 or x_pos >= self.n or y_pos >= self.n:
            return False
        
        return True

    def is_legal(self, color, x_pos, y_pos):
        if self[x_pos][y_pos] != 0:
            return False
        
        for item in self.__directions:
            if self.is_valid(x_pos + item[0], y_pos + item[1]) and self[x_pos + item[0]][y_pos + item[1]] != 0:
                return True
            
        #for item in self.__directions_next:
        #    if self.is_valid(x_pos + item[0], y_pos + item[1]) and self[x_pos + item[0]][y_pos + item[1]] != 0:
        #        return True

        return False 

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black)
        @param color not used and came from previous version.        
        """
        moves = set()  # stores the legal moves.

        # Get all the empty squares (color==0)
        for y in range(self.n):
            for x in range(self.n):
                if self.is_legal(color, x, y):
                    newmove = (x,y)
                    moves.add(newmove)

        if moves == set() and self[0][0] == 0:
            for y in range(self.n):
                for x in range(self.n):
                    newmove = (x,y)
                    moves.add(newmove)

        return list(moves)

    def has_legal_moves(self):
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    return True
        return False
    
    def is_win(self, color):
        """Check whether the given player has collected a triplet in any direction; 
        @param color (1=white,-1=black)
        """
        win = 5#self.n
        # check y-strips
        for y in range(self.n):
            count = 0
            for x in range(self.n):
                if self[x][y]==color:
                    count += 1
                else:
                    count = 0
                
                if count==win:
                    return True
                
        # check x-strips
        for x in range(self.n):
            count = 0
            for y in range(self.n):
                if self[x][y]==color:
                    count += 1
                else:
                    count = 0
                
                if count==win:
                    return True
        
        # check down diagonal strips
        start_x_pos = self.n - 1
        start_y_pos = 0

        while start_x_pos >= 0:
            count = 0
            x = start_x_pos
            y = start_y_pos

            start_x_pos -= 1
            while x < self.n:
                if self[x][y]==color:
                    count += 1
                else:
                    count = 0
                
                if count==win:
                    return True
                else:
                    x += 1
                    y += 1 
		
        start_x_pos = 0
        start_y_pos = 1
        
        while start_y_pos < self.n:
            count = 0
            x = start_x_pos
            y = start_y_pos

            start_y_pos += 1 
            while y < self.n:
                if self[x][y]==color:
                    count += 1
                else:
                    count = 0
                
                if count==win:
                    return True
                else:
                    x += 1
                    y += 1


        # check up diagonal strips
        start_x_pos = 0
        start_y_pos = 0

        while start_x_pos < self.n:
            count = 0
            x = start_x_pos
            y = start_y_pos

            start_x_pos += 1
            while x >= 0:
                if self[x][y]==color:
                    count += 1
                else:
                    count = 0
                
                if count==win:
                    return True
                else:
                    x -= 1
                    y += 1 
		
        start_x_pos = self.n - 1
        start_y_pos = 1
        
        while start_y_pos < self.n:
            count = 0
            x = start_x_pos
            y = start_y_pos

            start_y_pos += 1 
            while y < self.n:
                if self[x][y]==color:
                    count += 1
                else:
                    count = 0
                
                if count==win:
                    return True
                else:
                    x -= 1
                    y += 1
        
        
        return False

    def execute_move(self, move, color):
        """Perform the given move on the board; 
        color gives the color pf the piece to play (1=white,-1=black)
        """

        (x,y) = move

        # Add the piece to the empty square.
        assert self[x][y] == 0
        self[x][y] = color

