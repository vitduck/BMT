#!/usr/bin/env python3

import os
import re
import logging
import argparse

from gromacs import Gromacs
from gpu     import nvidia_smi, device_query, gpu_affinity
from ssh     import ssh_cmd
from env     import get_module

class GromacsGpu(Gromacs):
    def __init__(self, sif='', **kwargs):
        super().__init__(**kwargs)

        self.name    = 'GROMACS/GPU'
        self.device  = nvidia_smi(self.nodelist[0])
        self.sif     = sif 
 
        if self.sif:
            self.name += '/NGC'
            self.sif   = os.path.abspath(sif)
            self.bin  = f'singularity run --nv {self.sif} gmx'

        # mdrun private (GPU)
        self._bonded = 'gpu'
        self._nb     = 'gpu'
        
        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu = len(self.device.keys())

    def run(self): 
        self.mpi.env['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in range(0, self.mpi.gpu)])

        # Experimental support for GPUDirect implementation
        if self.gpudirect: 
            self.name     = self.name + '/GPUDIRECT'
            self.bin      = os.path.join(self.bindir, 'gmx')

            self.mpi.node = 1 
            self.mpi.task = self.mpi.gpu

            self._pme     = 'gpu'
            self._npme    = 1 

            os.environ['GMX_GPU_DD_COMM']              = 'true'
            os.environ['GMX_GPU_PME_PP_COMMS']         = 'true'
            os.environ['GMX_FORCE_UPDATE_DEFAULT_GPU'] = 'true'
        
        super().run()

    def mdrun(self): 
        cmd = [ super().mdrun() ]

        # thread-MPI requires -ntmpi to be set explicitly
        if self.sif: 
            cmd.append(f'-ntmpi {self.mpi.task}')

        if self.gpudirect: 
            cmd.append(f'-nstlist 400')

        # gpu indices
        #  cmd.append(f'-gpu_id {"".join([str(i) for i in range(0, self.mpi.gpu)])}')
        
        return " ".join(cmd)
