# Pydsm

This package makes use of the SharedArray and the multiprocessing package 
and is still under development.

## Authors

Zhiyuan Guo (Daniel)

Norm Matloff


## Usage


### Start the processes

To create a cluster of 4 processes, one will do:

```
with pydsm.Cluster(4) as cluster:
    #Code
```

### Global array

In pydsm, all global arrays in shared memory are numpy arrays. 
To create a global array, one needs to first create a cluster and then call 
`createShared()`.

```
a = cluster.createShared(name = "A", shape = 10, dataType = int)
```

One provides the global array with an arbitrary but unique name, 
the shape (i.e., dimension) of the array, and the datatype (default is int).
The shape and datatype arguments will follow the same format as those typical 
numpy functions such as `numpy.zeros()`. The returned array is an array with
all elements initialized to zeros. All names of the global arrays should be 
unique.

### Run the processes
Then, `runProcesses(func)` is invoked 
to run the user's function in parallel.

```
cluster.runProcesses(foo)
```


### Parallelized function

The function `foo` implemented by the user will be executed 
by 4 processes simultaneously. 
**The first argument of a user's parallel function is mendatory.**
This mendatory parameter is a dictionary that contains **resource**
you may need for your parallel function.
It has references to the id of each process, the global array(s), and a lock.


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
lock = resource['lock']
```

Then, the users can apply the lock anywhere
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

## Example
Let's go through an example. 
In this example, two vectors are added up in parallel.

