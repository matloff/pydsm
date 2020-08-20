from multiprocessing import Process
from multiprocessing import Lock
import os
import time
import random
import numpy as np
import SharedArray as sa
import fcntl
import errno
import signal
import sys



class Cluster:

    def __init__(self, numThread = None):
        if numThread == None:
           numThread = os.cpu_count()
        self.numThread = numThread
        
        # for sig in (signal.SIGABRT, signal.SIGINT, signal.SIGTERM):
        #     signal.signal(sig, self.terminate)
        
        self._initbarr(numThread)
        self.fd = os.open('FILE_LOCK', os.O_CREAT)

        self.sharedList = []  # a list of shared variables

        self.resources = {}
        self.resources["id"] = -1
        
        

    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()



    # paras need to be a tuple
    def runProcesses(self, func, paras = ()):

        p_list = []
        for id in range(self.numThread):
            # id starts at zero, and ends at numThread - 1
            self.resources = self.resources.copy() # a shallow copy of itself
            self.resources['id'] = id
            p_list.append(Process(target=func, args=(self.resources, )+paras))
        
        for p in p_list:
            p.start()
        
        for p in p_list:
            p.join()
        
        

    def _initbarr(self, numThread):
        nt = sa.create("shm://numThread2048", 1, int)
        nt[0] = numThread
        sense = sa.create("shm://sense2048", 1, int)
        sense[0] = 1
        counter = sa.create("shm://counter2048", 1, int)
        counter[0] = 0


    # Sense Reversal barrier
    @classmethod
    def barrier(cls):
        fd = cls.filelock()
        sense = sa.attach("shm://sense2048")
        counter = sa.attach("shm://counter2048")
        loc_sense = sense[0]
        nt = sa.attach("numThread2048")
        numThread = nt[0]

        if counter[0] == numThread - 1:  # last thread finished
            # Now every thread has reached the barrier
            # Reset everything
            counter[0] = 0
            sense[0] = 1 - sense[0]
            cls.fileunlock(fd)
        else:
            counter[0] += 1
            cls.fileunlock(fd)
            while loc_sense == sense[0]:
                pass



    # Create a shared array initialized to zeros
    # this shared array will be automatically deleted once processes finish
    def createShared(self, name, shape, dataType = int):
        # Check name != 'id' and name != 'lock' and no repeated names
        try:
            if name in self.resources:
                self.deleteShared()
                raise KeyError("Name '" + str(name) + "' repetition:" +
                    "Please use a different name.")
        except KeyError as e:
            exit(str(e))
            
        sharedLoc = "shm://" + name
        sharedAry = sa.create(sharedLoc, shape, dataType)
        self.sharedList.append(name)
        self.resources[name] = sharedAry

        return sharedAry

    # Create an instance of lock
    def createLock(self, name):
        # Check name != 'id' and name != 'lock' and no repeated names
        try:
            if name in self.resources:
                self.deleteShared()
                raise KeyError("Name '" + str(name) + "' repetition:" +
                    "Please use a different name.")
        except KeyError as e:
            exit(str(e))
        
        self.resources[name] = Lock()
    
    @classmethod
    def getShared(cls, name):
        return sa.attach(name)

    def deleteShared(self):
        for key in self.sharedList:
            sa.delete(key)
        sa.delete("shm://counter2048")
        sa.delete("shm://sense2048")
        sa.delete("shm://numThread2048")




    def terminate(self):
        os.close(self.fd)
        os.unlink("./FILE_LOCK")
        self.deleteShared()
        # In the case of abrupt termination of program, "shm://spInd2048" may
        # not be deleted. So need to delete it here
        try:
            sa.delete("spInd2048")
        except (IOError, OSError): # FileNotFoundError
            pass



    # If length is not divisible by n, those extra terms
    # will be placed in the list of the last process
    # For example, given a length of 10, and numThread of 3
    # and after shuffling, ary = [1, 3, 4, 0, 2, 7, 9, 8, 6, 5]
    # Then, 
    # process with id 0 will get [1, 3, 4]
    # process with id 1 will get [0, 2, 7]
    # process with id 2 will get [9, 8, 6, 5]
    @classmethod
    def splitIndices(cls, length, id, random = True):
        n = sa.attach("numThread2048")[0]

        if id == 0:
            ary = sa.create("shm://spInd2048", length, int)
            ary[:] = np.arange(length)
            if random:
                np.random.shuffle(ary)

        cls.barrier()

        if id != 0:
            ary = sa.attach("spInd2048")


        # Copy the computed numpy array to a new iterable
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


    @classmethod
    def filelock(cls):
        fd = os.open('FILE_LOCK', os.O_RDONLY)
        while True:
            try:
                # Acquire the lock
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (IOError, OSError) as e:
                # Raise if the error is not EAGAIN 
                # (i.e. Resource temporarily unavailable)
                if e.errno != errno.EAGAIN:
                    raise
            time.sleep(0.01) # Sleep to avoid busy waiting
        return fd
        

    @classmethod
    def fileunlock(cls, fd):
        # Release the lock
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
     