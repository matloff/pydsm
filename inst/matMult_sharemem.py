from multiprocessing import shared_memory
from multiprocessing import Process
import numpy as np
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("nrowA", help="the number of rows of matrix A",
                        type=int, nargs='?', default=6)
parser.add_argument("ncolA", help="the number of cols of matrix A",
                        type=int, nargs='?', default=2)
parser.add_argument("numthreads", help="the number of parallel threads",
                        type=int, nargs='?', default=4)
parser.add_argument("-t", "--time", help="time the program", 
                        action="store_true")
args = parser.parse_args()



# Matrix multiplication; the product of matrix U and matrix V is computed;
# the result is stored in matrix W

# The idea is to break the rows of the matrix U into chunks, and have each
# thread/process work on one chunk

def mult(myid, myidxs, nrowA, ncolA, name_u, name_v, name_w):
    u_shm = shared_memory.SharedMemory(name=name_u)
    U = np.ndarray((nrowA, ncolA), dtype=np.int64, buffer=u_shm.buf)

    v_shm = shared_memory.SharedMemory(name=name_v)
    V = np.ndarray((ncolA, nrowA), dtype=np.int64, buffer=v_shm.buf)

    w_shm = shared_memory.SharedMemory(name=name_w)
    W = np.ndarray((nrowA, nrowA), dtype=np.int64, buffer=w_shm.buf)
    
    W[myidxs, ] = np.matmul(U[myidxs, ], V)

    u_shm.close()
    v_shm.close()
    w_shm.close()

def main(numthreads=None, nrowA=None, ncolA=None):
    if numthreads is None:
        numthreads = args.numthreads
    if nrowA is None:
        nrowA = args.nrowA
    if ncolA is None:
        ncolA = args.ncolA
    numElements = nrowA * ncolA

    a = (np.arange(numElements) + 1).reshape(nrowA, ncolA)
    shm_a = shared_memory.SharedMemory(create=True, size=a.nbytes)
    A = np.ndarray(a.shape, dtype=a.dtype, buffer=shm_a.buf)
    A[:] = a[:]

    b = (np.arange(numElements) + 1).reshape(ncolA, nrowA)
    shm_b = shared_memory.SharedMemory(create=True, size=b.nbytes)
    B = np.ndarray(b.shape, dtype=b.dtype, buffer=shm_b.buf)
    B[:] = b[:]

    c = (np.arange(nrowA * nrowA) + 1).reshape(nrowA, nrowA)
    shm_c = shared_memory.SharedMemory(create=True, size=c.nbytes)
    C = np.ndarray(c.shape, dtype=c.dtype, buffer=shm_c.buf)
    C[:] = c[:]

    p_list = [] # a list of subprocesses
    chunkSize = int(nrowA / numthreads)
    for id in range(numthreads):
        # id starts at zero, and ends at numThread - 1
        if id == numthreads - 1:
            idxs = list(range(nrowA)[id*chunkSize:])
        else:
            idxs = list(range(nrowA)[id*chunkSize:(id+1)*chunkSize])
        p_list.append(Process(target=mult, args=(id, idxs, nrowA, ncolA, 
                        shm_a.name, shm_b.name, shm_c.name)))

    # Run the parallel processes
    for p in p_list:
        p.start()
    
    for p in p_list:
        p.join()

    # print("Check out matrix C in main: {}" .format(C))
    shm_a.close()
    shm_a.unlink()
    shm_b.close()
    shm_b.unlink()
    shm_c.close()
    shm_c.unlink()

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    if args.time:
        print("This takes %.2f seconds" % (end - start))