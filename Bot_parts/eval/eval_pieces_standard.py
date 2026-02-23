from base import *

def evaluate(board):
    score = 0
    
    # Count pieces and increment score
    for i in scores:
        score += scores[i] * len(board.pieces(i, True)) # True is white
        score -= scores[i] * len(board.pieces(i, False)) # False is black
    return score