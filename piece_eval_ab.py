import chess
import time

PLAY = True
board = chess.Board()
DEPTH = 5
move_times = []

scores = {
    # AlphaZero (2020) piece values
        chess.PAWN: 100,
        chess.KNIGHT: 305,
        chess.BISHOP: 333,
        chess.ROOK: 563,
        chess.QUEEN: 950,
        chess.KING: 30000
    }

def evaluate(board):
    score = 0
    
    # Count pieces and increment score
    for i in scores:
        score += scores[i] * len(board.pieces(i, True)) # True is white
        score -= scores[i] * len(board.pieces(i, False)) # False is black
    return score




def minimax(board, depth, alpha, beta):

    if depth == 0 or board.is_game_over():
        return evaluate(board)
    
    else:
        turn = board.turn

        if turn == chess.WHITE:
            eval = -99999
            for move in list(board.legal_moves):
                board.push(move)
                eval = max(eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                alpha = max(alpha, eval)

                if beta <= alpha:
                    break
            return eval
        
        else:
            eval = 99999
            for move in list(board.legal_moves):
                board.push(move)
                eval = min(eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                beta = min(beta, eval)
                
                if beta <= alpha:
                    break
            return eval



while not board.is_game_over():
    turn = board.turn
    best_move = None
    highest_value = -63000 if turn else 63000
    alpha = -63000
    beta = 63000

    legal_moves = list(board.legal_moves)

    #start_time = time.perf_counter()
    for i in legal_moves:
        board.push(i)
        #value = evaluate(board)     depth-1's evaluate() got switched out for minimax()
        value = minimax(board, DEPTH-1, alpha, beta)
        board.pop()
        if turn:
            if value > highest_value:
                highest_value = value
                best_move = i
            alpha = max(alpha, value)
        else:
            if value < highest_value:
                highest_value = value
                best_move = i
            beta = min(beta, value)
    """
    end_time = time.perf_counter()
    move_time = end_time - start_time
    move_times.append(move_time)
    """
    board.push(best_move)
    print(board)
    print()
