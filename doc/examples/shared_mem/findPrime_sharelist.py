from multiprocessing import shared_memory
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import ShareableList
from multiprocessing import Process
from multiprocessing import Lock
import numpy as np
import math
import sys

# Execution format: python findPrime_sharemem.py range
# e.g. > python findPrime_sharemem.py 10000
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
def work(N, Prime, Nextbase, Numwork, myid, lock):
    
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
            return    





def main():
    nthreads = 4
    smm = SharedMemoryManager()
    smm.start()

    n = int(sys.argv[1])
    N = smm.ShareableList([n])
    
    prime = [0] * (n+1)
    Prime = smm.ShareableList(prime)

    nextbase = [0]
    Nextbase = smm.ShareableList(nextbase)

    numwork = [0] * nthreads
    Numwork = smm.ShareableList(numwork)

    # first mark all even numbers non-prime and the rest prime
    for i in range(3, n+1):
        if i % 2 == 0:
            Prime[i] = 0
        else:
            Prime[i] = 1

    Nextbase[0] = 3

    l = Lock()
    p0 = Process(target=work, args=(N, Prime, Nextbase, Numwork, 0, l))
    p1 = Process(target=work, args=(N, Prime, Nextbase, Numwork, 1, l))
    p2 = Process(target=work, args=(N, Prime, Nextbase, Numwork, 2, l))
    p3 = Process(target=work, args=(N, Prime, Nextbase, Numwork, 3, l))

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
    for i in range(3, n + 1):
        if Prime[i]:
            nprimes += 1

    print("A total of {} primes were found" .format(nprimes))
    smm.shutdown()





if __name__ == "__main__":
    main()