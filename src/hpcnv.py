#!/usr/bin/env python

import os
import re

from utils import init_gpu, init_gpu_affinity
from bmt   import Bmt

class Hpcnv(Bmt):
    def __init__(self, name, nodes, ngpus, omp, sif, prefix):

        super().__init__(name)
        
        self.wrapper = ''
        self.gpu_id  = init_gpu(self.host[0])
        
        self.nodes   = nodes or len(self.host)
        self.ngpus   = ngpus or len(self.gpu_id)
        self.ntasks  = ngpus or len(self.gpu_id)
        self.omp     = omp
        self.sif     = sif
        self.prefix  = prefix
        self.sif     = os.path.abspath(self.sif)

        self.check_prerequisite('openmpi', '4')
        self.check_prerequisite('connectx', '4')
        self.check_prerequisite('nvidia', '450.36')
        self.check_prerequisite('singularity', '3.4.1')

    def ngc_cmd(self): 
        return (
           f'mpirun ' 
                '--hostfile hostfile '
                '--mca btl ^openib '
                '-x CUDA_VISIBLE_DEVICES '
                'singularity run '
               f'--nv {self.sif} ' 
               f'{self.wrapper} '
                   f'--dat {self.input} '
                   f'--cpu-cores-per-rank {self.omp} '  
                   f'--cpu-affinity {":".join(init_gpu_affinity(self.host[0])[0:self.ngpus])} '
                   f'--gpu-affinity {":".join([str(i) for i in range(0, self.ngpus)])} ')
