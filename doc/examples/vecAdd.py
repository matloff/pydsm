import pydsm
import numpy as np


# Every function needs to have a resource in the beginning
def add(resource):
    myid = resource['id']
    lock = resource['lock'] # not used here
    A = resource['A']
    B = resource['B']
    C = resource['C']

    myidxs = pydsm.Cluster.splitIndices(10, myid, random=False)
    C[myidxs] = A[myidxs] + B[myidxs]

    # Below is just for illustrative purpose
    pydsm.Cluster.barrier()
    if(myid == 1):
        print("Check out vector C in processes: {}" .format(C))



def main():
    # a cluster of 4 processes
    with pydsm.Cluster(4) as cluster:
        A = cluster.createShared(name = "A", shape = 10, dataType = int)
        B = cluster.createShared("B", 10, int)
        C = cluster.createShared("C", 10, int)
        A[:] = range(10) 
        # A = array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        B[:] = range(10)
        B += 1 
        # B = array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Now run the processes
        cluster.runProcesses(add)
        
        # The barrier in 'add' is not necessary for this print statement
        print("Check out vector C in main: {}" .format(C))

if __name__ == "__main__":
    main()
