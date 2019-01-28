#------------------------------------------------------------------------------------#
# queens.py: N-Queens benchmark                                                      #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

from argparse import ArgumentParser
import cobra
from sys import getrecursionlimit, setrecursionlimit

# N-Queens benchmark: find all solutions (or the total number) to the problem of placing n chess queens on an n by n chessboard so that no two queens are on the same row, column or diagonal (since Bezzel 1848).

#python -O -m benchs.queens 10 -f 1 -v 2 # for first solution
#python -O -m benchs.queens 8 -b # for all solutions

def queens(n):
    q=[cobra.Var('Q'+str(i+1), 1, n) for i in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            cobra.nequxyc(q[i], q[j], 0)
            cobra.nequxyc(q[i], q[j], j-i)
            cobra.nequxyc(q[j], q[i], j-i)

def main(n, search=2, root=True, verbose=0, varChoice=0, timeout=None):
    cobra.Logprint(verbose)
    setrecursionlimit(2400)

    queens(n)
    opt=cobra.Optimizer(None, search=search, root=root, varChoice=varChoice) # Enumeration on variables
    varsol, objname, objvalue, backtracks, proof, duration, completion, nbsol = opt.optimize()
    if nbsol == 1: print("solution:", varsol)
    print("number of solutions =", nbsol)
    print("backtracks=", backtracks)
    print("runtime =", duration)

if __name__ == "__main__":
    parser = ArgumentParser(description='N-Queens Benchmark')
    parser.add_argument("N", help="Size of the chessboard", type=int)
    parser.add_argument("-s", "--search", type=int, choices=[2, 3], help="2=enumerate on variables, 3=dichotomic search", default=2)
    parser.add_argument("-b", "--branchANDbound", help="-b=Branch and Bound, default=Root", action='store_true', default=False) # for all solutions
    parser.add_argument("-v", "--verbose", type=int, choices=[0, 2, 4, 5], help="0=quiet, 2=search progression, 4=constraint propagation, 5=trailing", default=0)
    parser.add_argument("-f", "--varChoice", type=int, choices=[0, 1], help="0=no reordering, 1=minimum domain first", default=0)
    parser.add_argument("-t", "--timeout", help="Budget time in seconds (or fractions thereof)", type=float, default=None)
    args = parser.parse_args()
    main(args.N, search=args.search, root=not(args.branchANDbound), verbose=args.verbose, varChoice=args.varChoice, timeout=args.timeout)

 #   Board Size:       Number of Solutions to              Number of irregular         Number of semi-regular        Number of regular
 #   (length of one        N queens problem:                    Solutions:                  Solutions:                  Solutions:                                        
 #    side of N x N                                    
 #    chessboard)
 #
 #     1                                  1                        n/a                          n/a                         n/a
 #     2                                  0                         0                            0                           0
 #     3                                  0                         0                            0                           0
 #     4                                  2                         0                            0                           1
 #     5                                 10                         1                            0                           1
 #     6                                  4                         0                            1                           0
 #     7                                 40                         4                            2                           0
 #     8                                 92                        11                            1                           0
 #     9                                352                        42                            4                           0
 #    10                                724                        89                            3                           0
 #    11                               2680                       329                           12                           0
 #    12                              14200                      1765                           18                           4
 #    13                              73712                      9197                           32                           4
 #    14                             365596                     45647                          105                           0
 #    15                            2279184                    284743                          310                           0
 #    16                           14772512                   1846189                          734                          32
 #    17                           95815104                  11975869                         2006                          64
 #    18                          666090624                  83259065                         4526                           0
 #    19                         4968057848                 621001708                        11046                           0
 #    20                        39029188884                4878630533                        36035                         240
 #    21                       314666222712               39333230881                        93740                         352
 #    22                      2691008701644              336375931369                       312673                           0
 #    23                     24233937684440             3029241762900                       895310                           0
 #    24                    227514171973736            28439270037332                      2917938                        1664
 #    25                   2207893435808352           275986675209470                      8532332                        1632
 #    26                  22317699616364044          2789712437580722                     28929567                           0
 #    27                 234907967154122528         29363495854214938                     80100756                           0

#python -O -m benchs.queens 11 -b
#number of solutions = 2680
#backtracks= 29947
#runtime = 0:0:31.5222

#python -O -m benchs.queens 11 -b -f 1
#number of solutions = 2680
#backtracks= 28405
#runtime = 0:0:33.8839

#python -O -m benchs.queens 12 -b
#number of solutions = 14200
#backtracks= 146101
#runtime = 0:12:51.5221

#python -O -m benchs.queens 30 -f 1 -v 2
#-Enumeration on variables
#   -minimum domain fisrt variable order
#solution: {'Q1': 1, 'Q2': 3, 'Q3': 5, 'Q4': 7, 'Q5': 12, 'Q6': 10, 'Q7': 20, 'Q8': 16, 'Q9': 14, 'Q10': 24, 'Q11': 27, 'Q12': 9, 'Q13': 28, 'Q14': 25, 'Q15': 11, 'Q16': 26, 'Q17': 23, 'Q18': 30, 'Q19': 18, 'Q20': 29, 'Q21': 15, 'Q22': 13, 'Q23': 21, 'Q24': 19, 'Q25': 8, 'Q26': 6, 'Q27': 4, 'Q28': 2, 'Q29': 17, 'Q30': 22}
#number of solutions = 1
#backtracks= 10490
#runtime = 0:0:57.3197
