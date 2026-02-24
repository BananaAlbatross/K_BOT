import time
import chess
from Bot_parts.base import *

# FEN key transposition table
TT = {}

class SearchTimeout(Exception):
    pass

def tt_lookup(board, depth):
    key = board.fen()
    entry = TT.get(key)
    if not entry:
        return None
    stored_depth, score = entry
    
    if stored_depth >= depth:
        return score
    return None

def tt_store(board, depth, score):
    key = board.fen()
    TT[key] = (depth, score)

def minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    # Time Check
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    #TT
    stored_score = tt_lookup(board, depth)
    if stored_score is not None:
        return stored_score

    #Case check
    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0
    if depth == 0 or board.is_game_over():
        val = evaluator(board)
        tt_store(board, depth, val)
        return val

    #Search
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
    
    #TT store
    tt_store(board, depth, value)
    return value

def select_move(board, depth, evaluator):
    start_time = time.time()
    time_limit = 0.95
    
    best_move = None
    turn = board.turn
    alpha = NEG_INF
    beta = POS_INF
    best_value = NEG_INF if turn else POS_INF

    # Clear TT or keep it between moves? 
    # For a fair "ELO" test, usually keep it to show the benefit of TT.
    
    try:
        for move in board.legal_moves:
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
