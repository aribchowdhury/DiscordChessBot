class ChessPiece:
    def __init__(self, loc: str, color: str):
        self.loc = loc
        self.color = color
        self.num_movements = 0
        self.valid_moves = set() #update whenever a piece moves after picture gets sent
        self.board = None # Internal memory of board state updated with update call

    def updateValidMoves(self, board: dict, king_pos: str): #  Update set of all valid moves of chess piece
        # Get all possible movements of the piece itself
        # Check validity against if any pieces of yours are located at those spots
        self.lookForAvoidAllies()
        self.lookForChecks(king_pos)
    
    def lookForAvoidAllies(self): # Update set of all valid moves of chess piece to be spaces that won't land on ally
        team_spaces = set()
        for pos in self.valid_moves:
            if pos in ["kc", "qc", "ep"]:
                continue
            if self.board.get(pos, None):
                if self.board[pos].color == self.getColor():
                    team_spaces.add(pos)
        self.valid_moves -= team_spaces

    def lookForChecks(self, king_pos: str):
        # Look through all valid moves and see if any result in check, remove them from valid moves
        non_check_moves = set()
        for pos in self.valid_moves:
            if self.piece == " king":
                king_pos_temp = pos
            else:
                king_pos_temp = king_pos
            if pos == "kc":
                action = {"moved":[[self, self.loc, "g"+self.loc[1]], [self.board["h"+self.loc[1]], "h"+self.loc[1], "f"+self.loc[1]]], "taken":[]}
            elif pos == "qc":
                action = {"moved":[[self, self.loc, "c"+self.loc[1]], [self.board["a"+self.loc[1]], "a"+self.loc[1], "d"+self.loc[1]]], "taken":[]}
            elif "ep" in pos:
                action = {"moved":[], "taken":[[self.board[pos[2:]], pos[2:]]]}
                if self.board[pos[2:]].getColor() == "white":
                    action["moved"].append([self, self.loc, self._addToLocWithNums(pos[2:], [0,-1])])
                else:
                    action["moved"].append([self, self.loc, self._addToLocWithNums(pos[2:], [0,1])])
            else:
                action = {"moved":[[self, self.loc, pos]], "taken":[[self.board[pos],pos]] if self.board.get(pos, None) else []}
            for piece, loc in action["taken"]:
                self.board[loc] = None
            for piece, loc, new_loc in action["moved"]:
                self.board[loc] = None
                self.board[new_loc] = piece 
            if not self._isThreatened(king_pos_temp):
                non_check_moves.add(pos)
            for piece, loc, new_loc in action["moved"]:
                self.board[loc] = piece
                self.board[new_loc] = None
            for piece, loc in action["taken"]:
                self.board[loc] = piece
        self.valid_moves = non_check_moves

    def moveTo(self, pos): # Move piece if possible and return board and pos moved to, otherwise return -1 for pos
        if pos not in self.valid_moves:
            return self.board, -1
        else:
            if pos == "kc":
                return self.castle("king")
            elif pos == "qc":
                return self.castle("queen")
            elif "ep" in pos:
                return self.enPassante(pos)
            else:
                if self.getPiece() == " pawn" and abs(int(self.loc[1])-int(pos[1])) == 2:
                    rpawn = self._addToLocWithNums(pos,[1,0])
                    if self.board.get(rpawn, None) and self.board[rpawn].getName() == self.getOtherColor() + " pawn":
                        self.board[rpawn].add_ep = pos 
                    lpawn = self._addToLocWithNums(pos,[-1,0])
                    if self.board.get(lpawn, None) and self.board[lpawn].getName() == self.getOtherColor() + " pawn":
                        self.board[lpawn].add_ep = pos 
                self.board[self.loc] = None
                self.loc = pos
                self.board[self.loc] = self 
                self.num_movements += 1
                return self.board, pos

    def castle(self, side): # Dummy function for castling
        pass

    def enPassante(self, pos): # Dummy function for enPassante
        pass

    def getPiece(self): # Get piece type
        return self.piece
    
    def getColor(self): # Get piece color
        return self.color

    def getOtherColor(self): # Get opposing team's color
        return "white" if self.color == "black" else "black"

    def getName(self): # Get full name of piece (color + type)
        return self.color + self.piece

    def getLoc(self): # Get current location of piece
        return self.loc

    def hasMoved(self): # See if piece has been moved yet, useful for castling
        return self.num_movements > 0
    
    def _inBounds(self, pos): # Check if a pos is in bounds of the board
        return (isinstance(pos, tuple) and 1 <= pos[0] <= 8 and 1 <= pos[1] <= 8) or\
            (isinstance(pos, str) and 'a' <= pos[0] <= 'h' and '1' <= pos[1] <= '8')

    def _convertLocToNums(self, pos): # Convert location to a 2-integer indexed position
        return (ord(pos[0])-ord('a')+1, ord(pos[1])-ord('1')+1)

    def _convertNumsToLoc(self, pos): # Convert 2-integer indexed position to location
        return chr(pos[0]+ord('a')-1) + chr(pos[1]+ord('1')-1)

    def _addToLocWithNums(self, pos, add_with): # Add to a location with a 2-integer indexed movement
        pos = self._convertLocToNums(pos)
        pos = (pos[0]+add_with[0], pos[1]+add_with[1])
        if not self._inBounds(pos):
            return "NA"
        else:
            return self._convertNumsToLoc(pos)

    def _isThreatened(self, loc: str): # Check if location is threatened by opposing team
        king_targets = [(1,1),(1,0),(0,1),(0,1),(0,-1),(-1,1),(1,-1),(-1,-1)]
        knight_targets = [(1,2),(2,1),(-1,2),(2,-1),(-1,-2),(-2,-1),(1,-2),(-2,1)]
        pawn_targets = [(i, 1 if self.getColor() == "black" else -1) for i in [-1,1]]
        for piece, targets in [(" king", king_targets), (" knight", knight_targets), (" pawn", pawn_targets),]:
            for target in targets:
                if self.board.get(self._addToLocWithNums(loc, target), None) != None:
                    if self.board[self._addToLocWithNums(loc, target)].getName() == self.getOtherColor() + piece:
                        return True
        for piece_name, shift in [(" rook",[1,0]),(" rook",[-1,0]),(" rook",[0,1]),(" rook",[0,-1]), \
        (" bishop",[1,1]),(" bishop",[1,-1]),(" bishop",[-1,1]),(" bishop",[-1,-1])]:
            temp_loc = self._addToLocWithNums(loc, shift)
            while temp_loc != "NA":
                switch = self.board.get(temp_loc, None)
                if switch == None:
                    temp_loc = self._addToLocWithNums(temp_loc, shift)
                elif switch.getName() in [self.getOtherColor() + piece_name, self.getOtherColor() + " queen"]:
                    return True
                else:
                    break
        return False
    