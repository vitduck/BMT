#!/usr/bin/env python3

import re
import os
import argparse

from glob  import glob 
from utils import sync
from bmt   import Bmt

class Iozone(Bmt):
    def __init__(self, size='64M', record='1M', threads=4, **kwargs): 
        super().__init__(**kwargs)

        self.name      = 'IOZONE'
        self.src       = ['http://www.iozone.org/src/current/iozone3_491.tgz']
        self.bin       = os.path.join(self.bindir,'iozone') 
        self.header    = ['Node', 'Thread', 'Size', 'Record', 'Write(MB/s)', 'Read(MB/s)', 'R_Write(OPS)', 'R_Read(OPS)']
        self.size      = size

        self.record    = record
        self.threads   = threads

        self.getopt() 

    def build(self): 
        if os.path.exists(self.bin):
            return 

        self.buildcmd += [
           f'cd {self.builddir}; tar xf iozone3_491.tgz', 
           f'cd {self.builddir}/iozone3_491/src/current; make linux', 
           f'cp {self.builddir}/iozone3_491/src/current/iozone {self.bindir}']

        super().build() 

    def write_hostfile(self): 
        outdir = os.path

        with open(self.hostfile, 'w') as fh:
            for node in self.nodelist:
                for threads in range(self.threads): 
                    fh.write(f'{node} {self.outdir} {self.bin}\n')

    def run(self): 
        self.mkoutdir()
        self.write_hostfile() 

        option = (
           f'-s {self.size} '                            # file size per threads 
           f'-r {self.record} '                          # record size 
           f'-+m {self.hostfile} '                       # hostfile: <hostname> <outdir> <iozone bin> 
           f'-t {str(self.threads*len(self.nodelist))} ' # total number of threads 
            '-c '                                        # includes close in timing calculation  
            '-e '                                        # incldues flush in timing calculation
            '-w '                                        # keep temporary files for read test
            '-+n')                                       # skip retests
        
        write_output  = f'iozone-i0-n{self.nnodes}-t{self.threads}-s{self.size}-r{self.record}.out'
        read_output   = f'iozone-i1-n{self.nnodes}-t{self.threads}-s{self.size}-r{self.record}.out'
        random_output = f'iozone-i2-n{self.nnodes}-t{self.threads}-s{self.size}-r{self.record}.out'

        for i in range(1, self.count+1): 
            if self.count > 1: 
                write_output  = re.sub('out(\.\d+)?', f'out.{i}', write_output)
                read_output   = re.sub('out(\.\d+)?', f'out.{i}', read_output)
                random_output = re.sub('out(\.\d+)?', f'out.{i}', random_output)

            # write
            self.output = write_output
            self.runcmd = f'RSH=ssh {self.bin} -i 0 {option}'

            sync(self.nodelist)
            super().run(1) 
        
            # read 
            self.output = read_output
            self.runcmd = f'RSH=ssh {self.bin} -i 1 {option}'

            sync(self.nodelist)
            super().run(1) 
        
            # random read/write
            #-I: Use direct IO 
            #-O: Return result in OPS
            self.output = random_output
            self.runcmd = f'RSH=ssh {self.bin} -i 2 -I -O {option}'

            sync(self.nodelist)
            super().run(1) 

            self.clean()

    def parse(self):
        key = ",".join(map(str, [self.nnodes, self.threads, self.size, self.record]))

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
        
    def getopt(self): 
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -s 1G -r 1M -t 8',
            description     = 'IOZONE Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False )

        opt = parser.add_argument_group(
            title='Optional arguments',
            description=(
                '-h, --help         show this help message and exit\n'
                '-v, --version      show program\'s version number and exit\n'
                '-s, --size         file size/threads\n'
                '-r, --record       record size\n'
                '-n, --nodes        number of nodes\n'
                '-t, --threads      number of threadss per node\n' ))
        
        opt.add_argument('-h', '--help'   , action='help'         , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                  version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'   , type=str, metavar=''  , help=argparse.SUPPRESS)
        opt.add_argument('-r', '--record' , type=str, metavar=''  , help=argparse.SUPPRESS)
        opt.add_argument('-n', '--nodes'  , type=int, metavar=''  , help=argparse.SUPPRESS)
        opt.add_argument('-t', '--threads', type=int, metavar=''  , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
