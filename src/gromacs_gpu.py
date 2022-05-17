#!/usr/bin/env python3

import os
import re
import logging
import argparse

from gromacs import Gromacs
from gpu     import nvidia_smi, gpu_affinity
from env     import get_module

class GromacsGpu(Gromacs):
    def __init__(self, sif='', **kwargs):
        super().__init__(**kwargs)

        self.name    = 'GROMACS (GPU)'
        self.device  = nvidia_smi()
        self.sif     = sif 
        self.gmx_gpu = 'CUDA'
        
        # for gpu
        self.nb     = 'gpu'

        # experimental
        if self.gpudirect: 
            self.bin      = os.path.join(self.bindir, 'gmx')

            # only single node is currently supported 
            self.mpi.node = 1 

            self.pme      = 'gpu' 
            self.bonded   = 'gpu'
            self.update   = 'gpu'
            
            # experimental halo exchange betweeb DD and PME rank
            os.environ['GMX_GPU_DD_COMMS']             = 'true'
            os.environ['GMX_GPU_PME_PP_COMMS']         = 'true'
            os.environ['GMX_FORCE_UPDATE_DEFAULT_GPU'] = 'true'

        # single rank for PME kernel offloading to GPU
        if self.pme == 'gpu': 
            if self.mpi.node * self.mpi.task == 1: 
                self._pme = -1
            else:
                self.npme = 1

        # singularity container
        if self.sif:
            self.name  = 'GROMACS (NGC)'
            self.sif   = os.path.abspath(sif)
            self.bin   = f'singularity run --nv {self.sif} gmx'
                
        # default cuda visible devices
        if not self.mpi.cuda_devs: 
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)

    def build(self): 
        self.check_prerequisite('cuda', '10.0')

        super().build()

    def mdrun(self):
        gpu_id = "".join([str(i) for i in range(0, self.mpi.gpu)]) 

        return super().mdrun() + f' -gpu_id {gpu_id}'

    def add_argument(self):
        super().add_argument() 

        self.parser.add_argument('--gpu', type=int, help='number of GPU per node (default: $SLURM_GPUS_ON_NODE)')
        self.parser.add_argument('--gpudirect', action='store_true', help='enable experimental GPUDirect implementation (default: False)')
