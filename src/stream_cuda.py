#!/usr/bin/env python 

import os
import re
import argparse

from env    import module_list
from stream import Stream

class StreamCuda(Stream):
    def __init__(self, arch='sm_70', mem='DEFAULT', size=eval('2**25'), ntimes=100, **kwargs): 

        super().__init__(**kwargs)
        
        self.name   = 'STREAM/CUDA'
        self.bin    = 'stream_cuda'
        self.kernel = ['Copy', 'Mul', 'Add', 'Triad', 'Dot']
        self.header = ['Copy(GB/s)', 'Mul(GB/s)', 'Add(GB/s)', 'Triad(GB/s)', 'Dot(GB/s)']

        self.arch   = arch 
        self.mem    = mem 
        self.size   = size 
        self.ntimes = ntimes 
                
        self.getopt()  
        
    def build(self): 
        self.check_prerequisite('cuda', '10.1')

        self.buildcmd += [
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/Stream.h -O {self.builddir}/Stream.h', 
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/main.cpp -O {self.builddir}/main.cpp',  
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.h -O {self.builddir}/CUDAStream.h', 
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.cu -O {self.builddir}/CUDAStream.cu',
           ('nvcc '
               '-O3 '
               '-std=c++11 '
               '-DCUDA '
              f'-arch={self.arch} '
              f'-D{self.mem} '
              f'-o {self.bin} {self.builddir}/main.cpp {self.builddir}/CUDAStream.cu')]
        
        super().build() 

    def run(self): 
        self.check_prerequisite('cuda', '10.1')

        self.mkoutdir()
        
        self.output = 'stream-cuda.out'
        self.runcmd = ( 
            f'ssh {self.host[0]} '                                     # ssh to remote host 
            f'"builtin cd {self.outdir}; '                             # cd to caller dir
            f'{self.bin} -s {str(self.size)} -n {str(self.ntimes)}"')  # stream_cuda cmd 
        
        super().run(1) 

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -a sm_70',
            description     = 'STREAM_CUDA Benchmark', 
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False )
    
        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help          show this help message and exit\n'
                '-v, --version       show program\'s version number and exit\n'
                '-a, --arch          targeting architecture\n'
                '-m, --mem           memory mode\n'
                '-s, --size          size of matrix\n'
                '-n, --ntimes        run each kernel n times\n' ))

        opt.add_argument('-h', '--help'   , action='help'         , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                  version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-a', '--arch'   , type=str, metavar=''  , help=argparse.SUPPRESS)
        opt.add_argument('-m', '--mem'    , type=str, metavar=''  , help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'   , type=int, metavar=''  , help=argparse.SUPPRESS)
        opt.add_argument('-n', '--ntimes' , type=int, metavar=''  , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args()) 
