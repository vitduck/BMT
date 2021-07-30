#!/usr/bin/env python

import os
import re

from bmt import Bmt

class HpcNvidia(Bmt):
    def __init__(self, gpu, thread, sif, prefix):

        super().__init__('hpc_nvidia')
        
        self._gpu     = gpu or self._parse_nvidia_smi()
        self.thread   = thread 
        self.sif      = sif
        self.prefix   = prefix
        self.affinity = self._parse_connect_topo() 
        self.wrapper  = ''
        self.input    = ''
   
    @property 
    def gpu(self): 
        return self._gpu 

    @gpu.setter 
    def gpu(self, gpu): 
        self._gpu     = gpu 
        self.affinity = self._parse_connect_topo() 
        
    def _parse_connect_topo(self):
        affinity = [] 
        topology = self.syscmd(f'ssh {self.host[0]} "nvidia-smi topo -m"')

        for line in topology.splitlines():
            if re.search('^GPU\d+', line): 
                affinity.append(line.split()[-1])

        return [affinity[int(i)] for i in self.gpu]

    def _parse_memory(self): 
        memory = self.syscmd(f'ssh {self.host[0]} "nvidia-smi -i 0 --query-gpu=memory.total --format=csv,noheader"').split()[0]

        return int(memory)

    def run(self): 
        # set correct path to sif file 
        self.sif = (os.path.relpath(os.path.abspath(self.sif), self.outdir)) 

        self.runcmd = (
           f'cd {self.outdir}; '
           f'{self.gpu_selection()} '
           f'mpirun ' 
                '--hostfile hostfile '
                '--mca btl ^openib '
                'singularity run '
               f'--nv {self.sif} ' 
               f'{self.wrapper} '
                   f'--dat {self.input} '
                   f'--cpu-cores-per-rank {self.thread} '  
                   f'--cpu-affinity {":".join(str(cpu) for cpu in self.affinity)} '
                   f'--gpu-affinity {":".join(str(gpu) for gpu in self.gpu)} ' )
