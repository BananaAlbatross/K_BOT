from Bot_parts.base import *
import chess
import time

class SearchTimeout(Exception):
    pass

def minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0
    if depth == 0 or board.is_game_over():
        return evaluator(board)

    if board.turn == chess.WHITE:
        value = NEG_INF
        for move in board.legal_moves:
            board.push(move)
            try:
                res = minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                value = max(value, res)
            finally:
                board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = POS_INF
        for move in board.legal_moves:
            board.push(move)
            try:
                res = minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                value = min(value, res)
            finally:
                board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def select_move(board, depth, evaluator):
    start_time = time.time()
    time_limit = 0.95  #0.95 vs 1 -- buffer
    
    best_move = None
    turn = board.turn
    alpha = NEG_INF
    beta = POS_INF
    best_value = NEG_INF if turn else POS_INF

    try:
        for move in board.legal_moves:
            board.push(move)
            # Pass the timer into the recursive calls
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
    
    #Best found or random
    return best_move if best_move is not None else next(iter(board.legal_moves))