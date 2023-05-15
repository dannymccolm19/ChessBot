import ChessEngine as ce
import chess as ch

class Main:
    
    def __init__(self, board=ch.Board):
        if board is None:
            board = ch.Board()
        self.board = board


    def playHumanMove(self):
       while True:
            if len(self.board.move_stack) > 0:
                print(self.board.peek())
            print(self.board.legal_moves)
            print("""To undo your last move, type "undo".""")

            play = input("Your move: ")
            if play == "undo":
                self.board.pop()
                self.board.pop()
                continue
            try:
                self.board.push_san(play)
                break
            except ValueError:
                print("Invalid move. Please try again.")

 
    def playEngineMove(self, maxDepth, color):
        engine = ce.Engine(self.board, maxDepth, color)
        self.board.push(engine.getBestMove())


    def startGame(self):
        while True:
            color = None
            while color not in ("b", "w"):
                color = input('Play as (type "b" or "w"): ')

            maxDepth = None
            while not isinstance(maxDepth, int):
                try:
                    maxDepth = int(input("Choose depth: "))
                except ValueError:
                    pass

            if color == "b":
                while not self.board.is_checkmate():
                    print("The engine is thinking...")
                    self.playEngineMove(maxDepth, ch.WHITE)
                    print(self.board)
                    self.playHumanMove()
                    print(self.board)
                print(self.board)
                print(self.board.outcome())
            elif color == "w":
                while not self.board.is_checkmate():
                    print(self.board)
                    self.playHumanMove()
                    print(self.board)
                    print("The engine is thinking...")
                    self.playEngineMove(maxDepth, ch.BLACK)
                    
                print(self.board)
                print(self.board.outcome())

            self.board.reset()


newBoard= ch.Board()
game = Main(newBoard)
newGame = game.startGame()
