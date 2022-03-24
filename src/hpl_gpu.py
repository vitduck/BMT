#!/usr/bin/env python3 

import os
import re
import argparse

from hpl  import Hpl
from gpu  import nvidia_smi, gpu_affinity, gpu_memory
from math import sqrt

class HplGpu(Hpl): 
    def __init__(self, sif='', **kwargs):
        super().__init__(**kwargs)

        self.check_prerequisite('openmpi'    , '4'     )
        self.check_prerequisite('connectx'   , '4'     )
        self.check_prerequisite('nvidia'     , '450.36')
        self.check_prerequisite('singularity', '3.4.1' )

        self.name     = 'HPL/NGC' 

        self.device   = nvidia_smi()
        self.sif      = os.path.abspath(sif)

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

        self.bin = self.singularity() 

        super().run()
    
    def singularity(self): 
        return ( 
            'singularity '
                'run '
                   f'--nv {self.sif} '
                    'hpl.sh ' 
                       f'--dat {self.input} '
                       f'--cpu-cores-per-rank {self.mpi.omp} '  
                       f'--cpu-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])} '
                       f'--gpu-affinity {":".join([str(i) for i in range(0, self.mpi.gpu)])} ' )

    def opt_matrix_size(self):
        self.size = []

        # user defined memory given in GB
        if self.memory:  
            for memory in self.memory: 
                self.size.append(10000*int(sqrt(self.mpi.node*self.mpi.gpu*memory*1000**3/8)/10000))
        # gpu memory from nvidia-smi(unit MiB)
        else: 
            self.size.append(10000*int(sqrt(0.90*self.mpi.node*self.mpi.gpu*gpu_memory(self.nodelist[0])*1024**2/8)/10000))
