from base import *
from eval_pieces_standard import *

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

            for move in board.legal_moves:
                board.push(move)
                best_eval = max(best_eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                alpha = max(alpha, best_eval)

                if beta <= alpha:
                    break
                
            return best_eval
        
        else:
            best_eval = POS_INF

            for move in board.legal_moves:
                board.push(move)
                best_eval = min(best_eval, minimax(board, depth-1, alpha, beta))
                board.pop()
                beta = min(beta, best_eval)
                
                if beta <= alpha:
                    break

            return best_eval
