import chess
import time

PLAY = True
DEPTH = 5
MATE_SCORE = 100000
NEG_INF = -99999
POS_INF = 99999
board = chess.Board()
move_times = []
