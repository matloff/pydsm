from multiprocessing import shared_memory
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import ShareableList
from multiprocessing import Process
from multiprocessing import Lock
import numpy as np
import math
import sys
# import time

# Execution format: python findPrime_sharemem.py range numthreads
# e.g. > python findPrime_sharemem.py 10000 4
# to find primes within 10000 using 4 processes


# Shared variables:
#   nthreads;    number of threads
#   n;           range
#   prime[];     in the end, prime[i] = 1 if it is prime
#   nextbase;    next sieve multiplier to be used
#   numwork;     total work done by this thread




# cross out all odd multiples of k
def crossout(k, n, prime):
    i = 3
    while i * k <= n:
        prime[i * k] = 0
        i += 2
    


# each thread's work
def work(myid, lock, n, name_n, prime, name_prime, nextbase, name_nextbase, 
            numwork, name_numwork):   
    n_shm = shared_memory.SharedMemory(name=name_n)
    N = np.ndarray(n.shape, dtype=n.dtype, buffer=n_shm.buf)

    prime_shm = shared_memory.SharedMemory(name=name_prime)
    Prime = np.ndarray(prime.shape, dtype=prime.dtype, buffer=prime_shm.buf)

    nextbase_shm = shared_memory.SharedMemory(name=name_nextbase)
    Nextbase = np.ndarray(nextbase.shape, dtype=nextbase.dtype, 
                            buffer=nextbase_shm.buf)

    numwork_shm = shared_memory.SharedMemory(name=name_numwork)
    Numwork = np.ndarray(numwork.shape, dtype=numwork.dtype, 
                            buffer=numwork_shm.buf)

    Numwork[myid] = 0 # total work done by this thread
    lim = int(math.sqrt(N[0])) # don't check multipliers greater than sqrt(N)

    while 1:
        lock.acquire()
        base = Nextbase[0]
        Nextbase[0] += 2
        lock.release()

        if base <= lim:
            if Prime[base]:
                crossout(base, N[0], Prime)
                Numwork[myid] += 1
        else:
            n_shm.close()
            prime_shm.close()
            numwork_shm.close()
            numwork_shm.close()
            return    





def main():
    nthreads = int(sys.argv[2])

    n = np.zeros((1,), dtype=int)
    n[0] = int(sys.argv[1])
    shm_n = shared_memory.SharedMemory(create=True, size=n.nbytes)
    N = np.ndarray(n.shape, dtype=n.dtype, buffer=shm_n.buf)
    N[:] = n[:]
    
    prime = np.zeros((n[0]+1, ), dtype=int)
    shm_prime = shared_memory.SharedMemory(create=True, size=prime.nbytes)
    Prime = np.ndarray(prime.shape, dtype=prime.dtype, buffer=shm_prime.buf)
    Prime[:] = prime[:]

    nextbase = np.zeros((1, ), dtype=int)
    shm_nextbase = shared_memory.SharedMemory(create=True, size=nextbase.nbytes)
    Nextbase = np.ndarray(nextbase.shape, dtype=nextbase.dtype, 
                            buffer=shm_nextbase.buf)
    Nextbase[:] = nextbase[:]

    numwork = np.zeros((nthreads, ), dtype=int)
    shm_numwork = shared_memory.SharedMemory(create=True, size=numwork.nbytes)
    Numwork = np.ndarray(numwork.shape, dtype=numwork.dtype, 
                            buffer=shm_numwork.buf)
    Numwork[:] = numwork[:]

    # first mark all even numbers non-prime and the rest prime
    for i in range(3, n[0]+1):
        if i % 2 == 0:
            Prime[i] = 0
        else:
            Prime[i] = 1

    Nextbase[0] = 3

    l = Lock()
    p0 = Process(target=work, args=(0, l, n, shm_n.name, prime, shm_prime.name, 
                    nextbase, shm_nextbase.name, numwork, shm_numwork.name))
    p1 = Process(target=work, args=(1, l, n, shm_n.name, prime, shm_prime.name, 
                    nextbase, shm_nextbase.name, numwork, shm_numwork.name))
    p2 = Process(target=work, args=(2, l, n, shm_n.name, prime, shm_prime.name, 
                    nextbase, shm_nextbase.name, numwork, shm_numwork.name))
    p3 = Process(target=work, args=(3, l, n, shm_n.name, prime, shm_prime.name, 
                    nextbase, shm_nextbase.name, numwork, shm_numwork.name))                 

    p0.start()
    p1.start()
    p2.start()
    p3.start()

    p0.join()
    p1.join()
    p2.join()
    p3.join()

    pos = 0
    for num in Numwork:
        print("Process {} has done {} values of base" .format(pos, num))
        pos += 1

    nprimes = 1
    for i in range(3, n[0] + 1):
        if Prime[i]:
            nprimes += 1

    print("A total of {} primes were found" .format(nprimes))

    shm_n.close()
    shm_n.unlink()
    shm_prime.close()
    shm_prime.unlink()
    shm_nextbase.close()
    shm_nextbase.unlink()
    shm_numwork.close()
    shm_numwork.unlink()






if __name__ == "__main__":
    # start = time.time()
    main()
    # print('Runtime: {0:0.1f} seconds'.format(time.time() - start))