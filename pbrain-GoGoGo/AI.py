import pisqpipe as pp
import time
from status import *

dx = [1, 0, 1, 1]
dy = [0, 1, 1, -1]

#switch to the opponent of the player
def OPPONENT(player):
    if player == stateType['OP']:
        return stateType['ME']
    elif player == stateType['ME']:
        return stateType['OP']
    raise ValueError("Invalid Player.")

stateType = {'EMPTY': 2, 'ME': 0, 'OP': 1, 'WRONG': 3}  #a dict, shows the type of cells

class point:
    #Functional point
    def __init__(self, x = 0, y = 0, value = 0):
        self.x = x
        self.y = y
        self.value = value

class cell:
    #basic information: constitute the board
    def __init__(self, x =0, y = 0, value = 0):
        self.type = stateType["EMPTY"] #empty, me, op or wrong
        self.x = x
        self.y = y
        self.adj1 = 0    #adj1=1: have one-distance neighbor
        self.adj2 = 0    #adj2=1: have two-distance neighbor
        self.value = value   #for choosing candidates and minimax
        self.pattern = [[0, 0] for i in range(4)] #4 directions, 2 players
        self.status1 = [[0, 0] for i in range(4)] #4 directions, 2 players
        self.status4 = [0, 0]
    #for pattern grading
    def update1(self, k):
        self.status1[k][0] = STATUS1[self.pattern[k][0]][self.pattern[k][1]]
        self.status1[k][1] = STATUS1[self.pattern[k][1]][self.pattern[k][0]]

    def update4(self):
        self.status4[0] = STATUS4[self.status1[0][0]][self.status1[1][0]][self.status1[2][0]][self.status1[3][0]]
        self.status4[1] = STATUS4[self.status1[0][1]][self.status1[1][1]][self.status1[2][1]][self.status1[3][1]]

    def prior(self):
        return (PRIOR[self.pattern[0][0]][self.pattern[0][1]] +
        PRIOR[self.pattern[1][0]][self.pattern[1][1]] +
        PRIOR[self.pattern[2][0]][self.pattern[2][1]] +
        PRIOR[self.pattern[3][0]][self.pattern[3][1]] +
        PRIOR[self.pattern[0][1]][self.pattern[0][0]] +
        PRIOR[self.pattern[1][1]][self.pattern[1][0]] +
        PRIOR[self.pattern[2][1]][self.pattern[2][0]] +
        PRIOR[self.pattern[3][1]][self.pattern[3][0]] +
        (self.adj1 != 0))

class ai:
    def __init__(self, width = 20, height = 20):
        self.width = width
        self.height = height
        self.maxCells = width * height
        self.board = [[cell(i, j) for i in range(width + 8)] for j in range(height + 8)]
        self.who = stateType['ME']
        self.opp = stateType['OP']
        self.moveCount = 0
        self.remCount = 0
        self.remMove = []
        self.remCell = []
        self.remULCand = []
        self.remLRCand = []
        self.nStates = [[0 for i in range(10)] for j in range(2)]  #number of states of players
        self.upperLeftCand = point(4, 4)
        self.lowerRightCand = point(width + 4, height + 4)
        self.nSearched = 0
        self.WIN_MAX = 30000
        self.WIN_MIN = 25000


    def generateBoard(self):
        #initialize type
        for x in range(self.width + 8):
            for y in range(self.height + 8):
                if (x < 4 or x >= self.width + 4 or y < 4 or y >= self.height + 4):
                    self.board[x][y].type = stateType["WRONG"]
        #initialize pattern
        for x in range(4, self.width + 4):
            for y in range(4, self.height + 4):
                for k in range(4):  #4 directions
                    xx, yy = x - dx[k], y - dy[k]
                    p = 0b00001000
                    while p != 0:  #the range
                        if self.board[xx][yy].type == stateType["WRONG"]:
                            self.board[x][y].pattern[k][0] ^= p
                            self.board[x][y].pattern[k][1] ^= p
                        p = p >> 1
                        xx, yy = xx - dx[k], yy - dy[k]
                    xx, yy = x + dx[k], y + dy[k]
                    p = 0b00010000
                    while p <= 128:
                        if self.board[xx][yy].type == stateType["WRONG"]:
                            self.board[x][y].pattern[k][0] ^= p
                            self.board[x][y].pattern[k][1] ^= p
                        p = p << 1
                        xx, yy = xx + dx[k], yy + dy[k]
        #initialize status1 and status4
        for x in range(4, self.width + 4):
            for y in range(4, self.height + 4):
                self.board[x][y].update1(0)
                self.board[x][y].update1(1)
                self.board[x][y].update1(2)
                self.board[x][y].update1(3)
                self.board[x][y].update4()

    def printBoard(self):
        board = [["." for i in range(self.width)] for j in range(self.height)]
        for i in range(len(board)):
            board[i].append(i)
        for x in range(4, self.width + 4):
            for y in range(4, self.height + 4):
                if self.board[x][y].type == stateType["WRONG"]:
                    board[x-4][y-4] = "#"
                if self.board[x][y].type == stateType["ME"]:
                    board[x-4][y-4] = "X"
                if self.board[x][y].type == stateType["OP"]:
                    board[x-4][y-4] = "O"
        lst = list(range(len(board)))
        for i in range(len(lst)):
            lst[i] = str(lst[i])
        board.append(lst)
        for line in board:
            print(line)


    def setWho(self, who):
        self.who = who
        self.opp = OPPONENT(who)

    def _move(self, x, y):
        #assert self.check()
        self.nSearched += 1
        self.nStates[0][self.board[x][y].status4[0]] -= 1
        self.nStates[1][self.board[x][y].status4[1]] -= 1
        self.board[x][y].type = self.who
        self.remCell.append(self.board[x][y])
        self.remMove.append(point(x, y))
        self.moveCount += 1
        self.remCount += 1
        self.remULCand.append(self.upperLeftCand)
        self.remLRCand.append(self.lowerRightCand)
        if (x - 2 < self.upperLeftCand.x): self.upperLeftCand.x = max(x - 2, 4)
        if (y - 2 < self.upperLeftCand.y): self.upperLeftCand.y = max(y - 2, 4)
        if (x + 2 > self.lowerRightCand.x): self.lowerRightCand.x = min(x + 2, self.width + 3)
        if (y + 2 > self.lowerRightCand.y): self.lowerRightCand.y = min(y + 2, self.height + 3)
        #modify pattern and points
        for k in range(4):
            xt, yt = x, y
            p = 0b00001000
            while p!=0:
                xt, yt = xt + dx[k], yt + dy[k]
                self.board[xt][yt].pattern[k][self.who] ^= p
                if self.board[xt][yt].type == stateType["EMPTY"]:
                    self.board[xt][yt].update1(k)
                    self.nStates[0][self.board[xt][yt].status4[0]] -= 1
                    self.nStates[1][self.board[xt][yt].status4[1]] -= 1
                    self.board[xt][yt].update4()
                    self.nStates[0][self.board[xt][yt].status4[0]] += 1
                    self.nStates[1][self.board[xt][yt].status4[1]] += 1
                p = p >> 1
            xt, yt = x, y
            p = 0b00010000
            while p <= 128:
                xt, yt = xt - dx[k], yt - dy[k]
                self.board[xt][yt].pattern[k][self.who] ^= p
                if self.board[xt][yt].type == stateType["EMPTY"]:
                    self.board[xt][yt].update1(k)
                    self.nStates[0][self.board[xt][yt].status4[0]] -= 1
                    self.nStates[1][self.board[xt][yt].status4[1]] -= 1
                    self.board[xt][yt].update4()
                    self.nStates[0][self.board[xt][yt].status4[0]] += 1
                    self.nStates[1][self.board[xt][yt].status4[1]] += 1
                p = p << 1
        #update candidates
        self.board[x - 1][y - 1].adj1 +=1
        self.board[x    ][y - 1].adj1 +=1
        self.board[x + 1][y - 1].adj1 +=1
        self.board[x - 1][y    ].adj1 +=1
        self.board[x + 1][y    ].adj1 +=1
        self.board[x - 1][y + 1].adj1 +=1
        self.board[x    ][y + 1].adj1 +=1
        self.board[x + 1][y + 1].adj1 +=1
        self.board[x - 2][y - 2].adj2 +=1
        self.board[x    ][y - 2].adj2 +=1
        self.board[x + 2][y - 2].adj2 +=1
        self.board[x - 2][y    ].adj2 +=1
        self.board[x + 2][y    ].adj2 +=1
        self.board[x - 2][y + 2].adj2 +=1
        self.board[x    ][y + 2].adj2 +=1
        self.board[x + 2][y + 2].adj2 +=1

        #exchange player
        self.who = OPPONENT(self.who)
        self.opp = OPPONENT(self.opp)
        #assert self.check()

        """def check(self):
            nSt = [[0 for i in range(10)] for j in range(2)]
            Allcands = self._AllCand()
            for cand in Allcands:
                nSt[0][self.board[cand.x][cand.y].status4[0]] += 1
                nSt[1][self.board[cand.x][cand.y].status4[1]] += 1
            for i in range(2):
                for j in range(1, 10):
                    if nSt[i][j] != self.nStates[i][j]:
                        print(nSt, self.nStates)
                        return False
            return True"""
    def move(self, x, y):
        self._move(x + 4, y + 4)
    #regret
    def undo(self):
        #assert self.check()
        self.moveCount -= 1
        self.remCount -= 1
        lastMove = self.remMove.pop()
        x, y = lastMove.x, lastMove.y
        self.remCell.pop()
        self.upperLeftCand = self.remULCand.pop()
        self.lowerRightCand = self.remLRCand.pop()
        self.board[x][y].update1(0)
        self.board[x][y].update1(1)
        self.board[x][y].update1(2)
        self.board[x][y].update1(3)
        self.board[x][y].update4()
        self.nStates[0][self.board[x][y].status4[0]] += 1
        self.nStates[1][self.board[x][y].status4[1]] += 1
        self.board[x][y].type = stateType["EMPTY"]
        self.who = OPPONENT(self.who)
        self.opp = OPPONENT(self.opp)
        #modify pattern
        for k in range(4):
            xt, yt = x, y
            p = 0b00010000
            while p <= 128:
                xt -= dx[k]
                yt -= dy[k]
                self.board[xt][yt].pattern[k][self.who] ^= p
                if self.board[xt][yt].type == stateType["EMPTY"]:
                    self.board[xt][yt].update1(k)
                    self.nStates[0][self.board[xt][yt].status4[0]] -= 1
                    self.nStates[1][self.board[xt][yt].status4[1]] -= 1
                    self.board[xt][yt].update4()
                    self.nStates[0][self.board[xt][yt].status4[0]] += 1
                    self.nStates[1][self.board[xt][yt].status4[1]] += 1
                p = p << 1
            xt, yt = x, y
            p = 0b00001000
            while p != 0:
                xt += dx[k]
                yt += dy[k]
                self.board[xt][yt].pattern[k][self.who] ^= p
                if self.board[xt][yt].type == stateType["EMPTY"]:
                    self.board[xt][yt].update1(k)
                    self.nStates[0][self.board[xt][yt].status4[0]] -= 1
                    self.nStates[1][self.board[xt][yt].status4[1]] -= 1
                    self.board[xt][yt].update4()
                    self.nStates[0][self.board[xt][yt].status4[0]] += 1
                    self.nStates[1][self.board[xt][yt].status4[1]] += 1
                p = p >> 1
        # delete candidates
        self.board[x - 1][y - 1].adj1 -= 1
        self.board[x    ][y - 1].adj1 -= 1
        self.board[x + 1][y - 1].adj1 -= 1
        self.board[x - 1][y    ].adj1 -= 1
        self.board[x + 1][y    ].adj1 -= 1
        self.board[x - 1][y + 1].adj1 -= 1
        self.board[x    ][y + 1].adj1 -= 1
        self.board[x + 1][y + 1].adj1 -= 1
        self.board[x - 2][y - 2].adj2 -= 1
        self.board[x    ][y - 2].adj2 -= 1
        self.board[x + 2][y - 2].adj2 -= 1
        self.board[x - 2][y    ].adj2 -= 1
        self.board[x + 2][y    ].adj2 -= 1
        self.board[x - 2][y + 2].adj2 -= 1
        self.board[x    ][y + 2].adj2 -= 1
        self.board[x + 2][y + 2].adj2 -= 1
        #assert self.check()

    def check(self):
        nSt = [[0 for i in range(10)] for j in range(2)]
        Allcands = self._AllCand()
        for cand in Allcands:
            nSt[0][self.board[cand.x][cand.y].status4[0]] += 1
            nSt[1][self.board[cand.x][cand.y].status4[1]] += 1
        for i in range(2):
            for j in range(1, 10):
                if nSt[i][j] != self.nStates[i][j]:
                    print(nSt, self.nStates)
                    return False
        return True

    def stopTime(self):
        return min(pp.info_timeout_turn, pp.info_time_left / 7)

    #for minimax
    def evaluate(self):
        p = {self.who:0, self.opp:0}
        for i in range(self.remCount):
            c = self.remCell[i]
            for k in range(4):
                p[c.type] += RANK[CONFIG[c.pattern[k][c.type]][c.pattern[k][1 - c.type]]]
        return p[self.who] - p[self.opp]

    def _AllCand(self):
        cands = []
        for x in range(self.upperLeftCand.x, self.lowerRightCand.x + 1):
            for y in range(self.upperLeftCand.y, self.lowerRightCand.y + 1):
                if (self.board[x][y].type == stateType["EMPTY"]) and (self.board[x][y].adj1 or self.board[x][y].adj2):
                    cands.append(cell(x, y))
        return cands

    #generate candidates
    def generateCand(self):
        cands = []
        AllCands = self._AllCand()
        n = 0
        for cand in AllCands:
            x, y = cand.x, cand.y
            if self.board[x][y].prior() > 1:
                cands.append(cell())
                cands[n].x, cands[n].y = x, y
                cands[n].value = self.board[x][y].prior()
                n += 1 #refuse bad choice
        #special condition: only one choice
        def oneCand(player, state, cands):
            i = 0
            while (self.board[cands[i].x][cands[i].y].status4[player] != state):
                i+=1
            cnds = [cands[i]]
            return cnds
        #special conditions
        #print(self.nStates)
        if self.nStates[self.who][A] > 0: #FIVE!
            #print("wow my5")
            cands = oneCand(self.who, A, cands)
            return cands, 1
        if self.nStates[self.opp][A] > 0: #Block Opponent's FIVE
            #print("wow your4")
            cands = oneCand(self.opp, A, cands)
            return cands, 1
        if self.nStates[self.who][B] > 0: #Attain live-FOUR
            #print("wow my4")
            cands = oneCand(self.who, B, cands)
            return cands, 1
        #Block opponent's THREE
        if self.nStates[self.opp][B] > 0:
            #print("wow your3")
            cands = []
            n = 0
            for cand in AllCands:
                x, y = cand.x, cand.y
                cands.append(cell())
                if (self.board[x][y].status4[self.who] >= E) or (self.board[x][y].status4[self.opp] >= E):
                    cands[n].x, cands[n].y = x, y
                    cands[n].value = self.board[x][y].prior()
                if (cands[n].value > 0): n += 1
        cands = cands[0:n]
        return cands, n

    def vcf(self):
        if self.nStates[self.who][A] >= 1: #win
            return 1
        if self.nStates[self.opp][A] >= 2: #cold
            return -2
        if self.nStates[self.opp][A] == 1:
            Allcands = self._AllCand()
            for cand in Allcands:
                x, y = cand.x, cand.y
                if self.board[x][y].status4[self.opp] == A:
                    self._move(x, y)
                    q = -self.vcf()
                    self.undo()
                    if q < 0: #cold
                        q -= 1
                    elif q > 0:
                        q += 1
                    return q
        if self.nStates[self.who][B] >= 1: # almost win
            return 3
        if self.nStates[self.who][C] >= 1: # XOOO_ * _OO
            if self.nStates[self.opp][B] == 0 and self.nStates[self.opp][C] == 0 \
                    and self.nStates[self.opp][D] == 0 and self.nStates[self.opp][E] == 0: #if not, opp cannot stop me
                return 5
            Allcands = self._AllCand()
            for cand in Allcands:
                x, y = cand.x, cand.y
                if self.board[x][y].status4[self.who] == C:
                    self._move(x, y)
                    q = -self.vcf()
                    self.undo()
                    if q > 0:  # cold
                        return q + 1
        if self.nStates[self.who][F] >= 1: # OO_OO
            if (self.nStates[self.opp][B] == 0 and self.nStates[self.opp][C] == 0 \
                    and self.nStates[self.opp][D] == 0 and self.nStates[self.opp][E] == 0):
                return 5
        return 0


    def minimax(self, depth, root, alpha, beta):
        best = point(0, 0, alpha - 1)
        if alpha > beta + 1:
            return point(0, 0, beta + 1)
        #search VCF or not
        q = self.vcf()
        if q != 0:
            if not root :
                if q > 0:
                    return point(0, 0, self.WIN_MAX - q)
                else:
                    return point(0, 0, -self.WIN_MAX - q)
            if q == 1:
                #print("will win")
                Allcands = self._AllCand()
                for cand in Allcands:
                    if self.board[cand.x][cand.y].status4[self.who] == A:
                        return point(cand.x, cand.y, self.WIN_MAX - 1)

        if depth == 0:
            return point(0, 0, self.evaluate())
        depth -= 1
        cands, n = self.generateCand()
        if n > 1:
            cands.sort(key = lambda cand: -cand.value)
        elif n == 1:
            if root: return point(cands[0].x, cands[0].y, cands[0].value)
        else:
            cands = self._AllCand()
            n = len(cands)
            if n == 0:
                best.value = 0
        #cands = cands[0:min(n, 6)]
        cands = cands[0:min(n, 10)]
        for cand in cands:
            assert best.value <= beta
            self._move(cand.x, cand.y)
            alpha2 = -beta
            beta2 = -(best.value + 1)
            if beta2 >= self.WIN_MIN: beta2 += 1
            if alpha2 <= -self.WIN_MIN: alpha2 -=1

            m = self.minimax(depth, False, alpha2, beta2)
            v = -m.value
            if v >= self.WIN_MIN: v -= 1
            if v <= -self.WIN_MIN: v += 1
            self.undo()

            if v > best.value:
                best = point(cand.x, cand.y, v)
                if v > beta: return point(best.x, best.y, beta + 1)
            if pp.terminateAI: break
        return best

    def turn(self):
        startTime = time.time()
        if self.moveCount == 0:
            return self.width//2, self.height//2
        for depth in range(7, 8):
            best = self.minimax(depth, True, float("-inf"), float("inf"))
            x, y = best.x-4, best.y-4
            if pp.terminateAI:
                break
        return x, y

    def eval(self):
        raise
