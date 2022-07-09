#!/usr/bin/env python3

import os
import re
import argparse

from env import module_list
from gpu import device_query, nvidia_smi, gpu_info
from bmt import Bmt

class StreamCuda(Bmt):
    def __init__(self, arch='', mem='DEFAULT', size=eval('2**25'), ntimes=100, **kwargs): 
        super().__init__(**kwargs)
        
        self.name   = 'STREAM/CUDA'
        self.bin    = os.path.join(self.bindir,'stream_cuda')

        self.device = nvidia_smi()

        self.arch   = arch 
        self.mem    = mem 
        self.size   = size 
        self.ntimes = ntimes 

        self.src    = [ 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/Stream.h', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/main.cpp', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.cu' ]

        self.header = ['arch', 'size', 'ntimes', 'copy(GB/s)', 'mul(GB/s)', 'add(GB/s)', 'triad(GB/s)', 'dot(GB/s)']

        self.parser.description = 'STREAM benchmark (CUDA)'
    
    def build(self): 
        self.check_prerequisite('cuda', '10.1')

        if not self.arch: 
            runtime, cuda_cc = device_query(self.builddir)
            self.arch        = f'sm_{cuda_cc}'

        self.buildcmd = [[
            ['nvcc', 
                '-O3', 
                '-std=c++11',
                '-DCUDA', 
               f'-arch={self.arch}', 
               f'-D{self.mem}', 
               f'-o {self.bin}', 
               f'{self.builddir}/main.cpp', 
               f'{self.builddir}/CUDAStream.cu' ]]]
        
        super().build() 

    def run(self): 
        os.chdir(self.outdir)
    
        self.output = f'stream-cuda-{self.arch}.out'

        super().run(1) 

    def runcmd(self): 
        cmd = [
            self.bin, 
               f'-s {str(self.size)}', 
               f'-n {str(self.ntimes)}' ]

        return [cmd]

    def parse(self):
        key = ",".join(map(str, [self.arch, self.size, self.ntimes]))

        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in ['Copy', 'Mul', 'Add', 'Triad', 'Dot']: 
                    if re.search(f'{kernel}:?', line):
                        if not self.result[key][kernel]: 
                            self.result[key][kernel] = [] 

                        self.result[key][kernel].append(float(line.split()[1])/1000)
    
    def add_argument(self):
        super().add_argument()

        self.parser.add_argument('--arch'  , type=str, metavar='SM',help='targeting architecture (default: auto-detected)')
        self.parser.add_argument('--mem'   , type=str, metavar='MODE',help='memory mode (default: MANAGED)')
        self.parser.add_argument('--size'  , type=int, help='matrix size (default: 33554432)')
        self.parser.add_argument('--ntimes', type=int, help='run each kernel n times (default: 100)')
