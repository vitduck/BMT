#!/usr/bin/env python3

import re
import os
import argparse

from glob import glob 
from utils import sync
from bmt import Bmt

class Iozone(Bmt):
    def __init__(self, size='64M', record='1M', node=0, thread=8, **kwargs): 
        super().__init__(**kwargs)

        self.name   = 'IOZONE'
        self.bin    = os.path.join(self.bindir,'iozone')

        self.mode   = 0
        self.size   = size
        self.record = record
        self.node   = node or len(self.nodelist)
        self.thread = thread

        self.src    = ['http://www.iozone.org/src/current/iozone3_491.tgz']

        self.header = ['node', 'thread', 'size', 'record', 'write(MB/s)', 'read(MB/s)', 'r_write(OPS)', 'r_read(OPS)']
 
        self.parser.description = 'IOZONE Benchmark'

    def build(self): 
        if os.path.exists(self.bin[0]):
            return 

        self.buildcmd = [
            [f'cd {self.builddir}', 'tar xf iozone3_491.tgz'], 
            [f'cd {self.builddir}/iozone3_491/src/current', 'make linux'],
            [f'cp {self.builddir}/iozone3_491/src/current/iozone {self.bindir}']] 

        super().build() 

    def write_hostfile(self): 
        with open(self.hostfile, 'w') as fh:
            for node in self.nodelist:
                for threads in range(self.thread): 
                    fh.write(f'{node} {self.outdir} {self.bin}\n')

    def run(self): 
        os.chdir(self.outdir)
        
        self.write_hostfile() 

        # cluster mode 
        os.environ['RSH'] = 'ssh -oStrictHostKeyChecking=no'

        write_output  = f'iozone-i0-n{self.node}-t{self.thread}-s{self.size}-r{self.record}.out'
        read_output   = f'iozone-i1-n{self.node}-t{self.thread}-s{self.size}-r{self.record}.out'
        random_output = f'iozone-i2-n{self.node}-t{self.thread}-s{self.size}-r{self.record}.out'

        for i in range(1, self.count+1): 
            if self.count > 1: 
                write_output  = re.sub('out(\.\d+)?', f'out.{i}', write_output)
                read_output   = re.sub('out(\.\d+)?', f'out.{i}', read_output)
                random_output = re.sub('out(\.\d+)?', f'out.{i}', random_output)

            # write
            self.mode   = 0 
            self.output = write_output

            sync(self.nodelist)
            super().run(1) 
        
            # read 
            self.mode   = 1 
            self.output = read_output

            sync(self.nodelist)
            super().run(1) 
        
            # random read/write
            self.mode   = 2 
            self.output = random_output

            sync(self.nodelist)
            super().run(1) 

            self.clean()

    def runcmd(self):
        cmd = [
            self.bin, 
           f'-i {self.mode}'] 

        # random read/write
        #-I: Use direct IO 
        #-O: Return result in OPS
        if self.mode == 2:  
            cmd += ['-I', '-O']

        # generic options
        cmd += [
           f'-s {self.size}',                   # file size per threads 
           f'-r {self.record}',                 # record size 
           f'-+m {self.hostfile}',              # hostfile: <hostname> <outdir> <iozone bin> 
           f'-t {str(self.thread*self.node)}',  # total number of threads 
            '-c',                               # includes close in timing calculation  
            '-e',                               # incldues flush in timing calculation
            '-w',                               # keep temporary files for read test
            '-+n' ]                             # skip retests

        return [cmd]

    def parse(self):
        key = ",".join(map(str, [self.node, self.thread, self.size, self.record]))

        with open(self.output, 'r') as output_fh: 
            for line in output_fh: 
                match = re.search('Children.+?(initial|random)? (reader|writer)', line)

                if match:
                    (mode, io) = match.groups() 
                    bandwidth  = line.split()[-2]

                    # random I/O
                    if mode == 'random': 
                        if not self.result[key][f'random_{io}']: 
                            self.result[key][f'random_{io}'] = [] 

                        self.result[key][f'random_{io}'].append(float(bandwidth))
                    else: 
                        if not self.result[key][io]:  
                            self.result[key][io] = [] 

                        self.result[key][io].append(float(bandwidth)/1024)

    def clean(self): 
        for io_file in sorted(glob(f'{self.outdir}/*DUMMY*')):
            os.remove(io_file)
        
    def add_argument(self): 
        super().add_argument()

        self.parser.add_argument('--size'  , type=str, help='file size per thread (default: 64M)')
        self.parser.add_argument('--record', type=str, help='record size (default: 1M)')
        self.parser.add_argument('--node'  , type=int, help='number of node (default: $SLURM_NNODES)')
        self.parser.add_argument('--thread', type=int, help='number of threads (default: 8')
