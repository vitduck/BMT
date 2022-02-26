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
        self.mca   = { }
        self.env   = { 
            'OMP_NUM_THREADS' : self._omp }  

    @property 
    def omp(self): 
        return self._omp 

    @omp.setter 
    def omp(self, number_of_threads): 
        self._omp = number_of_threads 
        self.env['OMP_NUM_THREADS'] = number_of_threads 

    def write_hostfile(self):
        with open(self.hostfile, 'w') as fh:
            for host in self.nodelist[0:self.nnodes]:
                fh.write(f'{host} slots={self.ntasks}\n')

    def mpirun(self): 
        mpirun_cmd = [
            'mpirun', 
                '--allow-run-as-root', 
               f'--np {self.nnodes * self.ntasks}', 
               f'--hostfile {self.hostfile}' ]

        if self.bind: 
            mpirun_cmd.append(f'--bind-to {self.bind}')

        # process mapping 
        if self.map: 
            mpirun_cmd.append(f'--map-by {self.map}') 

        # show report to stderr
        if self.verbose: 
            mpirun_cmd.append(f'--report-bindings')

        # sharp
        if self.sharp:
            self.mca['coll_hcoll_enable'    ]  = 1 
            self.env['HCOLL_ENABLE_SHARP'   ]  = self.sharp 
            self.env['SHARP_COLL_ENABLE_SAT']  = 1
            self.env['SHARP_COLL_LOG_LEVEL' ]  = 4

        # ucx is somewhat buggy
        if self.ucx: 
            self.mca['pml'    ] = 'ucx'
            self.env['UCX_TLS'] = ",".join(self.ucx)

        # number of ib devices 
        if self.hca: 
            self.env['UCX_NET_DEVICES'] = ",".join(self.hca)

        # iterate over mca hash  
        for key in self.mca: 
            mpirun_cmd.append(f'--mca {key} {self.mca[key]}') 

        # iterate over env hash 
        for var in self.env: 
            mpirun_cmd.append(f'-x {var}={self.env[var]}') 

        return " ".join(mpirun_cmd)
