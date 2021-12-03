#!/usr/bin/env python 

import os
import re
import logging
import argparse

from cpu    import cpu_info
from env    import module_list
from stream import Stream

class StreamOmp(Stream):
    def __init__ (self, size=40000000, ntimes=100, thread=0, affinity='spread', prefix='./'):
        super().__init__('stream_omp')

        self.bin      = 'stream_omp'
        self.kernel   = ['Copy', 'Scale', 'Add', 'Triad']

        self.size     = size 
        self.ntimes   = ntimes 
        self.thread   = thread or self.ntasks
        self.affinity = affinity
        self.prefix   = prefix 

        self.header   = ['Thread', 'Affinity', 'Copy(GB/s)', 'Scale(GB/s)', 'Add(GB/s)', 'Triad(GB/s)']
        
        self.getopt()
        
        self.cpu = cpu_info(self.host[0])

        module_list()

    def build(self): 
        # default gcc
        if 'CC' not in os.environ: 
            os.environ['CC'] = 'gcc'
        
        # intel icc 
        if os.environ['CC'] == 'icc': 
            openmp_flag = '-qopenmp' 
        else: 
            openmp_flag = '-fopenmp' 

        self.buildcmd += [
           f'wget https://www.cs.virginia.edu/stream/FTP/Code/stream.c -O {self.builddir}/stream.c', 
          (f'{os.environ["CC"]} '
                '-O3 '
               f'{openmp_flag} '
                '-ffreestanding '
               f'-DSTREAM_ARRAY_SIZE={str(self.size)} '
               f'-DNTIMES={str(self.ntimes)} '
               f'-o {self.bin} {self.builddir}/stream.c')]
        
        super().build() 

    def run(self): 
        module_cmd = ''
        if os.environ['CC'] == 'icc':
            module_cmd = 'module load intel;'

        self.mkoutdir() 

        self.output = f'stream-{self.affinity}-omp_{self.thread}.out'
        self.runcmd = (
            f'ssh {self.host[0]} '                   # ssh to remote host 
            f'"builtin cd {self.outdir}; '           # cd to caller dir 
            f'{module_cmd} '                         # for intel compiler
             'OMP_PLACES=threads '                   # thread placement 
            f'OMP_PROC_BIND={self.affinity} '        # thread affinity (close, spread, master) 
            f'OMP_NUM_THREADS={str(self.thread)} '   # thread number 
            f'{self.bin}"')                          # stream_omp cmd 
        
        super().run(1)

    def parse(self):
        super().parse() 

        # insert thread number and affinity to beginning
        self.result[-1] = [self.thread, self.affinity] + self.result[-1]

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -t 24 -a spread',
            description     = 'STREAM_OMP Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False)

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '-s, --size           size of matrix\n'
                '-n, --ntimes         run each kernel n times\n'
                '-t, --thread         number of OMP threads\n'
                '-a, --affinity       thread affinit (close|spread)\n'
                '    --prefix         bin/build/output directory\n' ))

        opt.add_argument('-h', '--help'    , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version' , action='version', 
                                             version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'    , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-n', '--ntimes'  , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--thread'  , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-a', '--affinity', type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix'  , type=str, metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
