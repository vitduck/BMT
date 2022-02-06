#!/usr/bin/env python 

import os
import re
import argparse

from statistics import mean
from env        import module_list
from ssh        import ssh_cmd
from bmt        import Bmt

class StreamCuda(Bmt):
    def __init__(self, arch='sm_70', mem='DEFAULT', size=eval('2**25'), ntimes=100, **kwargs): 

        super().__init__('STREAM/CUDA', **kwargs)
        
        self.bin    = 'stream_cuda'
        self.src    = [ 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/Stream.h', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/main.cpp', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/cuda/CUDAStream.cu']

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
    
        for i in range(1, self.count+1): 
            self.output = 'stream-cuda.out'

            if self.count > 1: 
                self.output += f'.{i}'

            self.runcmd = ( 
               f'{ssh_cmd} {self.nodelist[0]} '          # ssh to remote host 
               f'"builtin cd {self.outdir}; '                             # cd to caller dir
               f'{self.bin} -s {str(self.size)} -n {str(self.ntimes)}"')  # stream_cuda cmd 
        
            super().run(1) 

    def parse(self):
        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in self.kernel:
                    if re.search(f'{kernel}:?', line):
                        if not self.result[kernel]: 
                            self.result[kernel] = [] 

                        self.result[kernel].append(float(line.split()[1])/1000)
    
    def summary(self): 
        stream_bandwidth = [] 

        for kernel in self.result:
            kernel_bandwidth  = self.result[kernel] 
            average_bandwidth = mean(kernel_bandwidth)

            stream_bandwidth.append("\n".join(list(map("{:.2f}".format, kernel_bandwidth))+[f'<{average_bandwidth:.2f}>']))

        self.table.append(stream_bandwidth)

        super().summary()

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s --arch sm_70',
            description     = 'STREAM_CUDA Benchmark', 
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False )
    
        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help          show this help message and exit\n'
                '-v, --version       show program\'s version number and exit\n'
                '    --arch          targeting architecture\n'
                '    --mem           memory mode\n'
                '    --size          size of matrix\n'
                '    --ntimes        run each kernel n times\n' ))

        opt.add_argument('-h', '--help'   , action='help',    help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', help=argparse.SUPPRESS, version='%(prog)s '+self.version)

        opt.add_argument('--arch'  , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('--mem'   , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('--size'  , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('--ntimes', type=int, metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args()) 
