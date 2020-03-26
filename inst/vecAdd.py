import pydsm
import numpy as np
import sys
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("length", help="the length of the vector A/B",
                        type=int, nargs='?', default=10)
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

# Usage: python vecAdd.py <vec_length> <numthreads>

# Vector addition; the sum of a vector A and a vector B is computed;
# the result is stored in the vector C



# Every function needs to have a resource in the beginning
def add(resource, n):
    myid = resource['id']
    A = pydsm.Cluster.getShared("A")
    B = pydsm.Cluster.getShared("B")
    C = pydsm.Cluster.getShared("C")

    myidxs = pydsm.Cluster.splitIndices(n, myid, random=True)
    C[myidxs] = A[myidxs] + B[myidxs]

    # Below is just for illustrative purpose
    pydsm.Cluster.barrier()
    if myid == 1:
        # In some versions of python, printing C directly may cause issues.
        # It is better to first convert the SharedArray into an numpy array
        # and then print it. So do np.array(C) before printing
        print("Check out vector C in processes: ", np.array(C))



def main():
    # a cluster of 4 processes
    n = args.length
    numthreads = args.numthreads
    with pydsm.Cluster(numthreads) as cluster:
        A = cluster.createShared(name = "A", shape = n, dataType = int)
        B = cluster.createShared("B", n, int)
        C = cluster.createShared("C", n, int)
        A[:] = np.arange(n) 
        # A := array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        B[:] = np.arange(n)
        B += 1 
        # B := array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Now run the processes
        cluster.runProcesses(add, paras=(n,))
        print("Check out vector C in main: ", np.array(C))

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    if args.time:
        print()
        print("This takes %.2f seconds" % (end - start))
