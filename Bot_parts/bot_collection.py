import random
import sys
import chess.polyglot
import chess
import time
import itertools
import sys

if len(sys.argv) > 1:
    CHOSEN_BOT = sys.argv[1]
else:
    CHOSEN_BOT = "C3" #Fallback

print(f"info string KaarenBot version 1.0 initialized as {CHOSEN_BOT}")
print(sys.argv[1])

#1, 2, 3, 4 -- default minimax, mvv_lva, iterative deepening, transposition table + mvv-lva
#A, B, C -- eval_material, eval_PST1, eval_PST2

# ------------- Definitions / Constants -------------

PLAY = True
TOL = 1  # Tolerance for near-best moves
DEPTHS = {
    "A1": 2,
    "A2": 4,
    "A3": 6,
    "A4": 5,
    "B1": 2,
    "B2": 4,
    "B3": 6,
    "B4": 5,
    "C1": 2,
    "C2": 4,
    "C3": 6,
    "C4": 5,
}
MATE_SCORE = 100000
NEG_INF = -99999
POS_INF = 99999
board = chess.Board()
move_times = []
TT = {}
nodes_visited = 0

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

PST_MG = {
    chess.PAWN: (
           0,    0,    0,    0,    0,    0,    0,    0,
           2,    4,   11,   18,   16,   21,    9,   -3,
          -9,  -15,   11,   15,   31,   23,    6,  -20,
          -3,  -20,    8,   19,   39,   17,    2,   -5,
          11,   -4,  -11,    2,   11,    0,  -12,    5,
           3,  -11,   -6,   22,   -8,   -5,  -14,  -11,
          -7,    6,   -2,  -11,    4,  -14,   10,   -9,
           0,    0,    0,    0,    0,    0,    0,    0,
    ),

    chess.KNIGHT: (
        -175,  -92,  -74,  -73,  -73,  -74,  -92, -175,
         -77,  -41,  -27,  -15,  -15,  -27,  -41,  -77,
         -61,  -17,    6,   12,   12,    6,  -17,  -61,
         -35,    8,   40,   49,   49,   40,    8,  -35,
         -34,   13,   44,   51,   51,   44,   13,  -34,
          -9,   22,   58,   53,   53,   58,   22,   -9,
         -67,  -27,    4,   37,   37,    4,  -27,  -67,
        -201,  -83,  -56,  -26,  -26,  -56,  -83, -201,
    ),

    chess.BISHOP: (
         -37,   -4,   -6,  -16,  -16,   -6,   -4,  -37,
         -11,    6,   13,    3,    3,   13,    6,  -11,
          -5,   15,   -4,   12,   12,   -4,   15,   -5,
          -4,    8,   18,   27,   27,   18,    8,   -4,
          -8,   20,   15,   22,   22,   15,   20,   -8,
         -11,    4,    1,    8,    8,    1,    4,  -11,
         -12,  -10,    4,    0,    0,    4,  -10,  -12,
         -34,    1,  -10,  -16,  -16,  -10,    1,  -34,
    ),

    chess.ROOK: (
         -31,  -20,  -14,   -5,   -5,  -14,  -20,  -31,
         -21,  -13,   -8,    6,    6,   -8,  -13,  -21,
         -25,  -11,   -1,    3,    3,   -1,  -11,  -25,
         -13,   -5,   -4,   -6,   -6,   -4,   -5,  -13,
         -27,  -15,   -4,    3,    3,   -4,  -15,  -27,
         -22,   -2,    6,   12,   12,    6,   -2,  -22,
          -2,   12,   16,   18,   18,   16,   12,   -2,
         -17,  -19,   -1,    9,    9,   -1,  -19,  -17,
    ),

    chess.QUEEN: (
          3,   -5,   -5,    4,    4,   -5,   -5,    3,
         -3,    5,    8,   12,   12,    8,    5,   -3,
         -3,    6,   13,    7,    7,   13,    6,   -3,
          4,    5,    9,    8,    8,    9,    5,    4,
          0,   14,   12,    5,    5,   12,   14,    0,
         -4,   10,    6,    8,    8,    6,   10,   -4,
         -5,    6,   10,    8,    8,   10,    6,   -5,
         -2,   -2,    1,   -2,   -2,    1,   -2,   -2,
    ),

    chess.KING: (
         271,  327,  271,  198,  198,  271,  327,  271,
         278,  303,  234,  179,  179,  234,  303,  278,
         195,  258,  169,  120,  120,  169,  258,  195,
         164,  190,  138,   98,   98,  138,  190,  164,
         154,  179,  105,   70,   70,  105,  179,  154,
         123,  145,   81,   31,   31,   81,  145,  123,
          88,  120,   65,   33,   33,   65,  120,   88,
          59,   89,   45,   -1,   -1,   45,   89,   59,
    ),
}

PST_EG = {
    chess.PAWN: (
          0,    0,    0,    0,    0,    0,    0,    0,
         -8,   -6,    9,    5,   16,    6,   -6,  -18,
         -9,   -7,  -10,    5,    2,    3,   -8,   -5,
          7,    1,   -8,   -2,  -14,  -13,  -11,   -6,
         12,    6,    2,   -6,   -5,   -4,   14,    9,
         27,   18,   19,   29,   30,    9,    8,   14,
         -1,  -14,   13,   22,   24,   17,    7,    7,
          0,    0,    0,    0,    0,    0,    0,    0,
    ),

    chess.KNIGHT: (
         -96,  -65,  -49,  -21,  -21,  -49,  -65,  -96,
         -67,  -54,  -18,    8,    8,  -18,  -54,  -67,
         -40,  -27,   -8,   29,   29,   -8,  -27,  -40,
         -35,   -2,   13,   28,   28,   13,   -2,  -35,
         -45,  -16,    9,   39,   39,    9,  -16,  -45,
         -51,  -44,  -16,   17,   17,  -16,  -44,  -51,
         -69,  -50,  -51,   12,   12,  -51,  -50,  -69,
        -100,  -88,  -56,  -17,  -17,  -56,  -88, -100,
    ),

    chess.BISHOP: (
         -40,  -21,  -26,   -8,   -8,  -26,  -21,  -40,
         -26,   -9,  -12,    1,    1,  -12,   -9,  -26,
         -11,   -1,   -1,    7,    7,   -1,   -1,  -11,
         -14,   -4,    0,   12,   12,    0,   -4,  -14,
         -12,   -1,  -10,   11,   11,  -10,   -1,  -12,
         -21,    4,    3,    4,    4,    3,    4,  -21,
         -22,  -14,   -1,    1,    1,   -1,  -14,  -22,
         -32,  -29,  -26,  -17,  -17,  -26,  -29,  -32,
    ),

    chess.ROOK: (
         -9,  -13,  -10,   -9,   -9,  -10,  -13,   -9,
        -12,   -9,   -1,   -2,   -2,   -1,   -9,  -12,
          6,   -8,   -2,   -6,   -6,   -2,   -8,    6,
         -6,    1,   -9,    7,    7,   -9,    1,   -6,
         -5,    8,    7,   -6,   -6,    7,    8,   -5,
          6,    1,   -7,   10,   10,   -7,    1,    6,
          4,    5,   20,   -5,   -5,   20,    5,    4,
         18,    0,   19,   13,   13,   19,    0,   18,
    ),

    chess.QUEEN: (
         -69,  -57,  -47,  -26,  -26,  -47,  -57,  -69,
         -54,  -31,  -22,   -4,   -4,  -22,  -31,  -54,
         -39,  -18,   -9,    3,    3,   -9,  -18,  -39,
         -23,   -3,   13,   24,   24,   13,   -3,  -23,
         -29,   -6,    9,   21,   21,    9,   -6,  -29,
         -38,  -18,  -11,    1,    1,  -11,  -18,  -38,
         -50,  -27,  -24,   -8,   -8,  -24,  -27,  -50,
         -74,  -52,  -43,  -34,  -34,  -43,  -52,  -74,
    ),

    chess.KING: (
          1,   45,   85,   76,   76,   85,   45,    1,
         53,  100,  133,  135,  135,  133,  100,   53,
         88,  130,  169,  175,  175,  169,  130,   88,
        103,  156,  172,  172,  172,  172,  156,  103,
         96,  166,  199,  199,  199,  199,  166,   96,
         92,  172,  184,  191,  191,  184,  172,   92,
         47,  121,  116,  131,  131,  116,  121,   47,
         11,   59,   73,   78,   78,   73,   59,   11,
    ),
}

PHASE_SCORES = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4,
    chess.KING: 0
} # Max phase is 8*0 + 4*1 + 4*1 + 4*2 + 2*4 + 2*0 = 24 (with promotion exceptions)

class SearchTimeout(Exception):
    pass


# ------------- Evaluation functions -------------


def eval_material(board):
    score = 0
    
    # Count pieces and increment score
    for i in SCORES:
        score += SCORES[i] * len(board.pieces(i, True)) # True is white
        score -= SCORES[i] * len(board.pieces(i, False)) # False is black
    return score

def eval_PST1(board):
    score = 0
    
    for i in SCORES:
        # Score-table
        score += SCORES[i] * len(board.pieces(i, True)) # True is white
        score -= SCORES[i] * len(board.pieces(i, False)) # False is black

        # Piece-Square Table
        for square in board.pieces(i, True):
            score += PST_MG[i][square]
        for square in board.pieces(i, False):
            score -= PST_MG[i][chess.square_mirror(square)]
    return score

def eval_PST2(board):
    score = 0
    phase = 0

    # Count pieces, calculate phase, increment score
    for i in SCORES:
        
        # Count of piece type i
        whiteCount = len(board.pieces(i, True))
        blackCount = len(board.pieces(i, False))

        # Phase sum
        phase += PHASE_SCORES[i] * (whiteCount + blackCount)
    
        # Score Table
        score += SCORES[i] * whiteCount # True is white
        score -= SCORES[i] * blackCount # False is black
    
    # Phase mapping to interval [0, 1]
    mg_phase = max(0, min(1, phase/24.0))
    eg_phase = 1 - mg_phase

    for piece_type in SCORES:
        for square in board.pieces(piece_type, chess.WHITE):
            mg_val = PST_MG[piece_type][square]
            eg_val = PST_EG[piece_type][square]
            score += (mg_val * mg_phase + eg_val * eg_phase)
            
        for square in board.pieces(piece_type, chess.BLACK):
            m_sq = chess.square_mirror(square) 
            mg_val = PST_MG[piece_type][m_sq]
            eg_val = PST_EG[piece_type][m_sq]
            score -= (mg_val * mg_phase + eg_val * eg_phase)

    return score


# ------------- Search functions -------------


def quiescence(board, alpha, beta, evaluator, start_time, time_limit):
    global nodes_visited
    nodes_visited += 1
    current_turn = board.turn

    if nodes_visited % 100 == 0:
        if time.time() - start_time > time_limit:
            raise SearchTimeout()
    
    stand_pat = evaluator(board)

    if current_turn == chess.WHITE:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat

    for move in board.generate_legal_captures():
        board.push(move)
        try:
            score = quiescence(board, alpha, beta, evaluator, start_time, time_limit)
        finally:
            board.pop()
        if board.turn == chess.WHITE:
            if score > alpha:
                alpha = score
                if alpha >= beta:
                    break
        else:
            if score < beta:
                beta = score
                if beta <= alpha:
                    break
    return alpha if board.turn == chess.WHITE else beta

def choose_from_move_evals(move_evals, turn, fallback_board=None, debug_tag=None):
    tag = f"[{debug_tag}] " if debug_tag else ""
    if not move_evals:
        # nothing evaluated: pick any legal move (or None if none)
        if fallback_board is not None:
            try:
                fallback = next(iter(fallback_board.legal_moves))
                print(f"info string DEBUG: {tag}no evaluated moves, falling back to {fallback}", flush=True)
                return fallback
            except StopIteration:
                print(f"info string DEBUG: {tag}no legal moves available", flush=True)
                return None
        else:
            print(f"info string DEBUG: {tag}no evaluated moves and no fallback_board provided", flush=True)
            return None

    # compute best value
    if turn:  # white maximizes
        best_value = max(v for _, v in move_evals)
        candidates = [m for m, v in move_evals if best_value - v <= TOL]
        if candidates:
            return random.choice(candidates)
        return max(move_evals, key=lambda x: x[1])[0]
    else:     # black minimizes
        best_value = min(v for _, v in move_evals)
        candidates = [m for m, v in move_evals if v - best_value <= TOL]
        if candidates:
            return random.choice(candidates)
        return min(move_evals, key=lambda x: x[1])[0]
    

def default_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return (-MATE_SCORE-depth) if board.turn == chess.WHITE else (MATE_SCORE+depth)
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.is_repetition(2):
        return 0
    if depth == 0:
        return quiescence(board, alpha, beta, evaluator, start_time, time_limit)

    if board.turn == chess.WHITE:
        value = NEG_INF
        for move in board.legal_moves:
            board.push(move)
            try:
                res = default_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
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
                res = default_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                value = min(value, res)
            finally:
                board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def minimax_select_move(board, depth, evaluator, time_limit):
    start_time = time.time()
    time_limit *= 0.95 #buffer
    turn = board.turn

    for i in SCORES:
        mg_contrib = sum(PST_MG[i][sq] for sq in board.pieces(i, chess.WHITE))
        mg_contrib -= sum(PST_MG[i][chess.square_mirror(sq)] for sq in board.pieces(i, chess.BLACK))
        print(f"DEBUG PST piece={i} mg_contrib={mg_contrib}", flush=True)
    total_eval = evaluator(board)
    print(f"DEBUG total eval={total_eval}", flush=True)

    move_evals = []

    try:
        for move in board.legal_moves:
            board.push(move)
            try:
                # Evaluate each move with FULL window at root level to get true evaluations
                val = default_minimax(board, depth - 1, NEG_INF, POS_INF, evaluator, start_time, time_limit)
            finally:
                board.pop()

            mat = sum(SCORES[i] * (len(board.pieces(i, True)) - len(board.pieces(i, False))) for i in SCORES)
            print(f"DEBUG: {move.uci()} eval={val} material={mat}", flush=True)
            move_evals.append((move, val))
    except SearchTimeout:
        pass

    print("info string DEBUG: MINIMAX move evaluations:", " ".join(f"{m.uci()}={v}" for m, v in move_evals), flush=True)
    return choose_from_move_evals(move_evals, turn, fallback_board=board, debug_tag="minimax_select_move")

#--------------------------------------------------------

def iterative_deepening_order_moves(board, best_move_from_prev_depth=None):
    moves = list(board.legal_moves)
    
    def score_move(move):
        #Prioritise the best move from the previous iteration
        if best_move_from_prev_depth and move == best_move_from_prev_depth:
            return 1000000 
        
        return mvv_lva_score(board, move)

    moves.sort(key=score_move, reverse=True)
    return moves

def iterative_deepening_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    #Check time every position
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.is_repetition(2):
        return 0
    if depth == 0 or board.is_game_over():
        return quiescence(board, alpha, beta, evaluator, start_time, time_limit)

    if board.turn == chess.WHITE:
        value = NEG_INF
        for move in board.legal_moves:
            board.push(move)
            value = max(value, iterative_deepening_minimax(board, depth-1, alpha, beta, evaluator, start_time, time_limit))
            board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = POS_INF
        for move in board.legal_moves:
            board.push(move)
            value = min(value, iterative_deepening_minimax(board, depth-1, alpha, beta, evaluator, start_time, time_limit))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def iterative_deepening_fixed_depth_search(board, depth, evaluator, start_time, time_limit, prev_best):
    turn = board.turn
    move_evals = []
    ordered_moves = iterative_deepening_order_moves(board, prev_best)

    for move in ordered_moves:
        if time.time() - start_time > time_limit:
            raise SearchTimeout()

        board.push(move)
        try:
            # Evaluate each move with FULL window at root level to get true evaluations
            val = iterative_deepening_minimax(board, depth - 1, NEG_INF, POS_INF, evaluator, start_time, time_limit)
        finally:
            board.pop()

        move_evals.append((move, val))

    return choose_from_move_evals(move_evals, turn, fallback_board=board, debug_tag=f"iterative_deepening_fixed_depth_search d={depth}")

def iterative_deepening_search(board, depth, evaluator, time_limit):
    start_time = time.time()
    time_limit *= 0.95 #buffer
    best_move_found = None
    
    #Iterative deepening
    try:
        #Guaranteed depth 1
        best_move_found = iterative_deepening_fixed_depth_search(board, 1, evaluator, start_time, 999, None)
        
        for d in range(2, depth + 1):
            result = iterative_deepening_fixed_depth_search(board, d, evaluator, start_time, time_limit, best_move_found)
            if result:
                best_move_found = result
    except SearchTimeout:
        pass
    
    return best_move_found

#--------------------------------------------------------

def mvv_lva_score(board, move):
    if move.promotion:
        return 10000 + 100 * MOVE_ORDERING_SCORES.get(move.promotion, 0)
    
    if board.is_en_passant(move):
        return 8000
    
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            return 1000 * MOVE_ORDERING_SCORES.get(victim.piece_type, 0) - MOVE_ORDERING_SCORES.get(attacker.piece_type, 0)
        return 1000
    
    return 0

def mvv_lva_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    # Time check
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.is_repetition(2):
        return 0
    if depth == 0 or board.is_game_over():
        return quiescence(board, alpha, beta, evaluator, start_time, time_limit)

    moves = list(board.legal_moves)
    moves.sort(key=lambda m: mvv_lva_score(board, m), reverse=True)

    if board.turn == chess.WHITE:
        value = NEG_INF
        for move in moves:
            board.push(move)
            try:
                val = mvv_lva_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
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
                val = mvv_lva_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                value = min(value, val)
            finally:
                board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def mvv_lva_select_move(board, depth, evaluator, time_limit):
    start_time = time.time()
    time_limit *= 0.95 #buffer
    turn = board.turn
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: mvv_lva_score(board, m), reverse=True)
    move_evals = []

    try:
        for move in moves:
            board.push(move)
            try:
                # Evaluate each move with FULL window at root level to get true evaluations
                val = mvv_lva_minimax(board, depth - 1, NEG_INF, POS_INF, evaluator, start_time, time_limit)
            finally:
                board.pop()

            move_evals.append((move, val))

    except SearchTimeout:
        pass

    print("info string DEBUG: MVV-LVA move evaluations:", " ".join(f"{m.uci()}={v}" for m, v in move_evals), flush=True)
    return choose_from_move_evals(move_evals, turn, fallback_board=board, debug_tag="mvv_lva_select_move")

#--------------------------------------------------------

def tt_get_ordered_moves(board, tt_move=None):
    moves = list(board.legal_moves)
    
    def score_move(move):
        if move == tt_move:
            return 1000000
        if board.is_capture(move):
            return mvv_lva_score(board, move)
        return 0

    moves.sort(key=score_move, reverse=True)
    return moves

def tt_store(board, depth, score, move, flag='EXACT'):
    key = chess.polyglot.zobrist_hash(board)
    if key not in TT or TT[key][0] < depth:
        TT[key] = (depth, score, move, flag)

def tt_lookup(board, depth):
    key = chess.polyglot.zobrist_hash(board)
    entry = TT.get(key)
    if entry:
        stored_depth, score, move, flag = entry
        if stored_depth >= depth and flag == 'EXACT':
            return score, move
        return None, move
    return None, None

def transposition_table_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    best_move_at_node = None
    original_alpha = alpha
    # Time Check
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    #TT
    stored_score, tt_move = tt_lookup(board, depth)
    if stored_score is not None:
        return stored_score

    #Case check
    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.is_repetition(2):
        return 0
    if depth == 0 or board.is_game_over():
        val = quiescence(board, alpha, beta, evaluator, start_time, time_limit)
        return val

    ordered_moves = tt_get_ordered_moves(board, tt_move)

    #Search
    if board.turn == chess.WHITE:
        value = NEG_INF
        for move in ordered_moves:
            board.push(move)
            try:
                res = transposition_table_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                if res > value:
                    value = res
                    best_move_at_node = move
            finally:
                board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
    else:
        value = POS_INF
        for move in ordered_moves:
            board.push(move)
            try:
                res = transposition_table_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                if res < value:
                    value = res
                    best_move_at_node = move
            finally:
                board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
    
    # Determine flag
    if value <= original_alpha:
        flag = 'UPPER'  # failed low, score is an upper bound
    elif value >= beta:
        flag = 'LOWER'  # beta cutoff, score is a lower bound
    else:
        flag = 'EXACT'

    #TT store
    tt_store(board, depth, value, best_move_at_node, flag)
    return value

def transposition_table_select_move(board, max_depth, evaluator, time_limit):
    start_time = time.time()
    time_limit *= 0.95  # small buffer
    turn = board.turn
    ITERATIVE_DEEPENING = True

    if board.fullmove_number == 1 and board.turn == chess.WHITE:
        for move in list(board.legal_moves)[:5]:
            board.push(move)
            print(f"DEBUG direct eval {move.uci()} = {evaluator(board)}", flush=True)
            board.pop()

    best_move_overall = None
    best_value = NEG_INF if turn else POS_INF

    if ITERATIVE_DEEPENING:
        try:
            for depth in range(1, max_depth + 1):
                move_evals = []

                _, tt_move = tt_lookup(board, depth)
                ordered_moves = tt_get_ordered_moves(board, tt_move)

                if not ordered_moves:
                    break

                for move in ordered_moves:
                    if time.time() - start_time > time_limit:
                        raise SearchTimeout()

                    board.push(move)
                    try:
                        # Evaluate each move with FULL window at root level to get true evaluations
                        val = transposition_table_minimax(
                            board, depth - 1, NEG_INF, POS_INF, evaluator, start_time, time_limit
                        )
                    finally:
                        board.pop()

                    move_evals.append((move, val))

                if not move_evals:
                    break

                print("TT info string DEBUG: depth", depth, "ordered move evals:", [(m.uci(), v) for m, v in move_evals], flush=True)

                values = [v for _, v in move_evals]
                root_value = max(values) if turn else min(values)
                chosen = choose_from_move_evals(move_evals, turn, fallback_board=board, debug_tag=f"transposition_table_select_move_iter depth={depth}")

                # store result in TT and update best
                if chosen is not None:
                    tt_store(board, depth, root_value, chosen)
                    best_move_overall = chosen
                    best_value = root_value

        except SearchTimeout:
            pass

        # return best found or fallback to any legal move or None
        if best_move_overall is not None:
            print("Best move was " + best_move_overall.uci())
            return best_move_overall
        try:
            return next(iter(board.legal_moves))
        except StopIteration:
            return None

    else:
        # non-iterative fallback
        move_evals = []
        _, good_move = tt_lookup(board, max_depth)
        ordered_moves = tt_get_ordered_moves(board, good_move)

        try:
            for move in ordered_moves:
                if time.time() - start_time > time_limit:
                    raise SearchTimeout()
                board.push(move)
                try:
                    # Evaluate each move with FULL window at root level to get true evaluations
                    val = transposition_table_minimax(board, max_depth - 1, NEG_INF, POS_INF, evaluator, start_time, time_limit)
                finally:
                    board.pop()

                move_evals.append((move, val))

        except SearchTimeout:
            pass

        # final selection
        if not move_evals:
            print("info string DEBUG: no moves evaluated within time_limit, falling back", flush=True)
            try:
                return next(iter(board.legal_moves))
            except StopIteration:
                return None

        return choose_from_move_evals(move_evals, turn, fallback_board=board, debug_tag="transposition_table_select_move_non_iterative")


#-------------------------- ChessBot Class ------------------------------


class ChessBot:
    def __init__(self, name, search_func, eval_func):
        self.name = name
        self.search = search_func
        self.evaluate = eval_func
        self.depth=DEPTHS[name]

    def select_move(self, board, time_limit=1.0):
        return self.search(board, self.depth, self.evaluate, time_limit)

#1, 2, 3, 4 -- default minimax, mvv_lva, iterative deepening, transposition table
#A, B, C -- eval_material, eval_PST1, eval_PST2

bot_A1 = ChessBot("A1", minimax_select_move, eval_material)
bot_A2 = ChessBot("A2", mvv_lva_select_move, eval_material)
bot_A3 = ChessBot("A3", iterative_deepening_search, eval_material)
bot_A4 = ChessBot("A4", transposition_table_select_move, eval_material)

bot_B1 = ChessBot("B1", minimax_select_move, eval_PST1)
bot_B2 = ChessBot("B2", mvv_lva_select_move, eval_PST1)
bot_B3 = ChessBot("B3", iterative_deepening_search, eval_PST1)
bot_B4 = ChessBot("B4", transposition_table_select_move, eval_PST1)

bot_C1 = ChessBot("C1", minimax_select_move, eval_PST2)
bot_C2 = ChessBot("C2", mvv_lva_select_move, eval_PST2)
bot_C3 = ChessBot("C3", iterative_deepening_search, eval_PST2)
bot_C4 = ChessBot("C4", transposition_table_select_move, eval_PST2)

def get_move(bot_name, board, time_limit):
    bot_map = {
        "A1": bot_A1,
        "A2": bot_A2,
        "A3": bot_A3,
        "A4": bot_A4,
        "B1": bot_B1,
        "B2": bot_B2,
        "B3": bot_B3,
        "B4": bot_B4,
        "C1": bot_C1,
        "C2": bot_C2,
        "C3": bot_C3,
        "C4": bot_C4
    }
    bot = bot_map.get(bot_name)
    if not bot:
        raise ValueError(f"Unknown bot name: {bot_name}")
    return bot.select_move(board, time_limit)

# ----------------- Minimal UCI interface -----------------

def uci_loop():
    global board, DEPTH, TT, CHOSEN_BOT
    id_name = "KaarenBot"
    id_author = "Kaaren"

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
        except KeyboardInterrupt:
            break

        line = line.strip()
        if line == "":
            continue

        parts = line.split()
        cmd = parts[0]

        if cmd == "uci":
            print(f"id name {id_name}")
            print(f"id author {id_author}")
            """
            bot_options = " var ".join(["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4"])
            print(f"option name ChosenBot type combo default C3 var {bot_options}")
            """
            print("uciok")
            sys.stdout.flush()

        elif cmd == "isready":
            print("readyok")
            sys.stdout.flush()

        elif cmd == "ucinewgame":
            board = chess.Board()
            TT.clear() #Reset TT

        elif cmd == "position":
            if "startpos" in parts:
                board = chess.Board()
            elif "fen" in parts:
                fen_start = parts.index("fen") + 1
                # FEN strings end where "moves" begins, or at the end of the line
                fen_end = parts.index("moves") if "moves" in parts else len(parts)
                fen = " ".join(parts[fen_start:fen_end])
                board = chess.Board(fen)
            
            # Apply any moves sent by the GUI
            if "moves" in parts:
                moves_start = parts.index("moves") + 1
                for m in parts[moves_start:]:
                    try:
                        board.push_uci(m)
                    except Exception:
                        pass

        elif cmd == "go":
            time_limit = 1.0 # Default fallback
            
            try:
                if "movetime" in parts:
                    idx = parts.index("movetime")
                    time_limit = int(parts[idx+1]) / 1000.0
                else:
                    # Allocate roughly 1/30th of remaining time for this move
                    if board.turn == chess.WHITE and "wtime" in parts:
                        idx = parts.index("wtime")
                        time_limit = (int(parts[idx+1]) / 1000.0) / 30.0
                    elif board.turn == chess.BLACK and "btime" in parts:
                        idx = parts.index("btime")
                        time_limit = (int(parts[idx+1]) / 1000.0) / 30.0
            except (ValueError, IndexError):
                pass # Fallback to default if parsing fails

            time_limit = max(0.1, time_limit)

            try:
                best = get_move(CHOSEN_BOT, board, time_limit=time_limit)
                
                if best is None:
                    best = random.choice(list(board.legal_moves))
                
                print(f"bestmove {best.uci()}")
                sys.stdout.flush()

            except Exception as e:
                print(f"info string CRASH: {str(e)}")

                best = random.choice(list(board.legal_moves))
                print(f"bestmove {best.uci()}")
                sys.stdout.flush()

        elif cmd == "stop":
            pass

        elif cmd == "quit":
            break

        """
        elif cmd == "setoption":
            if "name ChosenBot" in line:
                try:
                    # Extract the value after the word 'value'
                    new_bot = line.split("value ")[1].strip()
                    global CHOSEN_BOT
                    CHOSEN_BOT = new_bot
                except IndexError:
                    pass
        """



if __name__ == "__main__":
    uci_loop()
