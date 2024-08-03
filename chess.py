# Expanded Chess Game in Python

class ChessPiece:
    def __init__(self, color):
        self.color = color

    def __str__(self):
        return self.__class__.__name__[0]  # Return the first letter of the class name

    def valid_move(self, start, end, board):
        raise NotImplementedError("This method should be overridden by subclasses")

class Pawn(ChessPiece):
    def valid_move(self, start, end, board):
        direction = 1 if self.color == 'white' else -1
        # Basic pawn move logic
        if start[0] == end[0] and (end[1] - start[1] == direction or
            (start[1] in [1, 6] and end[1] - start[1] == 2 * direction)):
            return board[end[0]][end[1]] is None
        # Pawn capture logic
        if abs(start[0] - end[0]) == 1 and end[1] - start[1] == direction:
            return board[end[0]][end[1]] is not None and board[end[0]][end[1]].color != self.color
        return False

class Rook(ChessPiece):
    def valid_move(self, start, end, board):
        if start[0] != end[0] and start[1] != end[1]:
            return False
        step = 1 if end[0] == start[0] else -1
        if start[0] == end[0]:
            for i in range(start[1] + step, end[1], step):
                if board[start[0]][i] is not None:
                    return False
        else:
            for i in range(start[0] + step, end[0], step):
                if board[i][start[1]] is not None:
                    return False
        return board[end[0]][end[1]] is None or board[end[0]][end[1]].color != self.color

class Knight(ChessPiece):
    def valid_move(self, start, end, board):
        dx, dy = abs(start[0] - end[0]), abs(start[1] - end[1])
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

class Bishop(ChessPiece):
    def valid_move(self, start, end, board):
        if abs(start[0] - end[0]) != abs(start[1] - end[1]):
            return False
        dx = 1 if end[0] > start[0] else -1
        dy = 1 if end[1] > start[1] else -1
        x, y = start[0] + dx, start[1] + dy
        while (x, y) != (end[0], end[1]):
            if board[x][y] is not None:
                return False
            x += dx
            y += dy
        return board[end[0]][end[1]] is None or board[end[0]][end[1]].color != self.color

class Queen(ChessPiece):
    def valid_move(self, start, end, board):
        return Rook(self.color).valid_move(start, end, board) or Bishop(self.color).valid_move(start, end, board)

class King(ChessPiece):
    def valid_move(self, start, end, board):
        return max(abs(start[0] - end[0]), abs(start[1] - end[1])) == 1

class Board:
    def __init__(self):
        self.board = self.create_board()
        self.current_turn = 'white'

    def create_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        for i in range(8):
            board[1][i] = Pawn('white')
            board[6][i] = Pawn('black')

        for color, row in zip(['white', 'black'], [0, 7]):
            board[row][0] = Rook(color)
            board[row][1] = Knight(color)
            board[row][2] = Bishop(color)
            board[row][3] = Queen(color)
            board[row][4] = King(color)
            board[row][5] = Bishop(color)
            board[row][6] = Knight(color)
            board[row][7] = Rook(color)

        return board

    def print_board(self):
        for row in self.board:
            print(' '.join(str(piece) if piece else '.' for piece in row))
        print()

    def move_piece(self, start, end):
        piece = self.board[start[0]][start[1]]
        if piece and piece.color == self.current_turn:
            if piece.valid_move(start, end, self.board):
                self.board[end[0]][end[1]] = piece
                self.board[start[0]][start[1]] = None
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'
            else:
                print("Invalid move!")
        else:
            print("No piece at start position or not your turn!")

def main():
    board = Board()
    board.print_board()
    
    while True:
        move = input(f"{board.current_turn.capitalize()}'s turn. Enter move (e.g., 'a2 a3'): ")
        try:
            start_pos, end_pos = move.split()
            start = (8 - int(start_pos[1]), ord(start_pos[0]) - ord('a'))
            end = (8 - int(end_pos[1]), ord(end_pos[0]) - ord('a'))
            board.move_piece(start, end)
            board.print_board()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
