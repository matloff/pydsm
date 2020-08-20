from multiprocessing import shared_memory
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import ShareableList
from multiprocessing import Process
from multiprocessing import Lock
import numpy as np
import math
import sys
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("range", help="find prime numbers within the range",
                        type=int, nargs='?', default=None)
parser.add_argument("nthreads", help="the number of parallel threads",
                        type=int, nargs='?', default=None)
parser.add_argument("-t", "--time", help="time the program", 
                        action="store_true")

try:
    args = parser.parse_args()
except SystemExit as e: 
    if e.code == 2:
        parser.print_help()
    sys.exit(0)

# Usage: python findPrime.py <range> <nthreads>
# e.g. $ python findPrime.py 10000 4
# to find primes within 10000


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





def main(nthreads=None, myrange=None):
    if nthreads is None:
        nthreads = args.nthreads
    if myrange is None:
        myrange = args.range

    n = np.zeros((1,), dtype=int)
    n[0] = myrange
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

    # Create an instance of Lock
    l = Lock()
    
    p_list = []
    for id in range(nthreads):
        p_list.append(Process(target=work, args=(id, l, n, shm_n.name, prime, 
    shm_prime.name, nextbase, shm_nextbase.name, numwork, shm_numwork.name)))


    # Run the parallel processes
    for p in p_list:
        p.start()
    
    for p in p_list:
        p.join()

    # pos = 0
    # for num in Numwork:
    #     print("Process {} has done {} values of base" .format(pos, num))
    #     pos += 1

    # nprimes = 0
    # for i in range(3, n[0] + 1):
    #     if Prime[i]:
    #         nprimes += 1

    # print("A total of {} primes were found" .format(nprimes))

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
