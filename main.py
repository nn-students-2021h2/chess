from chess.renderer import ConsoleRenderer
from chess.game import ChessGame

def main():
    renderer = ConsoleRenderer()
    game = ChessGame(renderer)
    game.run()

if __name__ == "__main__":
    main()