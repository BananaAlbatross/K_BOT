import chess
import time

PLAY = True
DEPTH = 5
MATE_SCORE = 100000
NEG_INF = -99999
POS_INF = 99999
board = chess.Board()
move_times = []

scores = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 30000
    }