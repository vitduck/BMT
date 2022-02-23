#!/usr/bin/env python3 

from mpi import Mpi

class OpenMPI(Mpi): 
    def __init__(self, ucx='', bind='', map='', sharp=0, **kwargs): 
        super().__init__(**kwargs) 

        self.ucx   = ucx 
        self.bind  = bind 
        self.map   = map
        self.sharp = sharp

    def write_hostfile(self):
        with open(self.hostfile, 'w') as fh:
            for host in self.nodelist[0:self.nnodes]:
                fh.write(f'{host} slots={self.ntasks}\n')

    def mpirun_cmd(self): 
        nprocs = self.nnodes * self.ntasks 

        mpirun = [
            'mpirun', 
            '--allow-run-as-root', 
           f'--np {nprocs}',
           f'--hostfile {self.hostfile}' ]

        if self.bind: 
            mpirun.append(f'--bind-to {self.bind}')

        if self.map: 
            mpirun.append(f'--map-by {self.map}') 

        if self.verbose: 
            mpirun.append(f'--report-bindings')

        if self.sharp:
            mpirun.append(f'-x HCOLL_ENABLE_SHARP={self.sharp}') 
            mpirun.append(f'-x SHARP_COLL_ENABLE_SAT=1')

        return " ".join(mpirun)
