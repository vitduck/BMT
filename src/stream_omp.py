#!/usr/bin/env python 

import os
import re
import logging
import argparse

from bmt import Bmt

class StreamOmp(Bmt):
    def __init__ (self, size=40000000, ntimes=100, affinity='spread', **kwargs):
        super().__init__('STREAM', **kwargs)

        self.src      = ['https://www.cs.virginia.edu/stream/FTP/Code/stream.c']
        self.kernel   = ['Copy', 'Scale', 'Add', 'Triad']
        self.header   = ['Thread', 'Affinity', 'Copy(GB/s)', 'Scale(GB/s)', 'Add(GB/s)', 'Triad(GB/s)']

        self.size     = size 
        self.ntimes   = ntimes 
        self.affinity = affinity

        # default omp threads 
        if not self.omp: 
            self.omp = self.host['CPUs']

        # intel icc
        if os.environ.get('CC') == 'icc':  
            self.name    += '/ICC'
            self.module   = 'intel'
            self.cc       = 'icc'
            self.cflags   = '-qopenmp'
            self.bin      = os.path.join(self.bindir,'stream_icc') 
        else: 
            self.module   = 'gcc'
            self.cc       = 'gcc'
            self.cflags   = '-fopenmp'
            self.bin      = os.path.join(self.bindir,'stream_gcc')

        self.getopt()

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
        self.mkoutdir() 

        self.runcmd = (
           f'ssh -oStrictHostKeyChecking=no {self.nodelist[0]} ' # ssh to remote host 
           f'"builtin cd {self.outdir}; '                        # cd to caller dir 
           f'module load {self.module}; '                        # for intel compiler
            'OMP_PLACES=threads '                                # thread placement 
           f'OMP_PROC_BIND={self.affinity} '                     # thread affinity
           f'OMP_NUM_THREADS={str(self.omp)} '                   # thread number 
           f'{self.bin}"')            

        self.output = f'stream-{self.affinity}-omp_{self.omp}.out'

        for i in range(1, self.count+1): 
            if self.count > 1: 
                self.output = re.sub('out(\.\d+)?', f'out.{i}', self.output)

            super().run(1)

    def parse(self):
        key = ",".join(map(str, [self.affinity, self.omp]))

        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in self.kernel:
                    if re.search(f'{kernel}:?', line):
                        if not self.result[key][kernel]: 
                            self.result[key][kernel] = []

                        self.result[key][kernel].append(float(line.split()[1])/1000)

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s --afinity spread --omp 24',
            description     = 'STREAM_GCC Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False)

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '    --size           size of matrix\n'
                '    --ntimes         run each kernel n times\n'
                '    --affinity       thread affinit (close|spread)\n'
                '    --omp            number of OMP threads\n' ))

        opt.add_argument('-h', '--help',     action='help' ,   help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version' , action='version', help=argparse.SUPPRESS, version='%(prog)s '+self.version,)

        opt.add_argument('--size',     type=int, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument('--ntimes',   type=int, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument('--affinity', type=str, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument('--omp',      type=int, metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
