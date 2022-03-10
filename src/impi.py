#!/usr/bin/env python3 

from mpi import Mpi

class IMPI(Mpi): 
    def write_hostfile(self):
        with open(self.hostfile, 'w') as fh:
            for host in self.nodelist[0:self.node]:
                fh.write(f'{host}:{self.task}\n')
    
    def mpirun(self): 
        cmd = [
            'mpirun', 
               f'-n {self.node * self.task}',
               f'-machinefile {self.hostfile}' ]

        # binding 
        if self.bind: 
            self.env['I_MPI_PIN_ORDER'] = self.bind 

        # mapping 
        if self.map: 
            self.env['I_MPI_PIN_DOMAIN'] = self.map 
            
        # iterate over env hash 
        for var in self.env: 
            cmd.append(f'-genv {var} {self.env[var]}') 

        return " ".join(cmd)
