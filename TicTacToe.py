class Player:
    def __init__(self, id, name, symbol):
        self.id = id
        self.name = name
        self.symbol = symbol

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_symbol(self):
        return self.symbol


class Board:
    def __init__(self, size):
        self.size = size
        self.board = [[' '] * self.size for _ in range(self.size)]

    def make_move(self, r, c, player):
        if self.board[r][c] != ' ':
            return False
        self.board[r][c] = player.get_symbol()
        return True

    def check_winner(self):
        # Check Rows
        for i in range(self.size):
            if all(self.board[i][j] == self.board[i][0] and self.board[i][0] != ' ' for j in range(self.size)):
                return self.board[i][0]

        # Check Columns
        for i in range(self.size):
            if all(self.board[j][i] == self.board[0][i] and self.board[0][i] != ' ' for j in range(self.size)):
                return self.board[0][i]

        # Check Positive Diagonal
        if all(self.board[i][i] == self.board[0][0] and self.board[0][0] != ' ' for i in range(self.size)):
            return self.board[0][0]

        # Check Negative Diagonal
        if all(self.board[i][self.size - 1 - i] == self.board[0][self.size - 1] and self.board[0][self.size - 1] != ' ' for i in range(self.size)):
            return self.board[0][self.size - 1]

        return None


class TicTacToe:
    def __init__(self, players, board_size=3):
        self.players = players
        self.board = Board(board_size)
        self.curr_move = 0  # 0: player_1, 1: player_2

    def make_move(self, r, c):
        curr_player = self.players[self.curr_move]
        if self.board.make_move(r, c, curr_player):
            # Switch player turn
            self.curr_move = 1 - self.curr_move
            return True
        return False

    def play(self, moves):
        for r, c in moves:
            if not self.make_move(r, c):
                print(f"Invalid move at ({r}, {c})")
            # Check for winner after every move
            winner = self.check_winner()
            if winner != 'No Winner Yet':
                print(f"Winner: {winner}")
                return

    def check_winner(self):
        winner_symbol = self.board.check_winner()

        if winner_symbol:
            # Find the player who has the winning symbol
            for player in self.players:
                if player.get_symbol() == winner_symbol:
                    return player.get_name()
        return 'No Winner Yet'


player1 = Player(1, "Alice", 'X')
player2 = Player(2, "Bob", 'O')

game = TicTacToe([player1, player2], 3)
moves = [
    (0, 0),  # Player 1 (X) moves
    (0, 1),  # Player 2 (O) moves
    (1, 1),  # Player 1 (X) moves
    (2, 2),  # Player 2 (O) moves
    (2, 1),  # Player 1 (X) moves
    (1, 0),  # Player 2 (O) moves
    (1, 2),  # Player 1 (X) moves
]

game.play(moves)
print(game.check_winner())