import chess
import time

PLAY = True
board = chess.Board()
DEPTH = 5
move_times = []
MATE_SCORE = 100000
NEG_INF = -99999
POS_INF = 99999

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

    if board.is_checkmate():
        return -MATE_SCORE if board.turn == chess.WHITE else MATE_SCORE

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0
    
    if depth == 0:
        return evaluate(board)
    
    else:
        turn = board.turn

        if turn == chess.WHITE:
            best_eval = NEG_INF

            for move in list(board.legal_moves):
                board.push(move)
                best_eval = max(best_eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                alpha = max(alpha, best_eval)

                if beta <= alpha:
                    break

            return best_eval
        
        else:
            best_eval = POS_INF
            
            for move in list(board.legal_moves):
                board.push(move)
                best_eval = min(best_eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                beta = min(beta, best_eval)
                
                if beta <= alpha:
                    break
                
            return best_eval



while not board.is_game_over():
    turn = board.turn
    best_move = None
    highest_value = NEG_INF if turn else POS_INF
    alpha = NEG_INF
    beta = POS_INF

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
        else:
            if value < highest_value:
                highest_value = value
                best_move = i

    """
    end_time = time.perf_counter()
    move_time = end_time - start_time
    move_times.append(move_time)
    """
    board.push(best_move)
    print(board)
    print()
