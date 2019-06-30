import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
import AI

pp.infotext = 'name="pbrain-minimax", author="ZZ", version="1.0", country="CN" '

MAX_BOARD = 100

def brain_init():
        if pp.width < 5 or pp.height < 5:
                pp.pipeOut("ERROR size of the board")
                return
        if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
                pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
                return
        global board
        board = AI.ai(pp.width, pp.height)
        board.generateBoard()
        pp.pipeOut("OK")

def brain_restart():
        global board
        board = AI.ai(pp.width, pp.height)
        board.generateBoard()
        pp.pipeOut("OK")

def brain_my(x, y):
        board.setWho(AI.stateType["ME"])
        board.move(x, y)

def brain_opponents(x, y):
        board.setWho(AI.stateType["OP"])
        board.move(x, y)

def brain_block(x, y):
    raise("not implemented")

def brain_takeback(x, y):
    board.undo()
    return 0

def brain_turn():
    board.setWho(AI.stateType["ME"])
    x, y = board.turn()
    pp.do_mymove(x, y)

def brain_end():
    del board

def brain_about():
    pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
    import win32gui
    def brain_eval(x, y):
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
    pp.brain_eval = brain_eval

def main():
    pp.main()

if __name__ == "__main__":
    main()
