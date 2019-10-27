import pydsm
import numpy as np
import sys
# import time

# Execution format: python vecAdd.py vec_length numthreads

# Every function needs to have a resource in the beginning
def add(resource, n):
    myid = resource['id']
    A = pydsm.Cluster.getShared("A")
    B = pydsm.Cluster.getShared("B")
    C = pydsm.Cluster.getShared("C")

    myidxs = pydsm.Cluster.splitIndices(n, myid, random=False)
    C[myidxs] = A[myidxs] + B[myidxs]

    # Below is just for illustrative purpose
    # pydsm.Cluster.barrier()
    # if myid == 1:
    #     print("Check out vector C in processes: {}" .format(C))



def main():
    # a cluster of 4 processes
    n = int(sys.argv[1])
    numthreads = int(sys.argv[2])
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
        
        print("Check out vector C in main: {}" .format(C))

if __name__ == "__main__":
    # start = time.time()
    main()
    # print('Runtime: {0:0.1f} seconds'.format(time.time() - start))
