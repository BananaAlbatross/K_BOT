import chess
import random
import re

play = True

board = chess.Board()
board.pieces
def evaluate(board):
    score = 0
    scores = {
        chess.PAWN: 100,
        chess.BISHOP: 300,
        chess.KNIGHT: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 30000
    }
    for i in scores:
        # Loendame nuppe ja arvutame skoori
        score += scores[i] * len(board.pieces(i, True)) # True on valge
        score -= scores[i] * len(board.pieces(i, False)) # False on must
    return score

if play:
    while not board.is_game_over():
        turn = board.turn
        best_move = None
        highest_value = -63000 if turn else 63000

        legal_moves = list(board.legal_moves)
        for i in legal_moves:
            board.push(i)
            value = evaluate(board)
            board.pop()
            if turn:
                if value > highest_value:
                    highest_value = value
                    best_move = i
            else:
                if value < highest_value:
                    highest_value = value
                    best_move = i
                
        board.push(best_move)
        print(board)
        print()

    print("GG " + board.result())


