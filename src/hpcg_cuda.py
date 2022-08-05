#!/usr/bin/env python3 

import os
import re
import argparse

from hpcg import Hpcg
from gpu  import nvidia_smi, gpu_affinity

class HpcgCuda(Hpcg): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name   = 'HPCG/GPU/CUDA'
        self.device = nvidia_smi()
        
        if self.sif:
            self.name += '/NGC'

        # default cuda visible devices
        if not self.mpi.cuda_devs:
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu:
            self.mpi.gpu  = len(self.mpi.cuda_devs)
            self.mpi.task = self.mpi.gpu

        self.parser.description  = 'HPCG benchmark (GPU)'

    def run(self): 
        # bug in 21.4
        os.environ['SINGULARITYENV_LD_LIBRARY_PATH'] = '/usr/local/cuda-11.2/targets/x86_64-linux/lib'

        os.chdir(self.outdir)

        self.write_input()
        self.mpi.write_hostfile()

        self.output = f'HPCG-n{self.mpi.node}-t{self.mpi.task}-o{self.mpi.omp}-g{self.mpi.gpu}-{"x".join([str(grid) for grid in self.grid])}.out'

        super().run(1)

    def execmd(self): 
        if self.sif: 
            self.bin  = 'hpcg.sh'

        cmd = [ 
            self.bin, 
               f'--dat {self.input}',
               f'--cpu-cores-per-rank {self.mpi.omp}', 
               f'--cpu-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])}', 
               f'--mem-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])}',
               f'--gpu-affinity {":".join([str(i) for i in range(0, self.mpi.gpu)])}' ]

        return cmd 

    def summary(self):
        super().summary()

        print('SpMV:  sparse matrix-vector multiplication')
        print('SymGS: symmetric Gauss-Seidel method')
        print('Total: GPU performance')
        print('Final: GPU + CPU initialization overhead')
