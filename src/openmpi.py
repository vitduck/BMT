#!/usr/bin/env python3 

from mpi import Mpi

class OpenMPI(Mpi): 
    def __init__(self, ucx=[], hca=[], sharp=0, verbose=0, **kwargs): 
        super().__init__(**kwargs) 

        self.ucx   = ucx 
        self.hca   = hca
        self.sharp = sharp
        self.mca   = {'pml' : '^ucx'}

    def write_hostfile(self):
        with open(self.hostfile, 'w') as fh:
            for host in self.nodelist[0:self.node]:
                fh.write(f'{host} slots={self.task}\n')

    def mpirun(self): 
        cmd = [
            'mpirun', 
                '--allow-run-as-root', 
               f'--np {self.node*self.task}', 
               f'--hostfile {self.hostfile}' ]

        # process binding
        if self.bind: 
            cmd.append(f'--bind-to {self.bind}')

        # process mapping 
        if self.map: 
            cmd.append(f'--map-by {self.map}') 
        
        # show report to stderr
        if self.verbose: 
            cmd.append(f'--report-bindings')

        # sharp
        if self.sharp:
            self.mca['coll_hcoll_enable'    ] = 1 

            self.env['HCOLL_ENABLE_SHARP'   ] = self.sharp 
            self.env['SHARP_COLL_ENABLE_SAT'] = 1
            self.env['SHARP_COLL_LOG_LEVEL' ] = 3

        # ucx is somewhat buggy and disabled by default
        if self.ucx: 
            self.mca['pml'    ] = 'ucx'
            self.env['UCX_TLS'] = ",".join(self.ucx)

        # number of ib devices 
        if self.hca: 
            self.env['UCX_NET_DEVICES'] = ",".join(self.hca)

        # iterate over mca hash  
        for key in self.mca: 
            cmd.append(f'--mca {key} {self.mca[key]}') 

        # iterate over env hash 
        for var in self.env: 
            cmd.append(f'-x {var}={self.env[var]}') 

        return cmd
