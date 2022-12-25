import sys

EMPTY_CHAR = '_'
AI_TURN = True
HU_TURN = False


class Bot:
    def __init__(self, hu_char, ai_char):
        self.hu_char = hu_char
        self.ai_char = ai_char
        self.scores = {
            hu_char: -10,
            ai_char: 10,
            'piece': 0
        }

    def computer_position(self, field):
        move = None
        best_score = -sys.maxsize
        board = [field[i].copy() for i in range(3)]
        for row in range(3):
            for col in range(3):
                if board[row][col] == EMPTY_CHAR:
                    board[row][col] = self.ai_char
                    score = self.minimax(board, 0, HU_TURN)
                    board[row][col] = EMPTY_CHAR
                    if score > best_score:
                        best_score = score
                        move = (row, col)
        return move

    def minimax(self, board, depth, is_ai_turn):
        if check_win(board, self.ai_char):
            return self.scores[self.ai_char]
        if check_win(board, self.hu_char):
            return self.scores[self.hu_char]
        if piece(board, self.hu_char, self.ai_char):
            return self.scores['piece']

        if is_ai_turn:
            # Выбираем ход, который выгоднее нам
            best_score = -sys.maxsize
            for row in range(3):
                for col in range(3):
                    if board[row][col] == EMPTY_CHAR:
                        board[row][col] = self.ai_char
                        score = self.minimax(board, depth + 1, HU_TURN)
                        board[row][col] = EMPTY_CHAR
                        best_score = max(best_score, score)
        else:
            best_score = sys.maxsize
            for row in range(3):
                for col in range(3):
                    if board[row][col] == EMPTY_CHAR:
                        board[row][col] = self.hu_char
                        score = self.minimax(board, depth + 1, AI_TURN)
                        board[row][col] = EMPTY_CHAR
                        best_score = min(best_score, score)
        return best_score


def check_win(field, player):
    win = False
    for row in field:
        if row.count(player) == 3:
            win = True
    for col in range(3):
        if field[0][col] == field[1][col] == field[2][col] == player:
            win = True
    if (field[0][0] == field[1][1] == field[2][2] == player) or (field[0][2] == field[1][1] == field[2][0] == player):
        win = True
    return win


def piece(board, hu_char, ai_char):
    if not check_win(board, ai_char):
        if not check_win(board, hu_char):
            if sum([i.count(EMPTY_CHAR) for i in board]) == 0:
                return True
    return False
