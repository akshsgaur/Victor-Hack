import sys

# First, let's check if the required library 'python-chess' is installed.
try:
    import chess
except ImportError:
    print(
        "This script requires the 'python-chess' library. "
        "Please install it using 'pip install python-chess'.",
        file=sys.stderr
    )
    sys.exit(1)

# Define the ChessGame class
class ChessGame:
    def __init__(self):
        self.board = chess.Board()

    def print_board(self):
        # Print the board to the console
        print(self.board)

    def is_game_over(self):
        # Check if the game is over
        return self.board.is_game_over()

    def move(self, uci):
        try:
            move = chess.Move.from_uci(uci)
            if move in self.board.legal_moves:
                self.board.push(move)
            else:
                print("That is not a legal move. Please try again.")
        except ValueError:
            print("Invalid move format. Please use UCI format like 'e2e4'.")

    def play(self):
        # Main game loop
        try:
            while not self.is_game_over():
                self.print_board()
                print("Current turn: " + ("White" if self.board.turn == chess.WHITE else "Black"))
                uci = input("Enter your move in UCI format (e.g., e2e4): ")
                self.move(uci)
            print("Game over.")
            print("Result: " + self.board.result())
        except KeyboardInterrupt:
            print("\nGame interrupted.")

if __name__ == "__main__":
    game = ChessGame()
    try:
        game.play()
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)