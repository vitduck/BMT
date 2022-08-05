#!/usr/bin/env python3

import os
import re
import argparse

from gpu          import device_query, nvidia_smi, gpu_info
from babel_stream import BabelStream

class StreamCuda(BabelStream):
    def __init__(self, arch='', mem='DEFAULT', **kwargs): 
        super().__init__(**kwargs)
        
        self.name   = 'STREAM/CUDA'
        self.bin    = os.path.join(self.bindir,'stream_cuda')

        self.arch   = arch 
        self.mem    = mem 
        
        self.model  = 'CUDA'
        self.stream = 'CUDAStream.cu'
        self.src    = [
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/Stream.h', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/main.cpp', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.cu' ]
        
        self.cc     = 'nvcc'
        self.cflags = '-O3'

        self.header = ['arch', 'size', 'ntimes', 'copy(GB/s)', 'mul(GB/s)', 'add(GB/s)', 'triad(GB/s)', 'dot(GB/s)']

        self.parser.description = 'STREAM_GPU benchmark'
    
    def build(self): 
        self.check_prerequisite('cuda', '10.1')
        
        self.device = nvidia_smi()

        if not self.arch: 
            runtime, cuda_cc = device_query(self.builddir)
            self.arch        = f'sm_{cuda_cc}'

        super().build() 

    def run(self): 
        os.chdir(self.outdir)
    
        self.output = f'stream-cuda-{self.arch}.out'
        
        super().run(1) 

    def param(self): 
        return ",".join(map(str, [self.arch, self.size, self.ntimes]))

    def add_argument(self):
        super().add_argument()

        self.parser.add_argument('--arch'  , type=str, metavar='SM',help='targeting architecture (default: auto-detected)')
        self.parser.add_argument('--mem'   , type=str, metavar='MODE',help='memory mode (default: MANAGED)')
