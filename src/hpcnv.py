#!/usr/bin/env python

import os
import re

from gpu import gpu_affinity, nvidia_smi
from bmt import Bmt

class Hpcnv(Bmt):
    def __init__(self, sif='', **kwargs):

        super().__init__('NGC', **kwargs)
        
        self.wrapper = ''
        self.device  = nvidia_smi(self.nodelist[0])

        # default number of GPUs
        if not self._ngpus: 
            self._ngpus  = len(self.device.keys())

        self._omp       = 4 
        self._ntasks    = self._ngpus
        self.sif        = os.path.abspath(sif) 

        self.mpi.ntasks = self._ntasks 
        
    @Bmt.ngpus.setter
    def ngpus(self, number_of_gpus): 
        super(Hpcnv, Hpcnv).ngpus.__set__(self, number_of_gpus) 
        
        self._ntasks    = number_of_gpus
        self.mpi.ntasks = number_of_gpus

    def ngc_cmd(self): 
        nprocs = self.nnodes * self.ntasks

        return (
           f'{self.mpi.mpirun_cmd()} '
                'singularity run '
               f'--nv {self.sif} ' 
               f'{self.wrapper} '
                   f'--dat {self.input} '
                   f'--cpu-cores-per-rank {self.omp} '  
                   f'--cpu-affinity {":".join(gpu_affinity(self.nodelist[0])[0:self.ngpus])} '
                   f'--gpu-affinity {":".join([str(i) for i in range(0, self.ngpus)])} ')

    def run(self): 
        self.check_prerequisite('openmpi'    , '4'     )
        self.check_prerequisite('connectx'   , '4'     )
        self.check_prerequisite('nvidia'     , '450.36')
        self.check_prerequisite('singularity', '3.4.1' )
        
        os.environ['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in range(0, self.ngpus)])
        
        self.mkoutdir() 
        
        self.write_input() 
        self.mpi.write_hostfile() 
        
        self.runcmd = self.ngc_cmd() 
        
        super().run(1)
