# Name: Alex Henner
# Date: 11/12/21
# Description: This program implements the Hasmi Shogi Game Variant 1.

from typing import List, Dict, Callable, Union, Tuple, Any
import sys, time, random, pygame as pg
from pygame import Surface

WIDTH, HEIGHT = 750, 820
GAP = (WIDTH - 40) // 9
WOOD_TILE = pg.transform.scale(pg.image.load('Images/wood_tile.png'), (GAP, GAP))
BLACK_PIECE = pg.transform.scale(pg.image.load('Images/Shogi_black.png'), (GAP - 10, GAP - 10))
RED_PIECE = pg.transform.scale(pg.image.load('Images/Shogi_red.png'), (GAP - 10, GAP - 10))


class HasamiShogiGame:
    """Hasami Shogi Game Variant 1 implementation has a Board object, which has Square objects"""
    def __init__(self, win: Union["Surface", "SurfaceType"]):
        """Initializes game state, active player, list of ranks, and initializes the board object"""
        self._game_states: List[str] = ["UNFINISHED", "RED_WON", "BLACK_WON"]
        self._game_state: str = self._game_states[0]

        self._active_players: List[str] = ["BLACK", "RED"]
        self._active_player: str = self._active_players[0]

        self._rank: str = "abcdefghi"
        self._initiate_move = True
        self._board: Board = Board(win)

    def get_location(self, mouse: tuple[int, int]) -> str:
        """returns the str of the location of the mouse click"""
        # grabbing the row and col the mouse was on when clicked.
        row = (mouse[1] - self._board.get_buffer() - self._board.get_top_gap()) // self._board.get_gap()
        col = (mouse[0] - self._board.get_buffer()) // self._board.get_gap()
        rank = self._rank[row]
        file = str(9 - col)
        return rank + file

    def get_initiate_move(self) -> bool:
        """returns if it is the first time a player has clicked a square"""
        return self._initiate_move

    def set_initiate_move(self, init_bool: bool) -> None:
        """sets initiate move"""
        self._initiate_move = init_bool

    def get_game_state(self) -> str:
        """returns current state of the game"""
        return self._game_state

    def get_active_player(self) -> str:
        """returns active player (whose turn it is)"""
        return self._active_player

    def get_num_captured_pieces(self, player: str) -> int:
        """Counts the captured pieces of the given player"""
        return 9 - self._board.count_pieces()[player]

    def make_move(self, from_location: str, to_location: str) -> bool:
        """
        Makes sure that the combination of from to to location is possible,
        Checks if it the right players turn,
        Checks if the game is still being played,
        Calls Board to check if the move is legal and if it is then call method to capture pieces if possible,
        and call method to update game
        """
        # Player doesn't move piece anywhere
        if from_location == to_location:
            return False

        # Player input too many letters or numbers
        if len(from_location) != 2 or len(to_location) != 2:
            return False

        # if it isn't in rank file notation (a2, i7, etc)
        if not from_location[0].isalpha() or not to_location[0].isalpha() \
                or not from_location[1].isnumeric() or not to_location[1].isnumeric():
            return False

        # update from location's rank and file to usable indices
        from_rank = self._rank.find(from_location[0])
        from_file = 9 - int(from_location[1])

        # if rank doesn't exist (greater than i) or if user used file of 0
        if from_rank == -1 or from_file == 9:
            return False

        # Check if current player is moving their piece and the game isn't over yet
        if self._board.occupant(from_rank, from_file).get_piece() != self._active_player \
                or self._game_state != self._game_states[0]:
            return False

        # update to location's rank and file to usable indices
        to_rank = self._rank.find(to_location[0])
        to_file = 9 - int(to_location[1])

        # if rank doesn't exist (greater than i) or if user used file of 0
        if to_rank == -1 or to_file == 9:
            return False

        # If the move is possible, make it and check for captured pieces and update the game
        if self._board.move(from_rank, from_file, to_rank, to_file):
            self._board.capture_pieces(self._board.occupant(to_rank, to_file))
            self._update_game()
            return True

        return False

    def ai_make_move(self, from_location: 'Square', to_location: 'Square') -> None:
        """allows the ai to make a move in the game"""
        self._board.ai_move(from_location, to_location)
        # location is given from 1-9, so need to subtract 1 for preprocessing
        self._board.capture_pieces(self._board.occupant(*[location - 1 for location in to_location.get_location()]))
        self._update_game()

    def _update_game(self) -> None:
        """Checks for a winner of the game and changes whose turn it is"""
        # change whose turn it is
        opponent = self._active_players[(self._active_players.index(self._active_player) + 1) % 2]
        # determining winner
        if self.get_num_captured_pieces(opponent) >= 8:
            if self._active_player == self._active_players[0]:
                self._game_state = self._game_states[2]
            else:
                self._game_state = self._game_states[1]
        elif self.get_num_captured_pieces(self._active_player) >= 8:
            if opponent == self._active_players[0]:
                self._game_state = self._game_states[2]
            else:
                self._game_state = self._game_states[1]

        # set whose turn it is
        self._active_player = opponent

    def get_square_occupant(self, position: str) -> str:
        """Returns the piece that is located at the position entered"""
        rank = self._rank.find(position[0])         # look through the ranks and change letter to int position
        file = 9 - int(position[1])                 # board is flipped horizontally
        return self._board.occupant(rank, file).get_piece()

    def get_board(self) -> 'Board':
        """Returns the board object"""
        return self._board


class Board:
    """Creates a board object that is 9x9 Square objects"""
    def __init__(self,
                 win: Union["Surface", "SurfaceType"],
                 board: str = 'RRRRRRRRR/9/9/9/9/9/9/9/BBBBBBBBB'):
        """initializes the board as nested lists and calls method to create the board"""
        self._board: List[List[Square]] = []
        self._rows = 9
        self._cols = 9
        self._buffer = 20
        self._top_gap = win.get_height() - win.get_width() + self._buffer       # Helping to make a square after gap
        self._width = win.get_width() - self._buffer
        self._height = win.get_height() - self._top_gap
        self._gap = (self._width - 2 * self._buffer) // self._cols
        self.create_board()
        self.set_board(board)

    def get_board(self):
        """returns board"""
        return self._board

    def get_buffer(self):
        """returns buffer"""
        return self._buffer

    def get_gap(self):
        """returns gap (length of square space)"""
        return self._gap

    def get_top_gap(self):
        """Returns the height of gap at top of screen"""
        return self._top_gap

    @staticmethod
    def convert_location(location: str) -> tuple[int, int]:
        """converts from string location to int"""
        ranks = "abcdefghi"
        rank = ranks.find(location[0])
        file = 9 - int(location[1])
        return rank, file

    def deselect_square(self, location: str) -> None:
        """deselects the square"""
        rank, file = self.convert_location(location)
        self.occupant(rank, file).set_selected(False)

    def select_square(self, location: str) -> None:
        """selects the square"""
        rank, file = self.convert_location(location)
        self.occupant(rank, file).set_selected(True)

    def refresh_possible(self):
        """changes all is possible values back to false"""
        for rank in self._board:
            for square in rank:
                square.set_is_possible(False)

    def get_player_locations(self, player: str) -> List['Square']:
        """Gets red locations for the AI"""
        pieces = []
        for row in self._board:
            for el in row:
                if el.get_piece() == player:
                    pieces.append(el)
        return pieces

    def create_board(self) -> None:
        """Creates the board by creating 9x9 Square objects and connects them all. It also places the initial pieces"""

        # iterate over all Squares and connect them to top and left squares and assign starting position values
        for rank in range(1, 10):
            self._board.append([])
            for file in range(1, 10):
                if rank == 1:               # a
                    top = None
                else:
                    top = self._board[rank-2][file-1]

                if file == 1:               # left
                    left = None
                else:
                    left = self._board[rank-1][file-2]

                self._board[rank-1].append(Square("NONE", top, left, rank, file, self._gap, self._top_gap, self._buffer))

        # reiterate over the squares and connect them to the bottom and right squares
        for rank in range(9):
            for file in range(9):
                if rank == 8:
                    bottom = None
                else:
                    bottom = self._board[rank+1][file]

                if file == 8:
                    right = None
                else:
                    right = self._board[rank][file+1]
                self._board[rank][file].set_bottom_and_right(bottom, right)

    def set_board(self, board: str) -> None:
        """sets pieces onto board using FEN"""
        rows = board.split('/')
        for rank in range(len(self._board)):
            file = 0
            for char in rows[rank]:
                if char == 'R':
                    self._board[rank][file].set_piece("RED")
                    file += 1
                elif char == 'B':
                    self._board[rank][file].set_piece("BLACK")
                    file += 1
                else:
                    file += int(char)

    def print_board(self) -> None:
        """Pretty prints the board with tiles for NONE Squares and row and column indices"""
        print("   ", end='')
        for num in range(9, 0, -1):
            print(num, end=(8 - len(str(num)))*" ")
        print()
        letters = "abcdefghi"
        for rank in range(9):
            for file in range(9):
                piece = self._board[rank][file].get_piece()
                if piece == "NONE":
                    piece = "|_____|"
                else:
                    piece = "|" + (5 - len(piece))//2 * '_' + piece + (5 - len(piece))//2 * '_' + "|"
                print(piece, end=(8 - len(piece))*" ")

            print(letters[rank])

    def count_pieces(self) -> Dict[str, int]:
        """Goes through all of the Square Objects on the board and counts how many pieces the player has left"""
        pieces: Dict[str, int] = {'BLACK': 0, 'RED': 0}

        for rank in range(9):
            for file in range(9):
                curr_piece = self._board[rank][file].get_piece()
                pieces[curr_piece] = pieces.get(curr_piece, 0) + 1

        pieces.pop("NONE")
        return pieces

    def won(self) -> bool:
        """checks if there is a winner"""
        pieces = self.count_pieces()
        if len(pieces) <= 1:
            return True
        if pieces['BLACK'] == 1 or pieces['RED'] == 1:
            return True

        return False

    def evaluate(self, player: str, board: 'Board') -> int:
        """Evaluates the state of the current board"""

        pieces_score = 0
        opponent_locations = []
        pieces = self.count_pieces()
        # print(f'pieces: {pieces}')
        previous_pieces = board.count_pieces()
        if len(pieces) == 1:
            if player in pieces:
                return 100
            else:
                return -100
        for key in pieces:
            if key == player:
                if pieces[key] == 1:
                    return -100
                pieces_score -= (previous_pieces[key] - pieces[key]) * 5
            else:
                if pieces[key] == 1:
                    return 100
                pieces_score += (previous_pieces[key] - pieces[key]) * 5
                opponent_locations = self.get_player_locations(key)
                opponent_pieces = pieces[key]
        locations = self.get_player_locations(player)
        open_score = 0
        for location in locations:
            open_score -= self._left_open_pieces(location, Square.get_left, Square.get_right)
            open_score -= self._left_open_pieces(location, Square.get_top, Square.get_bottom)

        for location in opponent_locations:
            open_score += self._left_open_pieces(location, Square.get_left, Square.get_right)
            open_score += self._left_open_pieces(location, Square.get_top, Square.get_bottom)

        return (open_score // (opponent_pieces+1)) + pieces_score + random.randint(-4, 4)

    def occupant(self, rank: int, file: int) -> 'Square':
        """returns the Square Object that is on the rank and file location"""
        return self._board[rank][file]

    def possible_moves(self, location):
        """Checks what the possible moves are of the the current selection"""
        curr_square = self.occupant(*self.convert_location(location))
        directions: List[Callable] = [Square.get_right, Square.get_bottom, Square.get_left, Square.get_top]

        # Crawl in all 4 directions
        for func in directions:
            self._possible_move_helper(curr_square, func)

    @staticmethod
    def _possible_move_helper(piece: 'Square', direction: Callable):
        """Sets all possible squares to True"""
        while direction(piece):
            piece = direction(piece)
            if piece.get_piece() != "NONE":         # if there is a piece in the way it can't be possible
                return
            else:
                piece.set_is_possible(True)

    def capture_pieces(self, piece: 'Square') -> None:
        """
        Goes in all 4 directions of the moved piece to check for capture, corners, and if moved piece captures self
        """

        directions: List[Callable] = [Square.get_right, Square.get_bottom, Square.get_left, Square.get_top]
        corners: List['Square'] = [
            self.occupant(0, 0),
            self.occupant(0, 8),
            self.occupant(8, 8),
            self.occupant(8, 0)]

        # Check all 4 directions for capture
        for func in directions:
            self._capture_piece_direction(piece, func)

        # Check corners for captures
        direction_1 = 0
        direction_2 = 1
        for corner in corners:
            self._capture_piece_corner(corner, directions[direction_1 % 4], directions[direction_2 % 4])
            direction_1 += 1
            direction_2 += 1

    @staticmethod
    def _capture_piece_corner(piece: 'Square', direction_1: Callable, direction_2: Callable) -> None:
        """Helper function to check if corner piece should be captured and update to captured"""
        # If there isn't a piece in the corner or pieces surrounding it
        if piece.get_piece() == "NONE" or direction_1(piece).get_piece() == "NONE" \
                or direction_2(piece).get_piece() == "NONE":
            return

        # Check to see if the surrounding pieces are opponent pieces
        if direction_1(piece).get_piece() != piece.get_piece() and direction_2(piece).get_piece() != piece.get_piece():
            piece.set_piece("NONE")

    def _left_open_pieces(self, piece: 'Square', direction_1: Callable, direction_2: Callable) -> int:
        """If want to implement self capture, but needs to be reimplemented in _capture_pieces"""
        flag = False
        captured_pieces: List['Square'] = []
        curr_piece = piece.get_piece()
        if curr_piece == 'NONE':
            return 0
        center = piece
        while piece and piece.get_piece() == curr_piece:
            captured_pieces.append(piece)
            piece = direction_1(piece)

        if not piece:
            return 0
        elif piece.get_piece() == "NONE":
            flag = True

        piece = direction_2(center)
        while piece and piece.get_piece() == curr_piece:
            captured_pieces.append(piece)
            piece = direction_2(piece)

        if not piece:
            return 0
        elif piece.get_piece() == "NONE" and flag:
            return len(captured_pieces) // 2

        return len(captured_pieces)

    def _capture_piece_direction(self, piece: 'Square', direction: Callable) -> None:
        """Checks if there should be captured pieces in the direction given and calls function to capture them"""
        captured_pieces: List['Square'] = []
        curr_piece = piece.get_piece()
        while direction(piece):
            piece = direction(piece)
            if piece.get_piece() == "NONE":                 # if we find empty square then no capture possible
                return

            if piece.get_piece() != curr_piece:             # if opposite color as initial add to capture
                captured_pieces.append(piece)
            else:                                           # if same color as initial moved piece capture if any
                self._update_pieces(captured_pieces)
                return

    @staticmethod
    def _update_pieces(captured_pieces: List['Square']):
        """Updates captured pieces to NONE"""
        for piece in captured_pieces:
            piece.set_piece("NONE")

    def move(self, from_rank: int, from_file: int, to_rank: int, to_file: int) -> bool:
        """
        Determines the direction the piece is trying to move and the distance it wants to travel.
        It calls a function to check if it is possible and if it is it will move the piece to the desired location.
        """

        # Assigns direction to the function of movement for a Square Object and distance to travel
        if from_file == to_file and from_rank < to_rank:            # Vertical Down
            direction = Square.get_bottom
            distance = abs(from_rank - to_rank)
        elif from_file == to_file and from_rank > to_rank:          # Vertical Up
            direction = Square.get_top
            distance = abs(from_rank - to_rank)
        elif from_rank == to_rank and from_file > to_file:          # Horizontal Left
            direction = Square.get_left
            distance = abs(from_file - to_file)
        elif from_rank == to_rank and from_file < to_file:          # Horizontal Right
            direction = Square.get_right
            distance = abs(from_file - to_file)
        else:
            return False

        # If piece can move, then move it
        if self._possible_move(self._board[from_rank][from_file], direction, distance):
            piece = self._board[from_rank][from_file].get_piece()   # Grab current piece
            self._board[to_rank][to_file].set_piece(piece)          # Change to location to piece
            self._board[from_rank][from_file].set_piece("NONE")     # Remove piece from location
            return True

        return False

    @staticmethod
    def ai_move(from_location: 'Square', to_location: 'Square'):
        """Lets AI move around the board"""
        # Move legality already checked, so switch pieces
        to_location.set_piece(from_location.get_piece())
        from_location.set_piece("NONE")

    @staticmethod
    def _possible_move(square: 'Square', direction: Callable, distance: int) -> bool:
        """Checks to make sure there are no pieces in the direction the piece would like to move"""
        for _ in range(distance):
            square = direction(square)
            if square.get_piece() != "NONE":
                return False

        return True

    def ai_possible_moves(self, location) -> List[Any]:
        """Checks what the possible moves are of the the current selection"""
        directions: List[Callable] = [Square.get_right, Square.get_bottom, Square.get_left, Square.get_top]
        possible_moves = []
        for func in directions:
            curr_moves = self._ai_possible_move_helper(location, func)
            # check to see if possible moves were found in that direction
            if curr_moves:
                possible_moves.extend(curr_moves)
        return [location, possible_moves]

    @staticmethod
    def _ai_possible_move_helper(piece: 'Square', direction: Callable) -> List['Square']:
        """Sets all possible squares to True"""
        possibles = []
        while direction(piece):
            piece = direction(piece)
            # if we find a piece in the way go and return what we have found if any
            if piece.get_piece() != "NONE":
                return possibles
            else:
                possibles.append(piece)
        return possibles

    def generate_fen(self) -> str:
        """generates FEN representation of the board"""
        fen = ""
        for rank in range(len(self._board)):
            count = 0
            for file in range(len(self._board[rank])):
                if self._board[rank][file].get_piece() == "RED":
                    if count != 0:
                        fen += str(count)
                        count = 0
                    fen += 'R'
                elif self._board[rank][file].get_piece() == "BLACK":
                    if count != 0:
                        fen += str(count)
                        count = 0
                    fen += 'B'
                else:
                    count += 1
            if count > 0:
                fen += str(count)
            fen += '/'
        return fen[:-1]

    def draw(self, win):
        """Draws the board onto the screen"""
        weight = 5
        font = pg.font.SysFont(None, 50)
        color = (0, 0, 0)
        rank = 'abcdefghi'

        # draws the horizontal lines and the right column text
        for row in range(10):
            pg.draw.line(
                win,
                pg.Color('black'),
                (self._buffer, self._buffer + row * self._gap + self._top_gap),
                (self._width - (self._buffer + 5), self._buffer + row * self._gap + self._top_gap),
                weight
            )

            if row != 9:
                row_text = font.render(rank[row], True, color)
                win.blit(
                    row_text,
                    (self._width - row_text.get_width() // 2,
                     self._buffer + row * self._gap + self._top_gap + row_text.get_height() // 2)
                )

        # draws the vertical lines and the top numbers
        for col in range(10):
            pg.draw.line(
                win,
                pg.Color('black'),
                (self._buffer + col * self._gap, self._buffer + self._top_gap),
                (self._buffer + col * self._gap, self._width - (self._buffer + 5) + self._top_gap),
                weight
            )

            if col != 9:
                col_text = font.render(str(9 - col), True, color)
                win.blit(
                    col_text,
                    (self._buffer + col * self._gap + (self._gap - col_text.get_width()) // 2,
                     self._top_gap - col_text.get_height()//2
                     )
                )


class Square:
    """Square node that is part of the board. It is connected to other squares in 4 directions"""
    def __init__(self, piece: str, top: 'Square', left: 'Square', row: int, col: int, width: int, height: int, buffer: int):
        """Initialize squares using the connected top and left squares (going left to right/top to bottom)"""
        self._piece = piece
        self._top = top
        self._right = None
        self._bottom = None
        self._left = left
        self._row = row
        self._col = col
        self._width = width
        self._height = height
        self._buffer = buffer
        self._selected = False
        self._is_possible = False
        self.x = (self._col - 1) * self._width + self._buffer + 3
        self.y = self._row * self._width + self._height - 3 * self._buffer + 7
        self._random_num = random.randint(0, 3)
        self._flip_x = True if random.randint(0, 1) == 1 else False
        self._flip_y = True if random.randint(0, 1) == 1 else False

    def get_piece(self) -> str:
        """returns the piece on the square"""
        return self._piece

    def set_is_possible(self, possible: bool) -> None:
        """set bool value to whether or not the square is possible for next move"""
        self._is_possible = possible

    def set_selected(self, selected: bool) -> None:
        """Sets if the square is selected"""
        self._selected = selected

    def set_bottom_and_right(self, bottom: "Square", right: "Square") -> None:
        """Sets the bottom and right connected squares on a separate pass through"""
        self._bottom = bottom
        self._right = right

    def get_top(self) -> 'Square':
        """returns the square that is connected above"""
        return self._top

    def get_bottom(self) -> 'Square':
        """returns the square that is connected below"""
        return self._bottom

    def get_right(self) -> 'Square':
        """returns the square that is connected to the right"""
        return self._right

    def get_left(self) -> 'Square':
        """returns the square that is connected to the left"""
        return self._left

    def set_piece(self, piece: str) -> None:
        """sets any piece that is on the square"""
        self._piece = piece

    def get_location(self):
        """returns the location of this square"""
        return self._row, self._col

    def draw(self, win: Union["Surface", "SurfaceType"]):
        """Draws the pieces onto the board and colors any squares. Green possible move and gray current selection"""

        # wooden tile
        win.blit(
            pg.transform.flip(
                pg.transform.rotate(
                    WOOD_TILE, 90 * self._random_num    # rotates a random amount
                ),
                self._flip_x,                           # random horizontal flip
                self._flip_y                            # random vertical flip
            ),
            (self.x, self.y)                            # the top left of each square
        )

        if self._piece == 'BLACK':                      # draw black piece
            win.blit(
                BLACK_PIECE,
                (self.x+2, self.y+2)
            )
        elif self._piece == 'RED':                      # draw red piece
            win.blit(
                pg.transform.rotate(RED_PIECE, 180),    # rotate red piece to look down
                (self.x+2, self.y+2)
            )

        # draw gray box around selected piece
        if self._selected:
            color = (125, 125, 125)
            pg.draw.rect(
                win,
                color,
                pg.Rect(self.x, self.y, self._width - 5, self._width - 5),
                5
            )
        # draw green box around squares that you can move to
        elif self._is_possible:
            color = (0, 200, 0)
            pg.draw.rect(
                win,
                color,
                pg.Rect(self.x, self.y, self._width - 5, self._width - 5),
                5
            )


class AI:
    """Creates an AI object to play against"""
    def __init__(self, win:  Union["Surface", "SurfaceType"], game: 'HasamiShogiGame', player: str):
        self._win = win
        self._game = game
        self._player = player
        self._opponent = "BLACK" if self._player == "RED" else "RED"
        self._board = None
        self._turn = 0

    @staticmethod
    def _set_possible_moves(board: 'Board', curr_pieces: List['Square']) -> List[List[Any]]:
        """Finds all possible moves for this turn"""
        curr_moves = []
        for piece in curr_pieces:
            curr_possible = board.ai_possible_moves(piece)
            if curr_possible[1]:
                curr_moves.append(board.ai_possible_moves(piece))
        return curr_moves

    def pick_move(self, board: 'Board') -> Tuple['Square', 'Square']:
        """Picks a move for the AI to play"""
        self._turn += 1
        self._board = board
        curr_pieces = board.get_player_locations(self._player)
        curr_moves = self._set_possible_moves(board, curr_pieces)
        rand_move = curr_moves[random.randint(0, len(curr_moves)-1) if len(curr_moves) > 1 else 0]
        max_score = -1000
        best_start, best_end = rand_move[0], (rand_move[1][random.randint(0, len(rand_move[1])-1)] if len(rand_move[1]) > 1 else rand_move[1][0])
        if self._turn < 3:
            return best_start, best_end
        for moves in curr_moves:
            start = moves[0]
            for end in moves[1]:
                eval = self.minimax(board.generate_fen(), [start, end], 1, -1000, 1000, True)
                if eval > max_score:
                    max_score = eval
                    best_start, best_end = start, end
        return best_start, best_end

    def minimax(self, board: str, position: List['Square'], depth: int, alpha: int, beta: int, maximizing_player: bool) -> int:
        """TODO"""
        curr_board = Board(self._win, board)
        from_rank, from_file = position[0].get_location()
        to_rank, to_file = position[1].get_location()
        curr_board.ai_move(curr_board.occupant(from_rank-1, from_file-1), curr_board.occupant(to_rank-1, to_file-1))
        curr_board.capture_pieces(curr_board.occupant(to_rank-1, to_file-1))

        if depth == 0 or curr_board.won():
            return curr_board.evaluate(self._player, self._board)

        if maximizing_player:
            curr_pieces = curr_board.get_player_locations(self._opponent)
            curr_moves = self._set_possible_moves(curr_board, curr_pieces)
            maxEval = -1000
            flag = False
            for moves in curr_moves:
                start: 'Square' = moves[0]
                for end in moves[1]:
                    # print(f'\tMaximizing from: {start.get_location()}\tto: {end.get_location()}')
                    eval = self.minimax(curr_board.generate_fen(), [start, end], depth-1, alpha, beta, False)
                    maxEval = max(maxEval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        flag = True
                        break
                if flag:
                    break
            return maxEval
        else:
            curr_pieces = curr_board.get_player_locations(self._player)
            curr_moves = self._set_possible_moves(curr_board, curr_pieces)
            minEval = 1000
            flag = False
            for moves in curr_moves:
                start: 'Square' = moves[0]
                for end in moves[1]:
                    # print(f'\tMinimizing from: {start.get_location()}\tto: {end.get_location()}')
                    eval = self.minimax(curr_board.generate_fen(), [start, end],
                                        depth - 1, alpha, beta, True)
                    minEval = min(minEval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        flag = True
                        break
                if flag:
                    break
            return minEval


def top_bar(win: Union["Surface", "SurfaceType"], game: HasamiShogiGame) -> None:
    """Draws the top bar onto the screen"""
    font = pg.font.SysFont(None, 60)
    color = (0, 0, 0)
    # Display the current player at the top of the board
    player_text = font.render(game.get_active_player(), True, color)
    win.blit(
        player_text,
        ((win.get_width() - player_text.get_width()) // 2, 15)
    )
    # Display the total number of pieces for Black
    font = pg.font.SysFont(None, 40)
    black_remaining = font.render(f"Black: {9 - game.get_num_captured_pieces('BLACK')}", True, color)
    win.blit(
        black_remaining,
        (20, 25)
    )
    #Display the total number of pieces for Red
    red_remaining = font.render(f"Red: {9 - game.get_num_captured_pieces('RED')}", True, color)
    win.blit(
        red_remaining,
        (win.get_width() - red_remaining.get_width() - 20, 25)
    )


def winner(win: Union["Surface", "SurfaceType"], game: HasamiShogiGame) -> None:
    """Displays winner splash screen"""
    paper_wall = pg.transform.scale(pg.image.load('Images/paper_wall.webp'), (win.get_width(), win.get_height()))
    win.blit(paper_wall, (0, 0))
    font = pg.font.SysFont(None, 100)
    color = (0, 0, 0)
    border = (125, 125, 125)
    winner_text = font.render(game.get_game_state().replace('_', ' '), True, color)
    play_again = font.render("Play again? (Y/N)", True, color)

    # Draw rectangle over background to make words easier to read
    pg.draw.rect(
        win,
        border,
        pg.Rect(
            (win.get_width() - play_again.get_width()) // 2 - 10,
            (win.get_height() - winner_text.get_height())//2 - 10,
            play_again.get_width() + 20,
            winner_text.get_height() + play_again.get_height() + 50
        )

    )
    # Display who won
    win.blit(
        winner_text,
        (
            (win.get_width() - winner_text.get_width()) // 2,
            (win.get_height() - winner_text.get_height())//2
        )
    )
    # Display if they want to play again
    win.blit(
        play_again,
        (
            (win.get_width() - play_again.get_width()) // 2,
            (win.get_height() + winner_text.get_height() + play_again.get_height())//2
        )
    )


def window_update(win: Union["Surface", "SurfaceType"], game: HasamiShogiGame) -> None:
    """Updates the drawing of all things"""

    win.fill((255, 255, 255))
    # Display each square and board
    if game.get_game_state() == "UNFINISHED":
        for rank in game.get_board().get_board():
            for square in rank:
                square.draw(win)

        game.get_board().draw(win)
        top_bar(win, game)
    # Display winner
    else:
        winner(win, game)


def title_update(win: Union["Surface", "SurfaceType"], selection: int = 0) -> None:
    """Updates the title screen window"""
    win.fill((255, 255, 255))
    font = pg.font.SysFont(None, 100)
    color = (0, 0, 0)
    one_player = font.render("1 Player", True, color)
    two_players = font.render("2 Players", True, color)
    ai_play = font.render("AIs play", True, color)

    # create green box around 1 player box
    if selection == 0:
        pg.draw.rect(
            win,
            (0, 255, 0),
            pg.Rect(
                (win.get_width() - one_player.get_width()) // 2 - 10,
                (win.get_height() - one_player.get_height()) // 3 - 10,
                one_player.get_width() + 20,
                one_player.get_height() + 20
            ),
            5
        )
    # create green box around 2 players box
    elif selection == 1:
        pg.draw.rect(
            win,
            (0, 255, 0),
            pg.Rect(
                (win.get_width() - two_players.get_width()) // 2 - 10,
                (win.get_height() + two_players.get_height() + one_player.get_height()) // 3 - 10,
                two_players.get_width() + 20,
                two_players.get_height() + 20
            ),
            5
        )
    else:
        pg.draw.rect(
            win,
            (0, 255, 0),
            pg.Rect(
                (win.get_width() - ai_play.get_width()) // 2 - 10,
                (win.get_height() + two_players.get_height() + one_player.get_height() + ai_play.get_height()) // 3 - 10,
                ai_play.get_width() + 20,
                ai_play.get_height() + 20
            ),
            5
        )
    # Display 1 player text
    win.blit(
        one_player,
        (
            (win.get_width() - one_player.get_width()) // 2,
            (win.get_height() - one_player.get_height()) // 3
        )
    )
    # Display 2 players text
    win.blit(
        two_players,
        (
            (win.get_width() - two_players.get_width()) // 2,
            (win.get_height() + two_players.get_height() + one_player.get_height()) // 3
        )
    )

    win.blit(
        ai_play,
        (
            (win.get_width() - ai_play.get_width()) // 2,
            (win.get_height() + two_players.get_height() + one_player.get_height() + ai_play.get_height()) // 3
        )
    )


def title_screen() -> None:
    """Holds logic for the title screen interaction"""

    # create pygame window
    pg.init()
    width = 750
    height = 820
    win = pg.display.set_mode((width, height))
    pg.display.set_caption("Hasami Shogi")
    selection = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif pg.key.get_pressed()[pg.K_SPACE]:          # space is pressed, so play game
                play_game(win, selection)
            elif pg.key.get_pressed()[pg.K_DOWN]:           # Scrolls down, but wraps around
                selection = (selection + 1) % 3
            elif pg.key.get_pressed()[pg.K_UP]:             # Scrolls up, but wraps around
                selection = (selection - 1) % 3
        title_update(win, selection)
        pg.display.update()


def play_game(win, selection) -> None:
    """plays the Hasami Shogi Game"""
    random.seed()
    game = HasamiShogiGame(win)
    from_piece = None
    if selection == 0 or selection == 2:      # if 1 player was selected
        ai_red = AI(win, game, "RED")
        ai_black = AI(win, game, "BLACK")
    while True:

        for event in pg.event.get():
            # if window closed or if there was a winner and players chose N (not to continue)
            if event.type == pg.QUIT or (pg.key.get_pressed()[pg.K_n] and game.get_game_state() != 'UNFINISHED'):
                sys.exit()
            # if game is finished and player chose Y (play again)
            elif pg.key.get_pressed()[pg.K_y] and game.get_game_state() != 'UNFINISHED':
                game = HasamiShogiGame(win)

            # Lets players click on pieces to move. Selection 1 means 2 players are playing
            if game.get_active_player() == 'BLACK' and (selection == 1 or selection == 0):
                if pg.mouse.get_pressed()[0]:               # Left click
                    mouse = pg.mouse.get_pos()              # Get x and y position on screen
                    location = game.get_location(mouse)     # change position to square locations

                    # Check if this is the first click and that the square clicked is current player piece
                    if game.get_initiate_move() and game.get_square_occupant(location) == game.get_active_player():
                        from_piece = location                       # Place clicked is the from location
                        game.set_initiate_move(False)               # change to piece has been selected to move
                        game.get_board().select_square(location)    # Change the display of the clicked square
                        game.get_board().possible_moves(location)               # Change display of possible squares

                    # Check if this is the second click and the click is in a possible move.
                    # Also if the same square is clicked twice
                    elif not game.get_initiate_move() and (game.make_move(from_piece, location)
                                                           or from_piece == location):
                        game.get_board().deselect_square(from_piece)    # change the display of original piece back
                        game.get_board().refresh_possible()             # remove display update to possibles
                        from_piece = None                               # Change from piece to not holding anything
                        game.set_initiate_move(True)                    # Change back to 1st click
                        print(game.get_board().generate_fen())

            # It is the AI's turn
            else:
                begin = time.time()
                if game.get_active_player() == "RED":
                    from_location, to_location = ai_red.pick_move(game.get_board())
                    print(f'Red\'s selection: {from_location.get_location(), to_location.get_location()}')
                    game.ai_make_move(from_location, to_location)
                    print(game.get_board().generate_fen())
                    game.get_board().print_board()
                else:
                    from_location, to_location = ai_black.pick_move(game.get_board())
                    print(f'Black\'s selection: {from_location.get_location(), to_location.get_location()}')
                    game.ai_make_move(from_location, to_location)
                    print(game.get_board().generate_fen())
                    game.get_board().print_board()
                end = time.time()
                print(end - begin)

        # window_update(win, game)
        # pg.display.update()


if __name__ == "__main__":
    # title_screen()
    # pg.quit()

    pg.init()
    width = 750
    height = 820
    win = pg.display.set_mode((width, height))
    game = HasamiShogiGame(win)
    rank = "Xabcdefghi"
    ai_red = AI(win, game, "RED")
    ai_black = AI(win, game, "BLACK")
    turn = 0
    start = time.time()
    while game.get_game_state() == "UNFINISHED":
        turn += 1
        begin = time.time()
        if game.get_active_player() == "RED":
            from_location, to_location = ai_red.pick_move(game.get_board())
        else:
            from_location, to_location = ai_black.pick_move(game.get_board())

        from_rank, from_file = from_location.get_location()
        to_rank, to_file = to_location.get_location()
        from_rank, to_rank = rank[from_rank], rank[to_rank]
        from_file, to_file = str(from_file), str(to_file)

        print(f'{game.get_active_player().lower().capitalize()}\'s selection: {from_rank + from_file} -> {to_rank + to_file}')
        game.ai_make_move(from_location, to_location)
        print(game.get_board().count_pieces())
        print(game.get_board().generate_fen())
        game.get_board().print_board()
        end = time.time()
        print(f'Turn: {turn}, Selection Time:{end - begin}, Total Time: {int((end - start) // 60)}:{(end - start) % 60}')

    print(game.get_game_state())
    pg.quit()
