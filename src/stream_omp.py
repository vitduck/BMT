#!/usr/bin/env python3

import os
import re
import logging
import argparse

from bmt import Bmt

class StreamOmp(Bmt):
    def __init__ (self, size=40000000, ntimes=100, affinity='spread', omp=0, **kwargs):
        super().__init__(**kwargs)

        self.size     = size 
        self.ntimes   = ntimes 
        self.affinity = affinity
        self.omp      = omp or self.host['CPUs']

        self.src      = ['https://www.cs.virginia.edu/stream/FTP/Code/stream.c']

        self.header   = ['size', 'ntimes', 'thread', 'affinity', 'copy(GB/s)', 'scale(GB/s)', 'add(GB/s)', 'triad(GB/s)']

        # intel icc
        if os.environ.get('CC') == 'icc':  
            self.name    += 'STREAM/ICC'
            self.cc       = 'icc'
            self.cflags   = '-qopenmp'
            self.bin      = os.path.join(self.bindir,'stream_icc') 
        else: 
            self.name     = 'STREAM'
            self.cc       = 'gcc'
            self.cflags   = '-fopenmp'
            self.bin      = os.path.join(self.bindir,'stream_gcc')

        # cmdline options  
        self.parser.usage        = '%(prog)s --afinity spread --omp 24'
        self.parser.description  = 'STREAM Benchmark'

        self.option.description += ( 
            '    --size           size of matrix\n'
            '    --ntimes         run each kernel n times\n'
            '    --affinity       thread affinit (close|spread)\n'
            '    --omp            number of OMP threads\n' )

    def build(self): 
        self.buildcmd += [
          (f'{self.cc} '
                '-O3 '
                '-ffreestanding '
               f'{self.cflags} '
               f'-DSTREAM_ARRAY_SIZE={str(self.size)} '
               f'-DNTIMES={str(self.ntimes)} '
               f'-o {self.bin} ' 
               f'{self.builddir}/stream.c')]
        
        super().build() 

    def run(self): 
        os.chdir(self.outdir)

        os.environ['OMP_PLACES']      = 'threads'
        os.environ['OMP_PROC_BIND']   = self.affinity
        os.environ['OMP_NUM_THREADS'] = str(self.omp)

        self.runcmd = f'{self.bin}'
        self.output = f'stream-{self.affinity}-omp_{self.omp}.out'

        super().run(1)

    def parse(self):
        key = ",".join(map(str, [self.size, self.ntimes, self.omp, self.affinity]))

        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in ['Copy', 'Scale', 'Add', 'Triad']: 
                    if re.search(f'{kernel}:?', line):
                        if not self.result[key][kernel]: 
                            self.result[key][kernel] = []

                        self.result[key][kernel].append(float(line.split()[1])/1000)

    def getopt(self):
        self.option.add_argument('--size'    , type=int, metavar='', help=argparse.SUPPRESS )
        self.option.add_argument('--ntimes'  , type=int, metavar='', help=argparse.SUPPRESS )
        self.option.add_argument('--affinity', type=str, metavar='', help=argparse.SUPPRESS )
        self.option.add_argument('--omp'     , type=int, metavar='', help=argparse.SUPPRESS )

        super().getopt() 
