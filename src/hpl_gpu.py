#!/usr/bin/env python3 

import os
import re
import argparse

from hpl  import Hpl
from gpu  import nvidia_smi, gpu_affinity, gpu_memory
from math import sqrt

class HplGpu(Hpl): 
    def __init__(self, sif=None, **kwargs):
        super().__init__(**kwargs)

        self.name     = 'HPL/GPU' 
        self.device   = nvidia_smi()
        self.sif      = sif

        if self.sif:
            self.name += '/NGC'
            self.sif   = os.path.abspath(sif)

        # default cuda visible devices
        if not self.mpi.cuda_devs: 
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)
            self.mpi.task = self.mpi.gpu

        # NVIDIA-HPL required parameters 
        self.l1       = 1
        
    def run(self):
        self.check_prerequisite('openmpi'    , '4'     )
        self.check_prerequisite('connectx'   , '4'     )
        self.check_prerequisite('nvidia'     , '450.36')

        if self.sif:
            self.check_prerequisite('singularity', '3.4.1' )

            self.bin   = f'singularity run --nv {self.sif} hpl.sh '
        else: 
            self.bin   = os.path.join(self.bindir, 'hpl.sh ')

        # wrapper options
        self.bin += ( 
            f'--dat {self.input} '
            f'--cpu-cores-per-rank {self.mpi.omp} '  
            f'--cpu-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])} '
            f'--mem-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])} '
            f'--gpu-affinity {":".join([str(i) for i in range(0, self.mpi.gpu)])} ' )

        # ucx transport (2021.4) 
        if self.mpi.ucx: 
            self.bin += ( 
                f'--ucx-tls {",".join(self.mpi.ucx)}' )

        super().run()

    def _scale(self): 
        return self.mpi.node*self.mpi.gpu
    
    def _total_memory(self): 
        return self._scale()*gpu_memory()*1024**2
