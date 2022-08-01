#!/usr/bin/env python3

import os
import re
import logging
import argparse

from babel_stream import BabelStream

class StreamOmp(BabelStream):
    def __init__ (self, affinity='spread', omp=0, ntimes=100, **kwargs):
        super().__init__(**kwargs)

        self.affinity = affinity
        self.omp      = omp or os.environ['SLURM_NTASKS_PER_NODE']

        self.model    = 'OMP'
        self.stream   = 'OMPStream.cpp'
        self.src      = [ 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/Stream.h', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/main.cpp', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/omp/OMPStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/omp/OMPStream.cpp' ]

        # intel icc
        if os.environ.get('CXX') == 'icpc':
            self.name   = 'STREAM/OMP/ICC'
            self.cc     = 'icpc'
            self.cflags = '-O3 -qopenmp'
            self.bin    = os.path.join(self.bindir,'babelstream_icpc')
        else: 
            self.name   = 'STREAM/OMP'
            self.cc     = 'g++'
            self.cflags = '-o3 -fopenmp'
            self.bin    = os.path.join(self.bindir,'babelstream_gcc')
        
        self.header    = ['size', 'ntimes', 'thread', 'affinity', 'copy(GB/s)', 'scale(GB/s)', 'add(GB/s)', 'triad(GB/s)', 'dot(GB/s)']

        self.parser.description = 'STREAM_OMP Benchmark'

    def run(self): 
        os.chdir(self.outdir)

        os.environ['OMP_PLACES']      = 'threads'
        os.environ['OMP_PROC_BIND']   = self.affinity
        os.environ['OMP_NUM_THREADS'] = str(self.omp)

        self.output = f'babelstream-{self.affinity}-omp_{self.omp}.log'

        super().run(1) 

    def param(self): 
        return ",".join(map(str, [self.size, self.ntimes, self.omp, self.affinity]))

    def add_argument(self):
        super().add_argument()

        self.parser.add_argument('--omp'     , type=int, metavar='OMP_NUM_THREADS', help='number of threads (default: 0)')
        self.parser.add_argument('--affinity', type=str, metavar='OMP_PROC_BIND', help='thread affinity (default: spread)')
