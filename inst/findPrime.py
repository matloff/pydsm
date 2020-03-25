import pydsm
import math
import sys
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("range", help="find prime numbers within the range",
                        type=int, nargs='?', default=10000)
parser.add_argument("nthreads", help="the number of parallel threads",
                        type=int, nargs='?', default=4)
parser.add_argument("-t", "--time", help="time the program", 
                        action="store_true")

try:
    args = parser.parse_args()
except SystemExit as e: 
    if e.code == 2:
        parser.print_help()
    sys.exit(0)


# Usage: python findPrime.py <range> <nthreads>
# e.g. $ python findPrime.py 10000
# to find primes within 10000


# Shared variables:
#   nthreads;    number of threads
#   n;           range
#   prime[];     in the end, prime[i] = 1 if it is prime
#   nextbase;    next sieve multiplier to be used




# cross out all odd multiples of k
def crossout(k, n, prime):
    i = 3
    while i * k <= n:
        prime[i * k] = 0
        i += 2
    


# each thread's work
def work(resource):
    # get the pointers/references to shared vars
    N = pydsm.Cluster.getShared('N')
    prime = pydsm.Cluster.getShared('prime')
    nextBase = pydsm.Cluster.getShared('nextBase')
    numWork = pydsm.Cluster.getShared('numWork')
    
    # get the unique id of each thread
    myid = resource['id']
    # get the same lock object
    lock = resource['lock']

    numWork[myid] = 0 # total work done by this thread
    lim = int(math.sqrt(N[0])) # don't check multipliers greater than sqrt(N)

    while 1:
        lock.acquire()
        base = nextBase[0]
        nextBase[0] += 2
        lock.release()

        if base <= lim:
            if prime[base]:
                crossout(base, N[0], prime)
                numWork[myid] += 1
        else:
            return    





def main():
    nthreads = args.nthreads
    myrange = args.range
    with pydsm.Cluster(nthreads) as p:

        N = p.createShared("N", 1, int)
        N[0] = myrange
        prime = p.createShared("prime", N[0] + 1, int)
        nextBase = p.createShared("nextBase", 1, int)
        numWork = p.createShared("numWork", nthreads, int)

        
        # first mark all even numbers non-prime and the rest prime
        for i in range(3, N[0] + 1):
            if i % 2 == 0:
                prime[i] = 0
            else:
                prime[i] = 1
        
        nextBase[0] = 3

        p.runProcesses(work)

        pos = 0
        for num in numWork:
            print("Process {} has done {} values of base" .format(pos, num))
            pos += 1

        nprimes = 1
        for i in range(3, N[0] + 1):
            if prime[i]:
                nprimes += 1
        
        print("A total of {} primes were found" .format(nprimes))





if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    if args.time:
        print()
        print("This takes %.2f seconds" % (end - start))
