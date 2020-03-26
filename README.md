# Pydsm

While the multi-thread parallel performance is limited in Python because of 
the Global Interpreter Lock, Pydsm provided parallel computation that
truly shares memory between processes in a distributed way.


## Requirements

* SharedArray
* numpy
* POSIX (Linux, variants of Unix including macOS, etc.)
* Python 2 is supported, but Python 3 is recommended

You can install py-dsm via the `pip` command:

```
pip install py-dsm
```

## Authors

Zhiyuan Guo

Norm Matloff


## Usage


### Start the processes

To create a cluster instance of 4 worker processes, one will do:

```
with pydsm.Cluster(4) as cluster:
```

### Global array

In pydsm, all global arrays in shared memory are numpy arrays. 
To create a global array, one needs to first create a cluster instance 
and then call `createShared()`.

```
a = cluster.createShared(name = "A", shape = 10, dataType = int)
```

The user needs to provide the global array with an arbitrary but unique name, 
the shape (i.e., dimension) of the array, and the datatype (default is int).
The shape and datatype arguments will follow the same format as those typical 
numpy functions such as `numpy.zeros()`. The returned array is an array with
all elements initialized to zeros. All names of the global arrays should be 
unique.

### Run the processes
Then, `runProcesses(func, paras)` is invoked 
to run the user's function in parallel. `func` is the name of the
user-defined parallel function. `paras`, defaulted to an empty tuple, 
is a tuple consisting of parameters passed in to the user's function.
Each worker process will get a copy of those parameters in `paras`.


```
cluster.runProcesses(foo)
```


### Parallelized function

The function `foo` implemented by the user will be executed 
by 4 processes simultaneously. 
**The first argument of a user's parallel function is mendatory.**
This mendatory parameter is a dictionary that contains **resource**
you may need for your parallel function.
The resource has references to the id of each process, 
the global array(s), and a lock.


```
def foo(res, ...):
	# res is the resource
	# ... means any extra parameters you may need
	# Code
```



### Locks and barriers

To use a lock in the parallelized function,
the lock first needs to be retrieved from
'resource' (the first parameter).

```
lock = res['lock']
```

Then, the user can apply the lock anywhere
they want in the function.

```
lock.apply()
# Critical section
lock.release()
```

The barrier is invoked in the following way.

```
pydsm.Cluster.barrier()
```

### Split the tasks

The user can invoke `splitIndices(n, id, random=True)` inside the user's
parallel function to distribute the tasks. 
`splitIndices` will return to each worker process a list of indices (numbers).

Say we want to compute Y = AX in parallel by splitting the rows of A into
chunks.  We have 100 rows in A and 10 processors. We can let each
process take 10 rows. 

```
myid = resource['id']
myidxs = pydsm.Cluster.splitIndices(100, myid, random=True)
Y[myidxs, ] = np.matmul(A[myidxs,], X)
```

In this scenario, `n` will be 100.
It is recommended to set `random` to True to 
split the rows randomly and thus achieve better load balancing.
Otherwise, process 0 will take the first ten rows, process 1 will take the
second ten rows, and so on, which may result in inefficient load balancing.



## Example
This is an embarrassingly parallel example that illustrates the usage
of the pydsm. Two vectors are added in parallel.
The idea is to break A and B into chunks, and have each worker process
work on one chunk.
The complete source code is in `doc/examples/vecAdd.py`.

A and B are the two vectors to be added.
The result will be stored in C, as the computation is carried out.
Thus, all of them need to be shared variables.
They are set up in the following way.


```
with pydsm.Cluster(4) as cluster:
	A = cluster.createShared(name = "A", shape = 10, dataType = int)
	B = cluster.createShared("B", 10, int)
	C = cluster.createShared("C", 10, int)
```

Now A and B are shared arrays backed by numpy.
We can use and treat them the same way we do to numpy arrays.

```
	A[:] = np.arange(10) 
	# A is now "array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])"
	B[:] = np.arange(10)
	B += 1 
	# B is now "array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])"
```

We then call `runProcesses()`, with the first parameter being
the name of the parallel function, which we will define later.
The second parameter is a tuple of parameters used by parallel function.
Here we pass in 10 as the length of each vector.

```
	cluster.runProcesses(add, paras=(10,))
```

Next, we define the parallel function `add`.

```
def add(resource, n):
    myid = resource['id']
    A = pydsm.Cluster.getShared("A")
    B = pydsm.Cluster.getShared("B")
    C = pydsm.Cluster.getShared("C")

    myidxs = pydsm.Cluster.splitIndices(n, myid, random=False)
    C[myidxs] = A[myidxs] + B[myidxs]
```

Each worker process first obtains an unique id, and then
attaches A, B, and C to the corresponding shared variable.
`splitIndices()` is then called to give each worker a list of indices.
Each worker will then compute elements in the array corresponding to those
indices.
Note that C is a shared variable, so `add` does not need to return C.

For illustrative purpose of the usage of barriers,
we can have the following code at the end of `add`.
The process 1 will print out C after the computation is done.

```
# Below is just for illustrative purpose
pydsm.Cluster.barrier()
if myid == 1:
	# In some versions of python, printing C directly may cause issues.
	# It is better to first convert the SharedArray into an numpy array
	# and then print it. So do np.array(C) before printing
	print("Check out vector C in processes: ", np.array(C))
	# C will be '[ 1  3  5  7  9 11 13 15 17 19]'
```


## More examples

For more sample applications using pydsm such as finding prime numbers and
matrix multiplication, they are under the directory `inst/`.

## Notes

If your program is terminated abnormally, py-dsm may not compeletely delete
your shared variables. When you run your program next time, you may encounter
the following error message because your program is trying to create a
shared variable that is still alive.

```
# You are trying to create a shared variable named 'A', but there is
# already a shared var named 'A'. 
FileExistsError: [Errno 17] File exists: 'shm://A'
```

In this scenario, you need to delete the shared variable yourself in the Python
interpreter.

```
>>> import SharedArray as sa
>>> sa.delete("A")
```


