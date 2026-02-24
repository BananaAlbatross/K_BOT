from Bot_parts.base import *
import chess
import time

class SearchTimeout(Exception):
    pass

def minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    #Check time every position
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
            value = max(value, minimax(board, depth-1, alpha, beta, evaluator, start_time, time_limit))
            board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = POS_INF
        for move in board.legal_moves:
            board.push(move)
            value = min(value, minimax(board, depth-1, alpha, beta, evaluator, start_time, time_limit))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def search_fixed_depth(board, depth, evaluator, start_time, time_limit):
    best_move = None
    turn = board.turn
    alpha = NEG_INF
    beta = POS_INF
    best_value = NEG_INF if turn else POS_INF

    for move in board.legal_moves:
        if time.time() - start_time > time_limit:
            raise SearchTimeout()
            
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
            
    return best_move

def search(board, depth, evaluator):
    start_time = time.time()
    time_limit = 0.95 #Not 1.00 for buffer
    best_move_found = None
    
    #Iterative deepening
    try:
        for d in range(1, depth + 1):
            result = search_fixed_depth(board, d, evaluator, start_time, time_limit)
            if result:
                best_move_found = result
    except SearchTimeout:
        pass
    
    #Best found or random
    return best_move_found or next(iter(board.legal_moves))