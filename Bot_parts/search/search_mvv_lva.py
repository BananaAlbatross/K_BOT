from Bot_parts.base import *
import chess
import time

SCORES = {
    # AlphaZero (2020) piece values
        chess.PAWN: 100,
        chess.KNIGHT: 305,
        chess.BISHOP: 333,
        chess.ROOK: 563,
        chess.QUEEN: 950,
        chess.KING: 30000
    }

MOVE_ORDERING_SCORES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000
}

class SearchTimeout(Exception):
    pass

def mvv_lva_score(board, move):
    if move.promotion:
        return 10000 + 100 * MOVE_ORDERING_SCORES.get(move.promotion, 0)
    
    if board.is_en_passant(move):
        return 8000
    
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            # Standard MVV-LVA formula: (10 * victim) - attacker
            return 1000 * MOVE_ORDERING_SCORES.get(victim.piece_type, 0) - MOVE_ORDERING_SCORES.get(attacker.piece_type, 0)
        return 1000
    
    return 0

def minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    # Time check
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0
    if depth == 0 or board.is_game_over():
        return evaluator(board)

    moves = list(board.legal_moves)
    moves.sort(key=lambda m: mvv_lva_score(board, m), reverse=True)

    if board.turn == chess.WHITE:
        value = NEG_INF
        for move in moves:
            board.push(move)
            try:
                val = minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                value = max(value, val)
            finally:
                board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = POS_INF
        for move in moves:
            board.push(move)
            try:
                val = minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                value = min(value, val)
            finally:
                board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def select_move(board, depth, evaluator):
    start_time = time.time()
    time_limit = 0.95 # Buffer for safety
    
    best_move = None
    turn = board.turn
    alpha = NEG_INF
    beta = POS_INF
    best_value = NEG_INF if turn else POS_INF
    
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: mvv_lva_score(board, m), reverse=True)

    try:
        for move in moves:
            board.push(move)
            try:
                val = minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
            finally:
                board.pop()

            if turn:
                if val > best_value:
                    best_value = val
                    best_move = move
                alpha = max(alpha, best_value)
            else:
                if val < best_value:
                    best_value = val
                    best_move = move
                beta = min(beta, best_value)
                
    except SearchTimeout:
        pass

    return best_move if best_move is not None else next(iter(board.legal_moves))
