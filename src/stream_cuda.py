#!/usr/bin/env python 

import re
import argparse

from env import module_list
from cpu import cpu_info
from gpu import gpu_info
from bmt import Bmt

class StreamCuda(Bmt):
    def __init__(self, arch='sm_70', mem='DEFAULT', size=eval('2**25'), ntimes=100, prefix='./'): 

        super().__init__('stream_cuda')
        
        self.bin    = 'stream_cuda'
        self.kernel = ['Copy', 'Mul', 'Add', 'Triad', 'Dot']

        self.arch   = arch 
        self.mem    = mem 
        self.size   = size 
        self.ntimes = ntimes 
        self.prefix = prefix
        self.header = ['Copy(GB/s)', 'Mul(GB/s)', 'Add(GB/s)', 'Triad(GB/s)', 'Dot(GB/s)']
        
        self.getopt()  
        
        self.cpu = cpu_info(self.host[0])
        self.gpu = gpu_info(self.host[0])

        module_list() 
        
    def build(self): 
        self.check_prerequisite('cuda', '10.1')

        self.buildcmd += [
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/Stream.h -O {self.builddir}/Stream.h', 
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/main.cpp -O {self.builddir}/main.cpp',  
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/CUDAStream.h -O {self.builddir}/CUDAStream.h', 
           f'wget https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/CUDAStream.cu -O {self.builddir}/CUDAStream.cu',
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

    def parse(self):
        bandwidth = [] 

        with open(self.output, 'r') as output_fh: 
            for line in output_fh:
                for kernel in self.kernel:
                    if re.search(f'{kernel}:?', line):
                        bandwidth.append(float(line.split()[1])/1000)
    
        self.result.append(bandwidth)

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
                '-n, --ntimes        run each kernel n times\n'
                '    --prefix        bin/build/output directory\n' ))

        opt.add_argument('-h', '--help'   , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                            version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-a', '--arch'   , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-m', '--mem'    , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'   , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-n', '--ntimes' , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str, metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args()) 
