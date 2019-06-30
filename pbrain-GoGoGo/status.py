from knowledge import *

def getStatus4(s0, s1, s2, s3):
    n = [0 for i in range(10)]
    n[s0] += 1
    n[s1] += 1
    n[s2] += 1
    n[s3] += 1
    if (n[9] >= 1): return A # OOOO_
    if (n[8] >= 1): return B # OOO_
    if (n[7] >= 2): return B # XOOO_ * _OOOX
    if (n[7] >= 1 & n[6] >= 1): return C # XOOO_ * _OO
    if (n[7] >= 1 & n[5] >= 1): return D # XOOO_ * _OOX
    if (n[7] >= 1 & n[4] >= 1): return D # XOOO_ * _O
    if (n[7] >= 1): return E # XOOO_
    if (n[6] >= 2): return F # OO_ * _OO
    if (n[6] >= 1 & n[5] >= 1): return G # OO_ * _OOX
    if (n[6] >= 1 & n[4] >= 1): return G # OO_ * _O
    if (n[6] >= 1): return H # OO_
    return 0

def getRank(cfg):
    mul = [3, 7, 11, 15, 19] #mcoix
    #mul = [0, 1, 4, 9, 16]
    return (
    mul[4] * COUNT5[cfg][4] +
    mul[3] * COUNT5[cfg][3] +
    mul[2] * COUNT5[cfg][2] +
    mul[1] * COUNT5[cfg][1] +
    mul[0] * COUNT5[cfg][0])

STATUS4 = [[[[0 for a in range(10)] for b in range(10)] for c in range(10)] for d in range(10)]
RANK = []
for a in range(10):
    for b in range(10):
      for c in range(10):
        for d in range(10):
          STATUS4[a][b][c][d] = getStatus4(a, b, c, d)
for a in range(107):
    RANK.append(getRank(a))