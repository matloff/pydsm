from multiprocessing.pool import Pool
from multiprocessing import Process, Value
from multiprocessing.sharedctypes import Array
import multiprocessing
import os
import itertools
import random
from functools import partial
import numpy as np
import SharedArray as sa


# This Pydsm pacakge uses SharedArray and multiprocessing modules




# Override the get_task in multiprocessing to solve the load balancing issue
def _get_tasks_rand(func, it, chunksize):
    # Modify get tasks so that this
    # randomly assign threads to elements in the array
    random.shuffle(it)
    it = iter(it)
    while 1:
        x = tuple(itertools.islice(it, chunksize))
        if not x:
            return
        yield (func, x)




    
sense = Value("d", 1, lock = False)
counter = Value("d", 0, lock = False)


class Cluster:

    numThreads = None
    ownlock = multiprocessing.Lock()

    def __init__(self, numThreads = None):
        if numThreads == None:
            Cluster.numThreads = os.cpu_count()
        else:
            Cluster.numThreads = numThreads    

        self.mlock = multiprocessing.Lock()

        self.sharedList = []  # a list of shared variables

        self.resources = {}
        self.resources["lock"] = self.mlock
        self.resources["id"] = -1
        



    # Func parameter needs to follow this format with iterable on the end
    #               func(a, b, c, iterable+); + means one or more 
    #
    # If the func to be executed has more than one argument
    # then put all the arguments except the iterable(s) into a list of multiArgs
    # e.g.  multiArgs = [2, 4, 5]   # a = 2, b = 4, c = 5
    #
    # star is True when you have iterable of iterables
    # For example, you want to add two vectors A = [1, 2, 3], B = [4, 5, 6]
    # Then create a new list of lists C = [[1, 4], [2, 5], [3, 6]]
    # And pass the C to runPool as 'iter'
    # In this case, your func should be like this
    #               func(a, b, c, iter1, iter2)
    # so that at each iteration iter1 and iter2 will take the following values:
    # iter1 = 1;    iter2 = 4
    # iter1 = 2;    iter2 = 5
    # iter1 = 3;    iter2 = 6
    
    # def runPool(self, func, iter, multiArgs=None, star=False):
    #     chunkSize = int(len(iter) / self.numThreads)
    #     # Pool._get_tasks = _get_tasks_rand
    #     # Pool._map_async = _my_map_async

    #     # set up a cluster
    #     p = Pool(Cluster.numThreads)

    #     if multiArgs != None:
    #         for arg in multiArgs:
    #             func = partial(func, arg)

    #     if star == True:
    #         result = p.starmap(func, iter, chunkSize)
    #     else:
    #         result = p.map(func, iter, chunkSize)

    #     p.terminate()
    #     return result
        


    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        self.deleteShared()



    # paras need to be a tuple
    def runProcesses(self, func, paras = ()):

        p_list = []
        for id in range(self.numThreads):
            # id starts at zero, and ends at numThreads - 1
            self.resources = self.resources.copy() # a shallow copy of itself
            self.resources['id'] = id
            p_list.append(Process(target = func, args = (self.resources, ) + paras))
        
        for p in p_list:
            p.start()
        
        for p in p_list:
            p.join()
        
        
        # self.deleteShared()
   



    # Sense Reversal barrier
    @classmethod
    def barrier(cls):
        cls.ownlock.acquire()
        loc_sense = sense.value


        if counter.value == cls.numThreads - 1:  # last thread finished
            # Now every thread has reached the barrier
            # Reset everything
            counter.value = 0
            sense.value = 1 - sense.value
            cls.ownlock.release()
        else:
            counter.value += 1
            cls.ownlock.release()
            while loc_sense == sense.value:
                pass



    # create a shared array initialized to zeros
    # this shared array will be automatically deleted once processes finish
    def createShared(self, name, shape, dataType = int):
        # check name != 'id' and name != 'lock' and no repeated names
        try:
            if name in self.resources:
                self.deleteShared()
                raise KeyError("Name '" + str(name) + "' repetition:" +
                    "Please use a different name.")
        except KeyError as e:
            exit(str(e))
            
        sharedLoc = "shm://" + name
        sharedAry = sa.create(sharedLoc, shape, dataType)
        self.sharedList.append(sharedAry)
        self.resources[name] = sharedAry


        return sharedAry


    def deleteShared(self):
        for s in self.sharedList:
            sa.delete(s.base.name)
            del s



    # if length is not divisible by n, those extra numbers
    # will be placed in the list of the last process
    # For example, given a length of 10, and numThreads of 3
    # and after shuffling, ary = [1, 3, 4, 0, 2, 7, 9, 8, 6, 5]
    # Then, 
    # process with id 0 will get [1, 3, 4]
    # process with id 1 will get [0, 2, 7]
    # process with id 2 will get [9, 8, 6, 5]
    @classmethod
    def splitIndices(cls, length, id, random = True):
        n = cls.numThreads

        if id == 0:
            ary = sa.create("shm://spInd2048", length, int)
            ary[:] = np.arange(length)
            if random:
                np.random.shuffle(ary)
        
        cls.barrier()

        if id != 0:
            ary = sa.attach("spInd2048")


        # copy the computed numpy array to a new iterable
        # then delete the shared array
        # return a slice of iterable to each process

        chunkSize = int(length / n)
        result = list(ary)

        cls.barrier()

        if id == 0:
            sa.delete("spInd2048")
            del ary

        if id == n - 1:
            return result[id*chunkSize:]
        else:
            return result[id*chunkSize:(id+1)*chunkSize]

