#!/usr/bin/env python3

import os
import re
import argparse

from ssh import ssh_cmd
from env import module_list
from gpu import device_query, nvidia_smi, gpu_info
from bmt import Bmt

class StreamCuda(Bmt):
    def __init__(self, arch='', mem='DEFAULT', size=eval('2**25'), ntimes=100, **kwargs): 
        super().__init__(**kwargs)
        
        self.name   = 'STREAM/CUDA'
        self.bin    = os.path.join(self.bindir,'stream_cuda') 

        self.device = nvidia_smi(self.nodelist[0])

        self.arch   = arch 
        self.mem    = mem 
        self.size   = size 
        self.ntimes = ntimes 

        self.src    = [ 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/Stream.h', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/main.cpp', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.cu']

        self.header = ['arch', 'size', 'ntimes', 'copy(GB/s)', 'mul(GB/s)', 'add(GB/s)', 'triad(GB/s)', 'dot(GB/s)']

        # cmdline options  
        self.parser.usage        = '%(prog)s --arch sm_70'
        self.parser.description  = 'STREAM benchmark (CUDA)'
    
        self.option.description += (
            '    --arch           targeting architecture\n'
            '    --mem            memory mode\n'
            '    --size           size of matrix\n'
            '    --ntimes         run each kernel n times\n' )


    def build(self): 
        self.check_prerequisite('cuda', '10.1')

        if not self.arch: 
            runtime, cuda_cc = device_query(self.nodelist[0], self.builddir)
            self.arch        = f'sm_{cuda_cc}'

        self.buildcmd += [
           ('nvcc '
                '-O3 '
                '-std=c++11 '
                '-DCUDA '
               f'-arch={self.arch} '
               f'-D{self.mem} '
               f'-o {self.bin} '
               f'{self.builddir}/main.cpp '
               f'{self.builddir}/CUDAStream.cu' )]
        
        super().build() 

    def run(self): 
        os.chdir(self.outdir)
    
        self.runcmd = ( 
           f'{ssh_cmd} {self.nodelist[0]} '          # ssh to remote host 
           f'"builtin cd {self.outdir}; '            # cd to caller dir
           f'{self.bin} ' 
           f'-s {str(self.size)} '
           f'-n {str(self.ntimes)}"' )

        self.output = 'stream-cuda.out'

        super().run(1) 

    def parse(self):
        key = ",".join(map(str, [self.arch, self.size, self.ntimes]))

        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in ['Copy', 'Mul', 'Add', 'Triad', 'Dot']: 
                    if re.search(f'{kernel}:?', line):
                        if not self.result[key][kernel]: 
                            self.result[key][kernel] = [] 

                        self.result[key][kernel].append(float(line.split()[1])/1000)
    
    def getopt(self):
        self.option.add_argument('--arch'  , type=str, metavar='', help=argparse.SUPPRESS )
        self.option.add_argument('--mem'   , type=str, metavar='', help=argparse.SUPPRESS )
        self.option.add_argument('--size'  , type=int, metavar='', help=argparse.SUPPRESS )
        self.option.add_argument('--ntimes', type=int, metavar='', help=argparse.SUPPRESS )

        super().getopt() 
