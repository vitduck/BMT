#!/usr/bin/env python3 

from mpi import Mpi

class tMPI(Mpi): 
    def run(self): 
        cmd = [] 

        # numaclt 
        if self.numa and self.gpu > 0: 
            cmd += self.numactl() 

        return " ".join(cmd)
