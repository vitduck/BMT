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
        
        if self.gpudirect: 
            self.name += '/GPUDIRECT'
            self.bin   = os.path.join(self.bindir, 'gmx')
        elif self.sif:
            self.name += '/NGC'
            self.sif   = os.path.abspath(sif)
            self.bin   = f'singularity run --nv {self.sif} gmx'
        
        # mdrun private (GPU)
        self._bonded = 'gpu'
        self._nb     = 'gpu'
        
        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)

    def run(self): 
        self.mpi.env['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in self.mpi.cuda_devs[0:self.mpi.gpu]])

        # Experimental support for GPUDirect implementation
        if self.gpudirect: 
            self.mpi.node = 1 
            self.mpi.task = len(self.mpi.gpu)
            
            self._pme     = 'gpu'
            self._npme    = 1 
            
            # experimental GPUDirect
            os.environ['GMX_GPU_DD_COMMS']             = 'true'
            os.environ['GMX_GPU_PME_PP_COMMS']         = 'true'
            os.environ['GMX_FORCE_UPDATE_DEFAULT_GPU'] = 'true'
        
        super().run()

    def mdrun(self): 
        cmd = [ super().mdrun() ]

        # thread-MPI requires -ntmpi to be set explicitly
        if self.sif or self.gpudirect: 
            cmd.append(f'-ntmpi {self.mpi.task}')

        return " ".join(cmd)
