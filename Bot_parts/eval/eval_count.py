import chess

SCORES = {
    # AlphaZero (2020) piece values
        chess.PAWN: 100,
        chess.KNIGHT: 305,
        chess.BISHOP: 333,
        chess.ROOK: 563,
        chess.QUEEN: 950,
        chess.KING: 30000
    }

def evaluate(board):
    score = 0
    
    # Count pieces and increment score
    for i in SCORES:
        score += SCORES[i] * len(board.pieces(i, True)) # True is white
        score -= SCORES[i] * len(board.pieces(i, False)) # False is black
    return score