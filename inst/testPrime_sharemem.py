import findPrime_sharemem
import time

# Usage: python3 testPrime_sharemem.py > result.txt


def main():
    numthreads = 10
    if findPrime_sharemem.args.range is not None:
        myrange = findPrime_sharemem.args.range
        start = time.time()
        findPrime_sharemem.main(numthreads, myrange)
        end = time.time()
        print("{} {:.2f}" .format(myrange, end - start))
    else:
        for size in range(500000, 10000001, 500000):
            start = time.time()
            findPrime_sharemem.main(numthreads, size)
            end = time.time()
            print("{} {:.2f}" .format(size, end - start))


if __name__ == "__main__":
    print("# File format: <Size> <Run time>")
    main()