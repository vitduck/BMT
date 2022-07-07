#!/usr/bin/env python3 

from mpi import Mpi

class OpenMPI(Mpi): 
    def __init__(self, ucx=None, hca=[], hcoll=0, sharp=0, nccl=False, verbose=False, debug=False, **kwargs): 
        super().__init__(**kwargs) 

        self.name    = 'OpenMPI'
        self.ucx     = ucx 
        self.hca     = hca
        self.hcoll   = hcoll
        self.sharp   = sharp
        self.nccl    = nccl
        self.verbose = verbose
        self.debug   = debug
        self.mca   = {} 

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
            if self.omp: 
                cmd.append(f'--map-by {self.map}:PE={self.omp}') 
            else:
                cmd.append(f'--map-by {self.map}') 
        
        # ucx is somewhat buggy and disabled by default
        if self.ucx is None:
            self.mca['pml']               = '^ucx'
            self.mca['coll_hcoll_enable'] = '0'
        else:
            #  self.mca['btl'] = '^uct'
            if len(self.ucx): 
                self.mca['pml']     = 'ucx'
                self.env['UCX_TLS'] = ",".join(self.ucx)
        
        # number of ib devices 
        if self.hca: 
            self.env['UCX_NET_DEVICES'] = ",".join(self.hca)

        # hcoll 
        if self.hcoll: 
            self.mca['coll_hcoll_enable'    ] = '1' 

        # sharp
        if self.sharp:
            self.mca['coll_hcoll_enable'    ] = '1' 

            self.env['HCOLL_ENABLE_SHARP'   ] = str(self.sharp)
            self.env['SHARP_COLL_ENABLE_SAT'] = '1'
            self.env['SHARP_COLL_LOG_LEVEL' ] = '3'

        # show report to stderr
        if self.verbose: 
            if self.bind != 'none' or self.map: 
                cmd.append(f'--report-bindings')

        # show debug message 
        if self.debug: 
            if self.ucx is not None: 
                self.env['UCX_LOG_LEVEL']='info' 

            if self.sharp: 
                self.env['SHARP_COLL_LOG_LEVEL' ] = '4'

        # iterate over mca hash  
        for key in self.mca: 
            cmd.append(f'--mca {key} {self.mca[key]}') 

        # iterate over env hash 
        for var in self.env: 
            cmd.append(f'-x {var}={self.env[var]}') 

        return cmd
