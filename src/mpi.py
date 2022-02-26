#!/usr/bin/env python3 

class Mpi: 
    def __init__(self, nodelist=[], nnodes=1, ntasks=1, omp=1, hostfile='hostfile', verbose=0): 
        self.nodelist = nodelist
        self.nnodes   = nnodes
        self.ntasks   = ntasks 
        self._omp     = omp
        self.hostfile = hostfile
        self.verbose  = verbose
    
    def write_hostfile(self):
        pass

    def mpirun_cmd(self): 
        pass
