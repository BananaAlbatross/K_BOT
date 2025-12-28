import chess
import random

play = True

board = chess.Board()

if play:
    while not board.is_game_over():
        move = random.choice(list(board.legal_moves))
                
        board.push(move)
        print(board)
        print()

    print("GG " + board.result())


 