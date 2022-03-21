#/usr/bin/env python3

import os
import re
import argparse

from glob    import glob
from utils   import sync
from bmt_mpi import BmtMpi

class Ior(BmtMpi):
    def __init__(self, transfer='4M', block='64M', segment=16, ltrsize=0, ltrcount=0, **kwargs): 
        super().__init__(**kwargs)
        
        self.name     = 'IOR'
        self.bin      = os.path.join(self.bindir, 'ior')
        
        self.transfer = transfer
        self.block    = block 
        self.segment  = segment
        self.ltrsize  = ltrsize
        self.ltrcount = ltrcount

        self.src      = ['https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz -O {self.builddir}/ior-3.3.0.tar.gz']
        
        self.header   = ['node', 'ntask', 'transfer', 'block', 'segment', 'size', 'write(MB/s)', 'read(MB/s)', 'write(OPS)', 'read(OPS)']

        # cmdline options 
        self.parser.usage        = '%(prog)s -b 16M -t 1M -s 16'
        self.parser.description  = 'IOR Benchmark'
        
        self.option.description += (
            '    --transfer       transfer size\n'
            '    --block          block size\n'
            '    --segment        segment count\n'
            '    --ltrsize        lustre stripe size\n' 
            '    --ltrcount       lustre stripe count\n' )

    def build(self): 
        if os.path.exists(self.bin):
            return
        
        self.check_prerequisite('openmpi', '3')

        self.buildcmd = [
           f'cd {self.builddir}; tar xf ior-3.3.0.tar.gz', 
          (f'cd {self.builddir}/ior-3.3.0;' 
            './configure '
               f'--prefix={os.path.abspath(self.prefix)} '
                'MPICC=mpicc ' 
               f'CPPFLAGS=-I{os.environ["MPI_ROOT"]}/include '
               f'LDFLAGS=-L{os.environ["MPI_ROOT"]}/lib;' 
            'make -j 8;' 
            'make install' )]

        super().build()

    def run(self): 
        os.chdir(self.outdir)

        self.mpi.write_hostfile() 

        self.runcmd = (
           f'{self.mpi.run()} '
           f'{self.bin} '
           f'-t {self.transfer} ' 
           f'-b {self.block} ' 
           f'-s {self.segment} '
            '-w '                 # write benchmark
            '-r '                 # read benchmark
            '-k '                 # do not remove files
            '-z '                 # random access to file 
            '-e '                 # fsync upon write close
            '-F '                 # N-to-N 
            '-C ' )               # reorderTasks
        
        # lustre directives 
        directive = [] 
        if self.ltrsize: 
            directive.append(f'lustreStripeSize={self.ltrsize}')
        if self.ltrcount: 
            directive.append(f'lustreStripeCount={self.ltrcount}')

        if directive: 
            self.runcmd += f'-O "{",".join(directive)}"'
        
        # flush cache 
        sync(self.nodelist)
        
        self.output = (
            'ior-'
           f'n{self.mpi.node}-'
           f'p{self.mpi.task}-'
           f't{self.transfer}-'
           f'b{self.block}-'
           f's{self.segment}.out' )

        super().run(1) 
            
        self.clean() 

    def parse(self): 
        key   = ",".join(map(str, [self.mpi.node, self.mpi.task, self.transfer, self.block, self.segment]))

        write = [] 
        read  = [] 

        with open(self.output, 'r') as output_fh:
            line = output_fh.readline() 

            while line: 
                # append total size to key 
                if re.search('aggregate filesize', line): 
                    size, unit = line.split()[-2:] 
                    size  = f'{size}{unit[0]}'
                    key  += f',{size}'
                    # size = f'{size}{unit[0].lower()}'

                if re.search('Summary', line): 
                    output_fh.readline() 
                    write = output_fh.readline().split()
                    read  = output_fh.readline().split()
                    exit

                line = output_fh.readline() 

        if not self.result[key]['write']: 
            self.result[key]['write']        = [] 
            self.result[key]['read']         = [] 
            self.result[key]['random_write'] = [] 
            self.result[key]['random_read']  = [] 
    
        self.result[key]['write'].append(float(write[3]))
        self.result[key]['read' ].append(float(read[3]))
        self.result[key]['random_write'].append(float(write[7]))
        self.result[key]['random_read' ].append(float(read[7]))

    def clean(self): 
        for io_file in glob('testFile*'): 
            os.remove(io_file)

    def getopt(self): 
        self.option.add_argument('--transfer' , type=str, metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--block'    , type=str, metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--segment'  , type=int, metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--ltrsize'  , type=int, metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--ltrcount' , type=int, metavar='' , help=argparse.SUPPRESS)
        
        super().getopt() 
