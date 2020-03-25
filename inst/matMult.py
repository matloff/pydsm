import pydsm
import numpy as np
import sys
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("nrowU", help="the number of rows of matrix U",
                        type=int, nargs='?', default=6)
parser.add_argument("ncolU", help="the number of cols of matrix U",
                        type=int, nargs='?', default=2)
parser.add_argument("numthreads", help="the number of parallel threads",
                        type=int, nargs='?', default=4)
parser.add_argument("-t", "--time", help="time the program", 
                        action="store_true")

try:
    args = parser.parse_args()
except SystemExit as e: 
    if e.code == 2:
        parser.print_help()
    sys.exit(0)



# Matrix multiplication; the product of matrix U and matrix V is computed;
# the result is stored in matrix W

# The idea is to break the rows of the matrix U into chunks, and have each
# thread/process work on one chunk

def mult(res, n):
    myid = res['id']
    U = pydsm.Cluster.getShared("U")
    V = pydsm.Cluster.getShared("V")
    W = pydsm.Cluster.getShared("W")

    myidxs = pydsm.Cluster.splitIndices(n, myid, random=False)
    W[myidxs, ] = np.matmul(U[myidxs, ], V)




def main():
    numthreads = args.numthreads
    nrowU = args.nrowU
    ncolU = args.ncolU
    numElements = nrowU * ncolU
    with pydsm.Cluster(numthreads) as cluster:
        u = cluster.createShared(name = "U", shape=(nrowU, ncolU), dataType=int)
        v = cluster.createShared("V", (ncolU, nrowU), int)
        w = cluster.createShared("W", (nrowU, nrowU), int)

        u[:] = (np.arange(numElements) + 1).reshape(nrowU, ncolU)
        # if nrowU is 6 and ncol is 2, then u will be
        # array([[ 1,  2],
        #        [ 3,  4],
        #        [ 5,  6],
        #        [ 7,  8],
        #        [ 9, 10],
        #        [11, 12]])


        v[:] = (np.arange(numElements) + 1).reshape(ncolU, nrowU)
        # if nrowU is 6 and ncol is 2, then v will be
        # array([[ 1,  2,  3,  4,  5,  6],
        #        [ 7,  8,  9, 10, 11, 12]])


        # Now run the processes
        cluster.runProcesses(mult, paras=(nrowU,))
        
    print("Check out matrix w in main: {}" .format(w))



if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    if args.time:
        print("This takes %.2f seconds" % (end - start))
