import chess
import random
import time

play = True
board = chess.Board()
move_times = []

if play:
    while not board.is_game_over():
        start_time = time.perf_counter()
        move = random.choice(list(board.legal_moves))
        end_time = time.perf_counter()
        move_time = end_time - start_time
        move_times.append(move_time)
        board.push(move)
        print(board)
        print()

    print("GG " + board.result())

print("Average move time: " + str(round(sum(move_times)/len(move_times), 5)) + " s")
 