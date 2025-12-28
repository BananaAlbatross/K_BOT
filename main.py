import chess
import random
import re

play = True

board = chess.Board()

def evaluate(board):
    score = 0
    scores = {  "p": -100,  "b": -300,  "n": -300,  "r": -500,  "q": -900,  "k": -30000, 
                "P": 100,   "B": 300,   "N": 300,   "R": 500,   "Q": 900,   "K": 30000,
                "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0}
    for i in re.sub(r'\d+', '', board.fen().split()[0].replace("/", "")):
        score += scores[i]
    return score

if play:
    while not board.is_game_over():
        best_move = None
        highest_value = -63000

        legal_moves = list(board.legal_moves)
        for i in legal_moves:
            board.push(i)
            value = evaluate(board)
            board.pop()
            if value > highest_value:
                highest_value = value
                best_move = i
                
        board.push(best_move)
        print(board)
        print()

    print("GG " + board.result())


