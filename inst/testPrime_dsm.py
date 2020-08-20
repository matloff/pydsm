import findPrime
import time

# Usage: python3 testPrime_dsm.py > result.txt


def main():
    numthreads = 10
    if findPrime.args.range is not None:
        myrange = findPrime.args.range
        start = time.time()
        findPrime.main(numthreads, myrange)
        end = time.time()
        print("{} {:.2f}" .format(myrange, end - start))
    else:
        for size in range(500000, 10000001, 500000):
            start = time.time()
            findPrime.main(numthreads, size)
            end = time.time()
            print("{} {:.2f}" .format(size, end - start))

if __name__ == "__main__":
    print("# File format: <Size> <Run time>")
    main()