import pydsm
import numpy as np
from scipy.spatial import distance


# Find distances between all pairs of rows in matrix A and B in parallel.
# The result should be the same as 'scipy.spatial.distance.cdist(A, B)'
#
#
# >>> a
# array([[1, 2],
#        [3, 4],
#        [5, 6],
#        [7, 8]])
#
# >>> b
# array([[1, 1],
#        [1, 1]])
#
# >>> distance.cdist(a,b)
# array([[1.        , 1.        ],
#        [3.60555128, 3.60555128],
#        [6.40312424, 6.40312424],
#        [9.21954446, 9.21954446]])




def work(res):
    myid = res['id']
    A = res['A']
    B = res['B']
    C = res['C']

    myindxs = pydsm.Cluster.splitIndices(4, myid, random=False)
    C[myindxs] = distance.cdist(A[myindxs], B)




def main():
    nthreads = 2
    with pydsm.Cluster(nthreads) as p:
        A = p.createShared("A", shape=(4,2), dataType=int)
        # populate 'a' with 1:8, and then resize it to a 4 by 2 matrix
        a = np.arange(1,9).reshape(4, 2)  
        A[:] = a # change all values in A to a's
        
        B = p.createShared("B", shape=(2,2), dataType=int)
        b = np.ones(shape=(2,2), dtype=int)
        B[:] = b # B is now a 2 by 2 matrix all filled with ones

        result = p.createShared("C", shape=(4,2), dataType=float)
        p.runProcesses(work)

        print("Sequential result: {}" .format(distance.cdist(a,b)))
        print("Parallel result: {}" . format(result))






if __name__ == "__main__":
    main()