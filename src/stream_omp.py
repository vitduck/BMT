#!/usr/bin/env python 

import os
import re
import logging
import argparse

from utils import syscmd
from bmt   import Bmt

class StreamOmp(Bmt):
    def __init__ (self, march='skylake-avx512', size=40000000, ntimes=100, thread=8, affinity='spread', prefix='./'):

        super().__init__('stream_omp')

        self.bin      = 'stream_omp'
        self.kernel   = ['Copy', 'Scale', 'Add', 'Triad']

        self.march    = march 
        self.size     = size 
        self.ntimes   = ntimes 
        self.thread   = thread
        self.affinity = affinity
        self.prefix   = prefix 
        self.header   = ['Thread', 'Affinity', 'Copy(GB/s)', 'Scale(GB/s)', 'Add(GB/s)', 'Triad(GB/s)']
        
        self.getopt()
        
    def build(self): 
        self.check_prerequisite('gcc', '7')

        self.buildcmd += [
           f'wget https://www.cs.virginia.edu/stream/FTP/Code/stream.c -O {self.builddir}/stream.c', 
           ('gcc ' 
                '-O3 '
                '-fopenmp '
                '-ffreestanding '
               f'-march={self.march} '
               f'-DSTREAM_ARRAY_SIZE={str(self.size)} '
               f'-DNTIMES={str(self.ntimes)} '
               f'-o {self.bin} {self.builddir}/stream.c')]

        super().build() 

    def run(self): 
        self.mkoutdir() 

        self.output = f'stream-{self.affinity}-omp_{self.thread}.out'
        self.runcmd = (
            f'ssh {self.host[0]} '                   # ssh to remote host 
            f'"builtin cd {self.outdir}; '           # cd to caller dir 
             'OMP_PLACES=threads '                   # thread placement 
            f'OMP_PROC_BIND={self.affinity} '        # thread affinity (close, spread, master) 
            f'OMP_NUM_THREADS={str(self.thread)} '   # thread number 
            f'{self.bin}"')                          # stream_omp cmd 
        
        super().run(1)

    def parse(self):
        bandwidth = [self.thread, self.affinity]

        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in self.kernel:
                    if re.search(f'{kernel}:?', line):
                        bandwidth.append(float(line.split()[1])/1024)

        self.result.append(bandwidth)

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -m skylake-avx512 -t 24 -a spread',
            description     = 'STREAM_OMP Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False)

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '-m, --march          targeting architecture\n'
                '-s, --size           size of matrix\n'
                '-n, --ntimes         run each kernel n times\n'
                '-t, --thread         number of OMP threads\n'
                '-a, --affinity       thread affinit (close|spread)\n'
                '    --prefix         bin/build/output directory\n' ))

        opt.add_argument('-h', '--help'    , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version' , action='version', 
                                             version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-m', '--march'   , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'    , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-n', '--ntimes'  , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--thread'  , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-a', '--affinity', type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix'  , type=str, metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
