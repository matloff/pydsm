# Pydsm

This package makes use of the 
SharedArray and the multiprocessing package and is still under development.

## Authors

Zhiyuan Guo (Daniel)

Norm Matloff


## Usage

To create a cluster of 4 processes, one will do:

```
with pydsm.Cluster(4) as cluster:
    #Code
```

In pydsm, all global arrays in shared memory are numpy arrays. To create a global array, one needs to first create a cluster and then call `createShared()`.

```
a = cluster.createShared(name = "A", shape = 10, dataType = int)
```

One provides the global array with an arbitrary but unique name, the shape (i.e., dimension) of the array, and the datatype (default is int). The shape and datatype arguments will follow the same format as those typical numpy functions such as `numpy.zeros()`. The returned array is an array with all elements initialized to zeros. All names of the global arrays should be unique.


Then, `runProcesses(func)` is invoked 
to run the user's function in parallel.

```
cluster.runProcesses(foo)
```

The function `foo` implemented by the user will
be executed by 4 processes simultaneously.
**Note that all user's parallel functions 
(foo, etc.) needs to have at least one parameter**

