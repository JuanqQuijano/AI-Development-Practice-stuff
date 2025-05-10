"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    if x_count == o_count:
        return X
    else:
        return O
#The player function should take a board state as input, and return which player’s turn 
#it is (either X or O).
#In the initial game state, X gets the first move. Subsequently, the player alternates with 
#each additional move.
#Any return value is acceptable if a terminal board is provided as input 
 #(i.e., the game is already over).

def actions(board):
     """
    Returns set of all possible actions (i, j) available on the board.
    """
     act = []
     for i in range(len(board)):
         for j in range (len(board[i])):
             if board[i][j] == EMPTY:
                 act.append((i,j))
     return act
    #Debe retornar una lista de tuples que tengan las coordenadas (i,j) del board cuyos espacios sean EMPTY


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    holder=[]
    if action not in actions(board):
        raise NameError('Not possible move')
    else:
        holder = copy.deepcopy(board)
        holder[action[0]][action[1]] = player(holder)
        return holder

    #Básicamente sería asignarle a las coordinadas dadas dentro del tuple resultante uno de los valores X u O, supongo que usando la función player?.
    #Supongo que sería un if de si es que dicha coordenada está dentro del tuple entonces se puede asignar uno de
    # los valores.
    #Debe retornarme un board sin cambiar el board original (usand deepcopy sería buena opción).

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # revisar las filas
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not EMPTY:
            return row[0]  #Nos dará la ficha que haya ganado

    # Revisar las columnas
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not EMPTY:
            return board[0][col]  #Nos dará la ficha que haya ganado (2)

    # Para revisar si alguien ganó por diagonales
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]  #Nos dará la ficha que haya ganado (2)
    if board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]  #Nos dará la ficha que haya ganado (2)
    
    return None  # Nos retornará nadota si no gana nadie
    

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if not any(EMPTY in row for row in board):
        return True
    elif winner(board) is not None:  # Check if winner is not None
        return True
    else:
        return False
    #If the game is over, either because someone has won the game or because all cells have been filled without anyone winning, the function should return True.
    #Otherwise, the function should return False if the game is still in progress.


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X: return 1
    elif winner(board) == O: return -1
    else: return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None  # retornará nada si es que se terminó la partida

    if player(board) == X:
        best_score = -999
        best_action = None
        for action in actions(board):
            score = min_value(result(board, action)) 
            if score > best_score:
                best_score = score
                best_action = action
        return best_action
    else:
        best_score = 999
        best_action = None
        for action in actions(board):
            score = max_value(result(board, action)) 
            if score < best_score:
                best_score = score
                best_action = action
        return best_action

def max_value(board):
    """
    Returns the maximum utility value for the maximizing player (X).
    """
    if terminal(board):
        return utility(board)
    v = -999
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    """
    Returns the minimum utility value for the minimizing player (O).
    """
    if terminal(board):
        return utility(board)
    v = 999
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

