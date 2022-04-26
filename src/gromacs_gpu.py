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

        self.name    = 'GROMACS/GPU'
        self.device  = nvidia_smi()
        self.sif     = sif 
        self.gmx_gpu = 'CUDA'
        
        # mdrun private (GPU)
        self._bonded = 'gpu'
        self._nb     = 'gpu'

        # experimental features 
        if self.gpudirect: 
            self.name    += '/GPUDIRECT'
            self.bin      = os.path.join(self.bindir, 'gmx')

            # only single node is currently supported 
            self.mpi.node = 1 

            self.pme      = 'gpu' 
            self.update   = 'gpu'
            
            # experimental halo exchange betweeb DD and PME rank
            os.environ['GMX_GPU_DD_COMMS']             = 'true'
            os.environ['GMX_GPU_PME_PP_COMMS']         = 'true'
            os.environ['GMX_FORCE_UPDATE_DEFAULT_GPU'] = 'true'

        # single rank for PME kernel offloading to GPU
        if self.pme == 'gpu': 
            if self.mpi.node * self.mpi.task == 1: 
                self._npme = -1
            else:
                self._npme = 1

        if self.sif:
            self.name += '/NGC'
            self.bin   = f'singularity run --nv {self.sif} gmx'
            self.sif   = os.path.abspath(sif)
                
        # default cuda visible devices
        if not self.mpi.cuda_devs: 
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)

        # cmdline options
        self.option.description += (
            '    --gpudirect      enable experimental GPUDirect\n' )

    def info(self): 
        for env in os.environ: 
            if re.search('GMX', env): 
                logging.info(f'export {env} = {self.environ[env]}')

    def build(self): 
        self.check_prerequisite('cuda', '10.0')

        super().build()

    def mdrun(self):
        gpu_id = "".join([str(i) for i in range(0, self.mpi.gpu)]) 

        return super().mdrun() + f' -gpu_id {gpu_id}'

    def getopt(self):
        self.option.add_argument('--gpudirect', action='store_true'  , help=argparse.SUPPRESS)

        super().getopt()
