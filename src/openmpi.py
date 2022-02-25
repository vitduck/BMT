#!/usr/bin/env python3 

from mpi import Mpi

class OpenMPI(Mpi): 
    def __init__(self, ucx=['dc','sm','self'], bind=None, map=None, hca=[], sharp=0, **kwargs): 
        super().__init__(**kwargs) 

        self.ucx   = ucx 
        self.bind  = bind 
        self.map   = map
        self.hca   = hca
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
            mpirun.append('-mca coll_hcoll_enable 1')
            mpirun.append(f'-x HCOLL_ENABLE_SHARP={self.sharp}') 
            mpirun.append(f'-x SHARP_COLL_ENABLE_SAT=1')
            mpirun.append(f'-x SHARP_COLL_LOG_LEVEL=3')

        # ucx is somewhat buggy
        if self.ucx: 
            mpirun.append(f'--mca pml ucx')
            mpirun.append(f'-x UCX_TLS={",".join(self.ucx)}')

        if self.hca: 
            mpirun.append(f'-x UCX_NET_DEVICES={",".join(self.hca)}')

        return " ".join(mpirun)
