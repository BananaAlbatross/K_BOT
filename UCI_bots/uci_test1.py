import sys
import chess
import random
import time

PLAY = True
board = chess.Board()
DEPTH = 5
move_times = []
DELTA = 10
MATE_SCORE = 100000
TRUE_RANDOM = False
NEG_INF = -99999
POS_INF = 99999

if not TRUE_RANDOM:
    random.seed(12345)

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

PHASE_SCORES = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4,
    chess.KING: 0
} # Max phase is 8*0 + 4*1 + 4*1 + 4*2 + 2*4 + 2*0 = 24 (with promotion exceptions)

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



# Prioritiseerib promotion'eid ja capture'id käigujärjestusel
def mvv_lva_score(board, move):
    if move.promotion:
        return 10000 + 100 * MOVE_ORDERING_SCORES.get(move.promotion)
    
    if board.is_en_passant(move):
        return 8000
    
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            return 1000 * MOVE_ORDERING_SCORES.get(victim.piece_type) - MOVE_ORDERING_SCORES.get(attacker.piece_type)
        else:
            return 1000
    
    return 0

def evaluate(board):
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
    phase = max(0, min(1, phase/24))

    # Piece-Square Table
    for i in SCORES:
        # White pieces
        for square in board.pieces(i, True):
            score += (PST_MG[i][square] * phase + PST_EG[i][square] * (1-phase))
        # Black pieces
        for square in board.pieces(i, False):
            score -= (PST_MG[i][chess.square_mirror(square)] * phase + PST_EG[i][chess.square_mirror(square)] * (1-phase))

    return int(round(score))



def minimax(board, depth, alpha, beta):

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE
    
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0
    
    if depth == 0 or board.is_game_over():
        return evaluate(board)
    
    else:
        turn = board.turn

        # Ennustame paremaid käike
        moves = list(board.legal_moves)
        moves.sort(key=lambda move: mvv_lva_score(board, move), reverse=True)

        if turn == chess.WHITE:
            best_eval = NEG_INF
            
            for move in moves:
                board.push(move)
                best_eval = max(best_eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                alpha = max(alpha, best_eval)

                if beta <= alpha:
                    break

            return best_eval
        
        else:
            best_eval = POS_INF

            for move in moves:
                board.push(move)
                best_eval = min(best_eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                beta = min(beta, best_eval)
                
                if beta <= alpha:
                    break

            return best_eval
        
def get_best_move(cur_board, depth=DEPTH):

    turn = cur_board.turn
    move_values = []
    
    for i in cur_board.legal_moves:
        cur_board.push(i)
        val = minimax(cur_board, depth-1, NEG_INF, POS_INF)
        cur_board.pop()
        move_values.append((i, val))

        if turn:
            # Potential moves for white (to turn)
            highest_value = max(move_values, key=lambda x: x[1])[1]
            potential_moves = [move for (move, value) in move_values if value >= highest_value - DELTA]
        else:
            # Potential moves for black (to turn)
            highest_value = min(move_values, key=lambda x: x[1])[1]
            potential_moves = [move for (move, value) in move_values if value <= highest_value + DELTA]

    if not potential_moves:
        if turn:
            return(max(move_values, key=lambda x: x[1])[0])
        else:
            return(min(move_values, key=lambda x: x[1])[0])
    else: 
        return(random.choice(potential_moves))

# ----------------- Minimal UCI interface -----------------
def uci_loop():
    global board, DEPTH
    id_name = "MyPythonBot"
    id_author = "You"

    print(f"id name {id_name}")
    print(f"id author {id_author}")
    print("uciok")
    sys.stdout.flush()

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

        if cmd == "isready":
            print("readyok")
            sys.stdout.flush()

        elif cmd == "ucinewgame":
            board = chess.Board()

        elif cmd == "position":
            # Syntax: position startpos [moves ...]  OR  position fen <fenstring> [moves ...]
            if parts[1] == "startpos":
                board = chess.Board()
                moves_start = 2
            elif parts[1] == "fen":
                # fen = parts[2] ... parts[7] (6 fields after 'fen')
                fen = " ".join(parts[2:8])
                board = chess.Board(fen)
                moves_start = 8
            else:
                continue

            # apply moves if any
            if len(parts) > moves_start:
                move_list = parts[moves_start + 1:] if parts[moves_start] == "moves" else parts[moves_start:]
                # handle "moves" token optionally
                for m in move_list:
                    try:
                        board.push_uci(m)
                    except Exception:
                        pass

        elif cmd == "go":
            movetime = None
            if "movetime" in parts:
                idx = parts.index("movetime")
                try:
                    movetime = int(parts[idx+1])
                except:
                    movetime = None

            # If movetime provided, we could modify depth heuristically. For now, just use DEPTH.
            # You can implement iterative deepening + timeout later.
            start = time.time()
            best = get_best_move(board, DEPTH)
            # When you implement iterative deepening you should respect "movetime"
            end = time.time()
            if best is None:
                best = random.choice(list(board.legal_moves))
            print(f"bestmove {best.uci()}")
            sys.stdout.flush()

        elif cmd == "stop":
            # we do no pondering and no background search in this simple engine
            pass

        elif cmd == "quit":
            break

        # optional: support "setoption name X value Y" if you want tunable options
    # end loop

if __name__ == "__main__":
    uci_loop()
