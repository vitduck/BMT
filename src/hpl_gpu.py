#!/usr/bin/env python3 

import os
import re
import argparse

from hpl  import Hpl
from gpu  import nvidia_smi, gpu_affinity, gpu_memory
from math import sqrt

class HplGpu(Hpl): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name     = 'HPL/GPU' 
        self.device   = nvidia_smi()
        self.bin      = os.path.join(self.bindir,'hpl.sh') 

        # default cuda visible devices
        if not self.mpi.cuda_devs: 
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)
            self.mpi.task = self.mpi.gpu

        # NVIDIA-HPL parameters 
        self.blocksize = [288]
        self.l1        = 1
        
        self.parser.description  = 'HPL Benchmark (GPU)'

    def run(self):
        self.check_prerequisite('openmpi'    , '4'     )
        self.check_prerequisite('connectx'   , '4'     )
        self.check_prerequisite('nvidia'     , '450.36')

        if self.sif: 
            self.name += '/NGC'

        super().run()

    def execmd(self): 
        if self.sif:
            self.bin   = 'hpl.sh'

        cmd = [ 
            self.bin,
               f'--dat {self.input}', 
               f'--cpu-cores-per-rank {self.mpi.omp}',  
               f'--cpu-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])}', 
               f'--mem-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])}', 
               f'--gpu-affinity {":".join([str(i) for i in range(0, self.mpi.gpu)])}' ]
        
        # ucx transport (2021.4) 
        if self.mpi.ucx: 
            cmd += [
                f'--ucx-tls {",".join(self.mpi.ucx)}' ]

        return cmd

    def total_device(self): 
        return self.mpi.node*self.mpi.gpu

    def total_memory(self): 
        return self.total_device()*gpu_memory()*1024**2
