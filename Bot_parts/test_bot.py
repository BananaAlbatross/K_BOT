from base import *
from eval_pieces_standard import *
from minimax_ab import *



while not board.is_game_over():
    turn = board.turn
    highest_value = NEG_INF if turn else POS_INF
    best_move = None
    alpha = NEG_INF
    beta = POS_INF

    legal_moves = list(board.legal_moves)

    #start_time = time.perf_counter()
    for i in legal_moves:
        board.push(i)

        value = minimax(board, DEPTH-1, alpha, beta)
        board.pop()

        if turn:
            if value > highest_value:
                highest_value = value
                best_move = i
        else:
            if value < highest_value:
                highest_value = value
                best_move = i

        board.push(best_move)
        print(board)
        print()

    print("GG " + board.result())
