#!/usr/bin/env python3 

class Mpi: 
    def __init__(self, nodelist=[], node=0, task=0, omp=0, hostfile='hostfile', verbose=0):
        self.nodelist = nodelist
        self.node     = node
        self.task     = task 
        self._omp     = omp
        self.hostfile = hostfile
        self.verbose  = verbose
        self.env      = {} 

        if omp: 
            self.env['OMP_NUM_THREADS'] = omp

    @property 
    def omp(self): 
        return self._omp 

    @omp.setter
    def omp(self, number_of_threads): 
        self._omp = number_of_threads 

        self.env['OMP_NUM_THREADS'] = number_of_threads 
    
    def write_hostfile(self):
        pass

    def mpirun(self): 
        pass
