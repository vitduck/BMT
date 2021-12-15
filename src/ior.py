#/usr/bin/env python3

import os
import re
import argparse

from glob  import glob
from utils import sync
from bmt   import Bmt

class Ior(Bmt):
    def __init__(self, transfer='1M', block='16M', segment=16, ltrsize=0, ltrcount=0, **kwargs): 
        super().__init__(**kwargs)

        self.name     = 'IOR'
        self.bin      = 'ior'
        self.header   = ['Node', 'Ntask', 'Transfer', 'Block', 'Segment', 'Size', 'Write(MB/s)', 'Read(MB/s)', 'Write(Ops)', 'Read(Ops)']
        
        self.transfer = transfer
        self.block    = block 
        self.segment  = segment
        self.ltrsize  = ltrsize
        self.ltrcount = ltrcount

        self.getopt()
        
    def build(self): 
        self.check_prerequisite('openmpi', '3')

        if os.path.exists(self.bin):
            return

        self.buildcmd += [
           f'wget https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz -O {self.builddir}/ior-3.3.0.tar.gz',
           f'cd {self.builddir}; tar xf ior-3.3.0.tar.gz', 
          (f'cd {self.builddir}/ior-3.3.0;' 
            './configure '
               f'--prefix={os.path.abspath(self.prefix)} '
                'MPICC=mpicc ' 
               f'CPPFLAGS=-I{os.environ["MPI_ROOT"]}/include '
               f'LDFLAGS=-L{os.environ["MPI_ROOT"]}/lib;' 
            'make -j 8;' 
            'make install')]
        
        super().build()

    def run(self): 
        self.check_prerequisite('openmpi', '3')

        self.mkoutdir()
        self.write_hostfile() 

        self.output = (
            'ior-'
           f'n{self.nodes}-'
           f'p{self.ntasks}-'
           f't{self.transfer}-'
           f'b{self.block}-'
           f's{self.segment}.out')

        self.runcmd = (
            'mpirun '
           f'--hostfile {self.hostfile} '
           f'{self.bin} '
           f'-t {self.transfer} ' 
           f'-b {self.block} ' 
           f'-s {self.segment} '
           f'-w '  # write benchmark
           f'-r '  # read benchmark
           f'-k '  # do not remove files
           f'-z '  # random access to file 
           f'-e '  # fsync upon write close
           f'-F '  # N-to-N 
           f'-C ') # reorderTasks
        
        # lustre directives 
        directive = [] 
        if self.ltrsize: 
            directive.append(f'lustreStripeSize={self.ltrsize}')
        if self.ltrcount: 
            directive.append(f'lustreStripeCount={self.ltrcount}')

        if directive: 
            self.runcmd += f'-O "{",".join(directive)}"'
  
        sync(self.host)
        super().run(1) 
        self.clean() 

    def parse(self): 
        with open(self.output, 'r') as output_fh:
            line = output_fh.readline() 

            while line: 
                if re.search('aggregate filesize', line): 
                    size, unit = line.split()[-2:] 
                    size = f'{size}{unit[0]}'
                    # size = f'{size}{unit[0].lower()}'

                if re.search('Summary', line): 
                    output_fh.readline() 
                    write = output_fh.readline().split()
                    read  = output_fh.readline().split()
                    exit

                line = output_fh.readline() 

        self.result.append([self.nodes, self.ntasks, self.transfer, self.block, self.segment, size, write[3], read[3], write[7], read[7]])

    def clean(self): 
        for io_file in glob('testFile*'): 
            os.remove(io_file)

    def getopt(self): 
        parser=argparse.ArgumentParser(
            usage           = '%(prog)s -b 16M -t 1M -s 16',
            description     = 'IOR Benchmark', 
            formatter_class = argparse.RawDescriptionHelpFormatter, 
            add_help        = False)

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '-t, --transfer       transfer size\n'
                '-b, --block          block size\n'
                '-s, --segment        segment count\n'
                '    --ltrsize        lustre stripe size\n' 
                '    --ltrcount       lustre stripe count\n'
                '    --nodes          number of nodes\n'
                '    --ntasks          number of mpi tasks per node\n' ))

        # options for stream setup
        opt.add_argument('-h', '--help'     , action='help'        , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version'  , action='version', 
                                 version='%(prog)s '+self.version  , help=argparse.SUPPRESS)
        opt.add_argument('-t', '--transfer' , type=str, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument('-b', '--block'    , type=str, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument('-s', '--segment'  , type=int, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ltrsize'  , type=int, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ltrcount' , type=int, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'    , type=int, metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ntasks'   , type=int, metavar='' , help=argparse.SUPPRESS)

        
        self.args = vars(parser.parse_args())
