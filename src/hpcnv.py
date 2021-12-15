#!/usr/bin/env python

import os
import re

from gpu import gpu_affinity
from bmt import Bmt

class Hpcnv(Bmt):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.wrapper = ''
        self.omp     = 4 
        self.ntasks  = self.ngpus 

    @Bmt.ngpus.setter
    def ngpus(self, ngpus): 
        super(Hpcnv, Hpcnv).ngpus.__set__(self, ngpus) 

        # HPC requires ngpus = ntasks
        self.ntask = ngpus 
    
    def ngc_cmd(self): 
        nprocs = self.nodes * self.ntasks

        return (
           f'mpirun '
	       f'-np {nprocs} '
                '--hostfile hostfile '
                '--mca btl ^openib '
                '-x CUDA_VISIBLE_DEVICES '
                'singularity run '
               f'--nv {self.sif} ' 
               f'{self.wrapper} '
                   f'--dat {self.input} '
                   f'--cpu-cores-per-rank {self.omp} '  
                   f'--cpu-affinity {":".join(gpu_affinity(self.host[0])[0:self.ngpus])} '
                   f'--gpu-affinity {":".join([str(i) for i in range(0, self.ngpus)])} ')

    def run(self): 
        self.check_prerequisite('openmpi', '4')
        self.check_prerequisite('connectx', '4')
        self.check_prerequisite('nvidia', '450.36')
        self.check_prerequisite('singularity', '3.4.1')
        
        os.environ['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in range(0, self.ngpus)])
        
        self.ntasks = self.ngpus
        
        self.mkoutdir() 

        self.write_hostfile() 
        self.write_input() 
        
        self.runcmd = self.ngc_cmd() 

        super().run(1)
