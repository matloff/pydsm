import numpy as np
from multiprocessing import shared_memory
from multiprocessing import Process
import sys
# import time

# Execution format: python vecAdd_sharemem.py vec_length numthreads


def add(myid, myidxs, n, name_a, name_b, name_c):
    a_shm = shared_memory.SharedMemory(name=name_a)
    A = np.ndarray(n, dtype=np.int64, buffer=a_shm.buf)

    b_shm = shared_memory.SharedMemory(name=name_b)
    B = np.ndarray(n, dtype=np.int64, buffer=b_shm.buf)

    c_shm = shared_memory.SharedMemory(name=name_c)
    C = np.ndarray(n, dtype=np.int64, buffer=c_shm.buf)

    C[myidxs] = A[myidxs] + B[myidxs]
    # if myid == 1:
    #     # needs a barrier above
    #     print("Check out vector C in processes: {}" .format(C))
    
    a_shm.close()
    b_shm.close()
    c_shm.close()




def main():
    n = int(sys.argv[1])
    numThread = int(sys.argv[2])
    
    a = np.arange(n)
    shm_a = shared_memory.SharedMemory(create=True, size=a.nbytes)
    A = np.ndarray(a.shape, dtype=a.dtype, buffer=shm_a.buf)
    A[:] = a[:]

    b = np.arange(n)
    shm_b = shared_memory.SharedMemory(create=True, size=b.nbytes)
    B = np.ndarray(b.shape, dtype=b.dtype, buffer=shm_b.buf)
    B[:] = b[:]

    c = np.arange(n)
    shm_c = shared_memory.SharedMemory(create=True, size=c.nbytes)
    C = np.ndarray(c.shape, dtype=c.dtype, buffer=shm_c.buf)
    # C is populated with all zeros


    p_list = []
    chunkSize = int(n / numThread)
    for id in range(numThread):
        # id starts at zero, and ends at numThread - 1
        if id == numThread - 1:
            idxs = list(range(n)[id*chunkSize:])
        else:
            idxs = list(range(n)[id*chunkSize:(id+1)*chunkSize])
        p_list.append(Process(target=add, args=(id, idxs, n, shm_a.name, 
                        shm_b.name, shm_c.name)))
    
    for p in p_list:
        p.start()
    
    for p in p_list:
        p.join()

    print("Check out vector C in main: {}" .format(C))

    shm_a.close()
    shm_a.unlink()
    shm_b.close()
    shm_b.unlink()
    shm_c.close()
    shm_c.unlink()

if __name__ == "__main__":
    # start = time.time()
    main()
    # print('Runtime: {0:0.1f} seconds'.format(time.time() - start))
