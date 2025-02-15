#!/usr/bin/env python3

import os
import re
import logging
import argparse

from bmt import Bmt

class Stream(Bmt):
    def __init__ (self, size=40000000, ntimes=100, affinity='spread', omp=0, **kwargs):
        super().__init__(**kwargs)

        self.size     = size 
        self.ntimes   = ntimes 
        self.affinity = affinity
        self.omp      = omp or os.environ['SLURM_NTASKS_PER_NODE']

        self.src      = ['https://www.cs.virginia.edu/stream/FTP/Code/stream.c']

        self.header   = ['size', 'ntimes', 'thread', 'affinity', 'copy(GB/s)', 'scale(GB/s)', 'add(GB/s)', 'triad(GB/s)']

        self.parser.description = 'STREAM Benchmark'

    def build(self): 
        # intel icc
        if os.environ.get('CC') == 'icc':
            self.name   = 'STREAM/OMP/ICC'
            self.cc     = 'icc'
            self.cflags = '-qopenmp'
            self.bin    = os.path.join(self.bindir,'stream_icc')
        else: 
            self.name   = 'STREAM/OMP'
            self.cc     = 'gcc'
            self.cflags = '-fopenmp'
            self.bin    = os.path.join(self.bindir,'stream_gcc')

        self.buildcmd = [[
          [f'{self.cc}', 
                '-O3', 
                '-ffreestanding', 
               f'{self.cflags}', 
               f'-DSTREAM_ARRAY_SIZE={str(self.size)}', 
               f'-DNTIMES={str(self.ntimes)}', 
               f'-o {self.bin}', 
               f'{self.builddir}/stream.c' ]]]
        
        super().build()

    def run(self): 
        os.chdir(self.outdir)

        os.environ['OMP_PLACES']      = 'threads'
        os.environ['OMP_PROC_BIND']   = self.affinity
        os.environ['OMP_NUM_THREADS'] = str(self.omp)

        self.output = f'stream-{self.affinity}-omp_{self.omp}.out'

        super().run(1) 

    def runcmd(self): 
        return [self.bin]

    def parse(self):
        key = ",".join(map(str, [self.size, self.ntimes, self.omp, self.affinity]))

        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in ['Copy', 'Scale', 'Add', 'Triad']: 
                    if re.search(f'{kernel}:?', line):
                        if not self.result[key][kernel]: 
                            self.result[key][kernel] = []

                        self.result[key][kernel].append(float(line.split()[1])/1000)

    def add_argument(self):
        super().add_argument()

        self.parser.add_argument('--size'    , type=int, help='size of matrix (default: 40000000)')
        self.parser.add_argument('--ntimes'  , type=int, help='run each kernel n times (default: 100)')
        self.parser.add_argument('--omp'     , type=int, metavar='OMP_NUM_THREADS', help='number of threads (default: 0)')
        self.parser.add_argument('--affinity', type=str, metavar='OMP_PROC_BIND', help='thread affinity (default: spread)')
