import chess

def evaluate_mobility(board):
    score = 0
    
    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for square in board.pieces(piece_type, chess.WHITE):
            board.turn = chess.WHITE
            moves = board.attacks(square)
            score += len(moves) * 2  # weight
        
        for square in board.pieces(piece_type, chess.BLACK):
            board.turn = chess.BLACK
            moves = board.attacks(square)
            score -= len(moves) * 2
    
    return score