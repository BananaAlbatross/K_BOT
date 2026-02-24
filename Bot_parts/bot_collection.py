import chess
import time
import itertools

# ------------- Definitions / Constants -------------

PLAY = True
DEPTH = 5
MATE_SCORE = 100000
NEG_INF = -99999
POS_INF = 99999
board = chess.Board()
move_times = []
TT = {}

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
    return int(round(score))

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
    mg_phase = max(0, min(1, phase/24))
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

    return int(round(score))


# ------------- Search functions -------------


def quiescence(board, alpha, beta, evaluator, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()
    stand_pat = evaluator(board)
    if board.turn == chess.WHITE:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat
    for move in board.legal_moves:
        if board.is_capture(move):
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

def default_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0
    if depth == 0 or board.is_game_over():
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
    time_limit -= 0.05 #buffer
    
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
                val = default_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
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

#--------------------------------------------------------

def iterative_deepening_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    #Check time every position
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
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

def iterative_deepening_fixed_depth_search(board, depth, evaluator, start_time, time_limit):
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
            val = iterative_deepening_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
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

def iterative_deepening_search(board, depth, evaluator, time_limit):
    start_time = time.time()
    time_limit -= 0.05 #buffer
    best_move_found = None
    
    #Iterative deepening
    try:
        for d in range(1, depth + 1):
            result = iterative_deepening_fixed_depth_search(board, d, evaluator, start_time, time_limit)
            if result:
                best_move_found = result
    except SearchTimeout:
        pass
    
    #Best found or random
    return best_move_found or next(iter(board.legal_moves))

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
            # Standard MVV-LVA formula: (10 * victim) - attacker
            return 1000 * MOVE_ORDERING_SCORES.get(victim.piece_type, 0) - MOVE_ORDERING_SCORES.get(attacker.piece_type, 0)
        return 1000
    
    return 0

def mvv_lva_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
    # Time check
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
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
    time_limit -= 0.05 #buffer
    
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
                val = mvv_lva_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
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

#--------------------------------------------------------

def tt_lookup(board, depth):
    key = board.zobrist_key()
    entry = TT.get(key)
    if not entry:
        return None
    stored_depth, score = entry
    
    if stored_depth >= depth:
        return score
    return None

def tt_store(board, depth, score):
    key = board.zobrist_key()
    TT[key] = (depth, score)

def transposition_table_minimax(board, depth, alpha, beta, evaluator, start_time, time_limit):
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
        val = quiescence(board, alpha, beta, evaluator, start_time, time_limit)
        tt_store(board, depth, val)
        return val

    #Search
    if board.turn == chess.WHITE:
        value = NEG_INF
        for move in board.legal_moves:
            board.push(move)
            try:
                res = transposition_table_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
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
                res = transposition_table_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
                value = min(value, res)
            finally:
                board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
    
    #TT store
    tt_store(board, depth, value)
    return value

def transposition_table_select_move(board, depth, evaluator, time_limit):
    start_time = time.time()
    time_limit -= 0.05 #buffer
    
    best_move = None
    turn = board.turn
    alpha = NEG_INF
    beta = POS_INF
    best_value = NEG_INF if turn else POS_INF

    try:
        for move in board.legal_moves:
            board.push(move)
            try:
                val = transposition_table_minimax(board, depth - 1, alpha, beta, evaluator, start_time, time_limit)
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


#-------------------------- ChessBot Class ------------------------------


class ChessBot:
    def __init__(self, name, search_func, eval_func, depth=DEPTH):
        self.name = name
        self.search = search_func
        self.evaluate = eval_func
        self.depth = depth

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

bots = [bot_A1, bot_A2, bot_A3, bot_A4, bot_B1, bot_B2, bot_B3, bot_B4, bot_C1, bot_C2, bot_C3, bot_C4]

class Tournament:
    def __init__(self, bots, k_factor=32):
        self.bots = bots
        self.ratings = {bot.name: 1200 for bot in bots}  # Start all at 1200
        self.k_factor = k_factor
        self.results = {bot.name: {"wins": 0, "losses": 0, "draws": 0} for bot in bots}

    def get_expected_score(self, rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_ratings(self, white_name, black_name, result):
        
        r_white = self.ratings[white_name]
        r_black = self.ratings[black_name]

        #Predicted
        exp_white = self.get_expected_score(r_white, r_black)
        exp_black = 1 - exp_white

        #Result: 1.0 for White win, 0.5 for draw, 0.0 for Black win
        score_white = result
        score_black = 1.0 - result

        # Update Elo
        self.ratings[white_name] += self.k_factor * (score_white - exp_white)
        self.ratings[black_name] += self.k_factor * (score_black - exp_black)

    def play_game(self, bot_white, bot_black, time_limit=1.0):
        board = chess.Board()
        # Clear Transposition Table
        TT.clear() 
        
        while not board.is_game_over():
            current_bot = bot_white if board.turn == chess.WHITE else bot_black
            move = current_bot.select_move(board, time_limit)
            board.push(move)
            
        # Determine result
        outcome = board.outcome().winner
        if outcome == chess.WHITE:
            return 1.0
        elif outcome == chess.BLACK:
            return 0.0
        else:
            return 0.5

    def run_round_robin(self, rounds=1):
        # All matchups
        pairings = list(itertools.permutations(self.bots, 2))
        
        for r in range(rounds):
            print(f"--- Starting Round {r+1} ---")
            for white_bot, black_bot in pairings:
                print(f"{white_bot.name} (W) vs {black_bot.name} (B)...", end=" ", flush=True)
                
                res = self.play_game(white_bot, black_bot)
                self.update_ratings(white_bot.name, black_bot.name, res)
                
                # Update stats
                if res == 1.0:
                    self.results[white_bot.name]["wins"] += 1
                    self.results[black_bot.name]["losses"] += 1
                elif res == 0.0:
                    self.results[black_bot.name]["wins"] += 1
                    self.results[white_bot.name]["losses"] += 1
                else:
                    self.results[white_bot.name]["draws"] += 1
                    self.results[black_bot.name]["draws"] += 1
                
                print(f"Result: {res}")

    def display_leaderboard(self):
        sorted_bots = sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)
        print("Leaderboard:")
        print(f"{'Bot Name':<20} | {'Rating':<8} | {'W-L-D'}")
        print("-" * 45)
        for name, rating in sorted_bots:
            res = self.results[name]
            stats = f"{res['wins']}-{res['losses']}-{res['draws']}"
            print(f"{name:<20} | {round(rating):<8} | {stats}")