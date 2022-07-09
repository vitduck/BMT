#!/usr/bin/env python3

import os
import re
import logging
import argparse

from gromacs import Gromacs
from gpu import nvidia_smi, gpu_affinity
from env import get_module

class GromacsGpu(Gromacs):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name    = 'GROMACS/GPU'
        self.device  = nvidia_smi()
        self.gmx_gpu = 'CUDA'

        self.nb      = 'gpu'
        
        # default cuda visible devices
        if not self.mpi.cuda_devs: 
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)

    def build(self): 
        if self.sif: 
            return 
        
        self.check_prerequisite('cuda', '10.0')

        super().build()

    def run(self): 
        # experimental !!!
        if self.gpudirect:
            self.name = 'GROMACS/GPUDirect'

            # experimental halo exchange betweeb DD and PME rank (2022.x) 
            os.environ['GMX_ENABLE_DIRECT_GPU_COMM'] = '1'
            
            # experimental halo exchange betweeb DD and PME rank (2021.x) 
            os.environ['GMX_GPU_DD_COMMS']     = '1'
            os.environ['GMX_GPU_PME_PP_COMMS'] = '1'

            self.bonded = 'gpu'
            self.pme    = 'gpu'
            self.update = 'gpu'
            
        # single rank for PME kernel offloading to GPU
        if self.pme == 'gpu': 
            if self.mpi.node * self.mpi.task == 1: 
                self._pme = -1
            else:
                self.npme = 1

        if self.sif: 
            self.name += '/NGC'

        super().run()

    def execmd(self):
        if self.sif: 
            self.bin = 'gmx' 

        gpu_id = "".join([str(i) for i in range(0, self.mpi.gpu)]) 

        return super().execmd() + [f'-gpu_id {gpu_id}']

    def add_argument(self):
        super().add_argument() 

        self.parser.add_argument('--gpudirect', action='store_true', help='enable experimental GPUDirect implementation (default: False)')
