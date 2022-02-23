#!/usr/bin/env python3 

from mpi import Mpi

class IMPI(Mpi): 
    def write_hostfile(self):
        with open(self.hostfile, 'w') as fh:
            for host in nodelist[0:self.nnodes]:
                fh.write(f'{host}:{self.ntasks}\n')
