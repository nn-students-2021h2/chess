from chess.structs import ChessPosition


class Piece:
    BLACK = "black"
    WHITE = "white"

    def __init__(self, position: ChessPosition, color: str):
        self._position = position
        self._color = color

    @property
    def position(self):
        return self._position

    @property
    def color(self):
        return self._color

    def move(self, target_position):
        self._position = target_position

    def get_threatened_positions(self, board: 'ChessBoard'):
        raise NotImplementedError

    def get_moveable_positions(self, board: 'ChessBoard'):
        raise NotImplementedError

    def symbol(self):
        black_color_prefix = '\u001b[31;1m'
        white_color_prefix = '\u001b[34;1m'
        color_suffix = '\u001b[0m'
        retval = self._symbol_impl()
        if self.color == Piece.BLACK:
            retval = black_color_prefix + retval + color_suffix
        else:
            retval = white_color_prefix + retval + color_suffix
        return retval

    def _symbol_impl(self):
        raise NotImplementedError


class PieceType:
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"
    PAWN = "pawn"


class Rook(Piece):
    BEAM_INCREMENTS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    def get_threatened_positions(self, board: 'ChessBoard'):
        positions = []
        for increment in Rook.BEAM_INCREMENTS:
            positions += board.beam_search_threat(self._position, self._color, increment[0], increment[1])
        return positions

    def get_moveable_positions(self, board: 'ChessBoard'):
        return self.get_threatened_positions(board)

    def _symbol_impl(self):
        return 'r'


class Knight(Piece):
    SPOT_INCREMENTS = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    def get_threatened_positions(self, board: 'ChessBoard'):
        positions = []
        for increment in Knight.SPOT_INCREMENTS:
            positions.append(board.spot_search_threat(self._position, self._color, increment[0], increment[1]))
        positions = [x for x in positions if x is not None]
        return positions

    def get_moveable_positions(self, board: 'ChessBoard'):
        return self.get_threatened_positions(board)

    def _symbol_impl(self):
        return 'k'

class Bishop(Piece):
    BEAM_INCREMENTS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    def get_threatened_positions(self, board: 'ChessBoard'):
        positions = []
        for increment in Bishop.BEAM_INCREMENTS:
            positions += board.beam_search_threat(self._position, self._color, increment[0], increment[1])
        return positions

    def get_moveable_positions(self, board: 'ChessBoard'):
        return self.get_threatened_positions(board)

    def _symbol_impl(self):
        return 'B'

class Queen(Piece):
    def get_threatened_positions(self, board: 'ChessBoard'):
        positions = []
        for increment in (Bishop.BEAM_INCREMENTS + Rook.BEAM_INCREMENTS):
            positions += board.beam_search_threat(self._position, self._color, increment[0], increment[1])
        return positions

    def get_moveable_positions(self, board: 'ChessBoard'):
        return self.get_threatened_positions(board)

    def _symbol_impl(self):
        return 'Q'


class King(Piece):
    SPOT_INCREMENTS = [(1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1)]
    def __init__(self, position: ChessPosition, color: str):
        super().__init__(position, color)
        self._board_handle = None

    def set_board_handle(self, board: 'ChessGame'):
        self._board_handle = board
        self._board_handle.register_king_position(self.position, self.color)

    def move(self, target_position: ChessPosition):
        Piece.move(self, target_position)
        self._board_handle.register_king_position(target_position, self.color)

    def get_threatened_positions(self, board: 'ChessBoard'):
        positions = []
        for increment in King.SPOT_INCREMENTS:
            positions.append(board.spot_search_threat(self._position, self._color, increment[0], increment[1]))
        positions = [x for x in positions if x is not None]
        return positions

    def get_moveable_positions(self, board: 'ChessBoard'):
        return self.get_threatened_positions(board)

    def _symbol_impl(self):
        return 'K'

class Pawn(Piece):
    SPOT_INCREMENTS_MOVE = [(0, 1)]
    SPOT_INCREMENTS_MOVE_FIRST = [(0, 1), (0, 2)]
    SPOT_INCREMENTS_TAKE = [(-1, 1), (1, 1)]
    def __init__(self, position: ChessPosition, color: str):
        super().__init__(position, color)
        self._moved = False

    def get_threatened_positions(self, board: 'ChessBoard'):
        positions = []
        increments = Pawn.SPOT_INCREMENTS_TAKE
        for increment in increments:
            positions.append(board.spot_search_threat(self._position, self._color, increment[0],
                                                      increment[1] if self.color == Piece.WHITE else (-1) * increment[1]))
        positions = [x for x in positions if x is not None]
        return positions

    def get_moveable_positions(self, board: 'ChessBoard'):
        positions = []
        increments = Pawn.SPOT_INCREMENTS_MOVE if self._moved else Pawn.SPOT_INCREMENTS_MOVE_FIRST
        for increment in increments:
            positions.append(board.spot_search_threat(self._position, self._color, increment[0],
                                                      increment[1] if self.color == Piece.WHITE else (-1) * increment[1], free_only=True))

        increments = Pawn.SPOT_INCREMENTS_TAKE
        for increment in increments:
            positions.append(board.spot_search_threat(self._position, self._color, increment[0],
                                                      increment[1] if self.color == Piece.WHITE else (-1) * increment[1], threat_only=True))

        positions = [x for x in positions if x is not None]
        return positions

    def move(self, target_position):
        self._moved = True
        Piece.move(self, target_position)

    def _symbol_impl(self):
        return 'p'

class PieceFactory:
    @staticmethod
    def create(piece_type: str, position: ChessPosition, color):
        if piece_type == PieceType.ROOK:
            return Rook(position, color)
        if piece_type == PieceType.KNIGHT:
            return Knight(position, color)
        if piece_type == PieceType.BISHOP:
            return Bishop(position, color)
        if piece_type == PieceType.KING:
            return King(position, color)
        if piece_type == PieceType.QUEEN:
            return Queen(position, color)
        if piece_type == PieceType.PAWN:
            return Pawn(position, color)
