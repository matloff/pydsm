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
    # so that iter1 may take value 1, 2, 3 and iter2 may take value 4, 5, 6
    def runPool(self, func, iter, multiArgs=None, star=False):
        chunkSize = int(len(iter) / self.numThreads)
        Pool._get_tasks = _get_tasks_rand

        # set up a cluster
        p = Pool(self.numThreads)

        if multiArgs != None:
            for arg in multiArgs:
                func = partial(func, arg)

        if star == True:
            result = p.starmap(func, iter, chunkSize)
        else:
            result = p.map(func, iter, chunkSize)

     #   p.terminate()
        return result
        

    # paras need to be a tuple
    def runProcesses(self, func, paras = ()):

        p_list = []
        for id in range(self.numThreads):
            self.resources = self.resources.copy() # a shallow copy of itself
            self.resources['id'] = id
            p_list.append(Process(target = func, args = (self.resources, ) + paras))
        
        for p in p_list:
            p.start()
        
        for p in p_list:
            p.join()
        
        
        self.deleteShared()
   



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
    def createShared(self, name, shape, dataType):
        # check name != 'id' and name != 'lock' and no repeated names
        try:
            if name in self.resources:
                self.deleteShared()
                raise KeyError("Name '" + str(name) + "' repetition:" +
                    "Please use a different name.")
        except KeyError as e:
            exit(str(e))
            
        sharedLoc = "shm://" + name
        sharedAry = sa.create(sharedLoc, shape, dtype = int)
        self.sharedList.append(sharedAry)
        self.resources[name] = sharedAry


        return sharedAry


    def deleteShared(self):
        for s in self.sharedList:
            sa.delete(s.base.name)
            del s