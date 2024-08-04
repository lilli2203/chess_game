class ChessPiece:
    def __init__(self, color):
        self.color = color

    def __str__(self):
        return self.__class__.__name__[0]  

    def valid_move(self, start, end, board):
        raise NotImplementedError("This method should be overridden by subclasses")

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def valid_move(self, start, end, board):
        direction = 1 if self.color == 'white' else -1
        if start[0] == end[0] and (end[1] - start[1] == direction or
            (start[1] in [1, 6] and end[1] - start[1] == 2 * direction and not self.has_moved)):
            return board[end[0]][end[1]] is None
        if abs(start[0] - end[0]) == 1 and end[1] - start[1] == direction:
            return board[end[0]][end[1]] is not None and board[end[0]][end[1]].color != self.color
        return False

    def promote(self, position, board):
        if (self.color == 'white' and position[1] == 7) or (self.color == 'black' and position[1] == 0):
            new_piece = input("Promote to (Q, R, B, N): ").upper()
            if new_piece == 'Q':
                board[position[0]][position[1]] = Queen(self.color)
            elif new_piece == 'R':
                board[position[0]][position[1]] = Rook(self.color)
            elif new_piece == 'B':
                board[position[0]][position[1]] = Bishop(self.color)
            elif new_piece == 'N':
                board[position[0]][position[1]] = Knight(self.color)

class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

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
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def valid_move(self, start, end, board):
        if max(abs(start[0] - end[0]), abs(start[1] - end[1])) == 1:
            return True
        if not self.has_moved and abs(start[0] - end[0]) == 2 and start[1] == end[1]:
            rook_pos = (0 if end[0] == 2 else 7, start[1])
            rook = board[rook_pos[0]][rook_pos[1]]
            if isinstance(rook, Rook) and not rook.has_moved:
                if all(board[i][start[1]] is None for i in range(min(start[0], end[0])+1, max(start[0], end[0]))):
                    return True
        return False

class Board:
    def __init__(self):
        self.board = self.create_board()
        self.current_turn = 'white'
        self.kings = {'white': (4, 0), 'black': (4, 7)}
        self.last_move = None
        self.move_history = []

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
                # En passant capture
                if isinstance(piece, Pawn) and abs(start[0] - end[0]) == 1 and self.board[end[0]][end[1]] is None:
                    self.board[end[0]][start[1]] = None
                
                original_end_piece = self.board[end[0]][end[1]]
                self.board[end[0]][end[1]] = piece
                self.board[start[0]][start[1]] = None

                if self.in_check(self.current_turn):
                    self.board[start[0]][start[1]] = piece
                    self.board[end[0]][end[1]] = original_end_piece
                    print("Move leaves king in check!")
                    return

                if isinstance(piece, Pawn):
                    piece.promote(end, self.board)
                    piece.has_moved = True

                if isinstance(piece, King):
                    piece.has_moved = True
                    self.kings[piece.color] = end

                if isinstance(piece, Rook):
                    piece.has_moved = True

                self.move_history.append((start, end))
                self.last_move = (start, end)
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                
                if self.in_check(self.current_turn):
                    print(f"{self.current_turn.capitalize()} is in check!")
                if self.in_checkmate(self.current_turn):
                    print(f"{self.current_turn.capitalize()} is in checkmate! Game over.")
                    exit()
                if self.is_stalemate(self.current_turn):
                    print("Stalemate! Game over.")
                    exit()
            else:
                print("Invalid move!")
        else:
            print("No piece at start position or not your turn!")

    def in_check(self, color):
        king_pos = self.kings[color]
        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if piece and piece.color != color and piece.valid_move((x, y), king_pos, self.board):
                    return True
        return False

    def in_checkmate(self, color):
        if not self.in_check(color):
            return False
        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if piece and piece.color == color:
                    for i in range(8):
                        for j in range(8):
                            if piece.valid_move((x, y), (i, j), self.board):
                                original_end_piece = self.board[i][j]
                                self.board[i][j] = piece
                                self.board[x][y] = None
                                if not self.in_check(color):
                                    self.board[x][y] = piece
                                    self.board[i][j] = original_end_piece
                                    return False
                                self.board[x][y] = piece
                                self.board[i][j] = original_end_piece
        return True

    def is_stalemate(self, color):
        if self.in_check(color):
            return False
        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if piece and piece.color == color:
                    for i in range(8):
                        for j in range(8):
                            if piece.valid_move((x, y), (i, j), self.board):
                                original_end_piece = self.board[i][j]
                                self.board[i][j] = piece
                                self.board[x][y] = None
                                if not self.in_check(color):
                                    self.board[x][y] = piece
                                    self.board[i][j] = original_end_piece
                                    return False
                                self.board[x][y] = piece
                                self.board[i][j] = original_end_piece
        return True

def offer_draw():
    response = input("Do you agree to a draw? (yes/no): ").lower()
    return response == 'yes'

def main():
    board = Board()
    board.print_board()
    
    while True:
        move = input(f"{board.current_turn.capitalize()}'s turn. Enter move (e.g., 'a2 a3') or type 'draw' to offer a draw: ")
        if move.lower() == 'draw':
            if offer_draw():
                print("Draw agreed. Game over.")
                break
        else:
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
