import chess as ch
import random as rd

class Engine:

    def __init__(self, board, maxDepth, color):
        self.board=board
        self.color=color
        self.maxDepth=maxDepth
        self.transposition_table = {}
    
    
    def getBestMove(self):
        if self.board.turn == self.color:
            _, best_move = self.engine(float('-inf'), float('inf'), 1, False)
        else:
            _, best_move = self.engine(float('-inf'), float('inf'), 1)
        return best_move
    
    #Calculates total material score
    def calculateMaterialScore(self):
        material_score = 0
        for piece_type in [ch.PAWN, ch.KNIGHT, ch.BISHOP, ch.ROOK, ch.QUEEN]:
            count = len(self.board.pieces(piece_type, self.color))
            material_score += count * self.getPieceValue(piece_type)
        return material_score

    #Returns value of each piece
    def getPieceValue(self, piece_type):
        if piece_type == ch.PAWN:
            return 1
        elif piece_type == ch.KNIGHT:
            return 3
        elif piece_type == ch.BISHOP:
            return 3.2
        elif piece_type == ch.ROOK:
            return 5.1
        elif piece_type == ch.QUEEN:
            return 8.8
        else:
            return 0
        
    #Gets value of piece being on given square    
    def getPieceSquareValue(self, piece_type, square):
        piece_square_table = {
            ch.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 5, 5, 5, 5, 5, 5, 5,
                1, 1, 2, 3, 3, 2, 1, 1,
                0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5,
                0, 0, 0, 2, 2, 0, 0, 0,
                0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5,
                0.5, 1, 1, -2, -2, 1, 1, 0.5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            ch.KNIGHT: [
                -5, -4, -3, -3, -3, -3, -4, -5,
                -4, -2, 0, 0, 0, 0, -2, -4,
                -3, 0, 1, 1.5, 1.5, 1, 0, -3,
                -3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3,
                -3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3,
                -3, 0, 1, 1.5, 1.5, 1, 0, -3,
                -4, -2, 0, 0.5, 0.5, 0, -2, -4,
                -5, -4, -3, -3, -3, -3, -4, -5
            ],
            ch.BISHOP: [
                -2, -1, -1, -1, -1, -1, -1, -2,
                -1, 0, 0, 0, 0, 0, 0, -1,
                -1, 0, 0.5, 1, 1, 0.5, 0, -1,
                -1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1,
                -1, 0, 1, 1, 1, 1, 0, -1,
                -1, 1, 1, 1, 1, 1, 1, -1,
                -1, 0.5, 0, 0, 0, 0, 0.5, -1,
                -2, -1, -1, -1, -1, -1, -1, -2
            ],
            ch.ROOK: [
                0, 0, 0, 0, 0, 0, 0, 0,
                0.5, 1, 1, 1, 1, 1, 1, 0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                -0.5, 0, 0, 0, 0, 0, 0, -0.5,
                0, 0, 0, 0.5, 0.5, 0, 0, 0
            ],
            ch.QUEEN: [
                -2, -1, -1, -0.5, -0.5, -1, -1, -2,
                -1, 0, 0, 0, 0, 0, 0, -1,
                -1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1,
                -0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
                0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
                -1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1,
                -1, 0, 0.5, 0, 0, 0, 0, -1,
                -2, -1, -1, -0.5, -0.5, -1, -1, -2
            ]
        }

        if piece_type in piece_square_table:
            if self.color == ch.WHITE:
                return piece_square_table[piece_type][square]
            else:
                return piece_square_table[piece_type][ch.square_mirror(square)]
        else:
            return 0

    #Calculates positional score    
    def calculatePositionalScore(self):
        positional_score = 0
        for square, piece in self.board.piece_map().items():
            if piece.color == self.color:
                piece_value = self.getPieceValue(piece.piece_type)
                positional_score += piece_value + self.getPieceSquareValue(piece.piece_type, square)
            else:
                piece_value = self.getPieceValue(piece.piece_type)
                positional_score -= piece_value + self.getPieceSquareValue(piece.piece_type, square)
        return positional_score
    
    #Calculates the safety of the king
    def calculateKingSafetyScore(self):
        king_safety_score = 0

        # Check if the king is under attack
        if self.board.is_check():
            king_safety_score -= 5

        return king_safety_score

    #Calculates how good pawn structure is
    def calculatePawnStructureScore(self):
        pawn_structure_score = 0
        pawns = self.board.pieces(ch.PAWN, self.color)
        for pawn in pawns:
            if not self.isIsolatedPawn(pawn):
                pawn_structure_score -= 10
        return pawn_structure_score
    
    #Checks if a pawn is isolated
    def isIsolatedPawn(self, square):
        file = square % 8
        adjacent_files = [file - 1, file + 1]
        for adj_file in adjacent_files:
            if 0 <= adj_file <= 7 and self.board.piece_at(adj_file + square // 8 * 8) == ch.PAWN:
                return False
        return True

    #Evaluation Function to calculate how good a position is.
    #Combines and weighs material, positional, king safety, and pawn structure score
    def evalFunct(self):
        material_score = self.calculateMaterialScore()
        positional_score = self.calculatePositionalScore()
        king_safety_score = self.calculateKingSafetyScore()
        pawn_structure_score = self.calculatePawnStructureScore()

        total_score = material_score + positional_score*0.8 + king_safety_score*0.5 + pawn_structure_score*0.3

        return total_score
        
    #Checks if there is a mating opurtunity for either player
    def mateOpportunity(self):
        if (self.board.legal_moves.count()==0):
            if (self.board.turn == self.color):
                return -999
            else:
                return 999
        else:
            return 0

    #Opening function to make the first 10 moves easier
    def opening(self):
        if self.board.fullmove_number < 10:
            if self.board.turn == self.color:
                move_count = self.board.legal_moves.count()

                # Prioritize moves that develop the pieces
                piece_moves = [move for move in self.board.legal_moves if self.board.piece_type_at(move.from_square) != ch.PAWN]
                if piece_moves:
                    return 1/30 * len(piece_moves) / move_count

                # Prioritize moves that control the center
                center_squares = [ch.E4, ch.D4, ch.E5, ch.D5]
                center_moves = [move for move in self.board.legal_moves if move.to_square in center_squares]
                if center_moves:
                    return 1/30 * len(center_moves) / move_count

                # Prioritize castling early
                castling_moves = [move for move in self.board.legal_moves if self.board.is_castling(move)]
                if castling_moves:
                    return 1/30 * len(castling_moves) / move_count

            else:
                return -1/30 * self.board.legal_moves.count()

        return 0


    
    def squareResPoints(self, square):
        pieceValue = 0
        if(self.board.piece_type_at(square) == ch.PAWN):
            pieceValue = 1
        elif (self.board.piece_type_at(square) == ch.ROOK):
            pieceValue = 5.1
        elif (self.board.piece_type_at(square) == ch.BISHOP):
            pieceValue = 3.33
        elif (self.board.piece_type_at(square) == ch.KNIGHT):
            pieceValue = 3.2
        elif (self.board.piece_type_at(square) == ch.QUEEN):
            pieceValue = 8.8

        if (self.board.color_at(square)!=self.color):
            return -pieceValue
        else:
            return pieceValue


    def move_heuristic(self, move):
        captured_piece_value = 0
        if self.board.is_capture(move):
            captured_piece_value = self.squareResPoints(move.to_square)
        return captured_piece_value
        
        
        
    def engine(self, alpha, beta, depth, is_human_turn=True):
        key = self.board.board_fen()
        if key in self.transposition_table:
            return self.transposition_table[key]

        if depth == self.maxDepth or self.board.is_game_over():
            return self.evalFunct(), None

        best_move = None
        
        moves = list(self.board.legal_moves)
        moves.sort(key=lambda move: self.move_heuristic(move), reverse=is_human_turn)


        if is_human_turn:
            best_value = float('inf')
            for move in moves:
                self.board.push(move)
                value, _ = self.engine(alpha, beta, depth + 1, not is_human_turn)
                self.board.pop()
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)
                if beta <= alpha:
                    break
        else:
            best_value = float('-inf')
            for move in moves:
                self.board.push(move)
                value, _ = self.engine(alpha, beta, depth + 1, not is_human_turn)
                self.board.pop()
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)
                if beta <= alpha:
                    break

        self.transposition_table[key] = (best_value, best_move)

        if depth == 1:
            return best_value, best_move
        else:
            return best_value, None
