#!/usr/bin/env python3

import re
import os
import argparse

from glob  import glob 
from cpu   import cpu_info
from utils import sync
from env   import module_list
from bmt   import Bmt

class Iozone(Bmt):
    def __init__(self, size='64M', record='1M', nodes=0, thread=4, prefix='./'): 
        super().__init__('iozone')
        
        self.bin       = 'iozone'

        self.size      = size
        self.record    = record
        self.nodes     = nodes or len(self.host)
        self.thread    = thread
        self.prefix    = prefix

        self.bandwidth = []
        self.header    = ['Node', 'Thread', 'Size', 'Record', 'Write(MB/s)', 'Read(MB/s)', 'R_Write(OPS)', 'R_Read(OPS)']
        
        self.getopt() 

        cpu_info(self.host[0])
        module_list() 

    def build(self): 
        if os.path.exists(self.bin): 
            return 

        self.buildcmd += [
           f'wget http://www.iozone.org/src/current/iozone3_491.tgz -O {self.builddir}/iozone3_491.tgz',
           f'cd {self.builddir}; tar xf iozone3_491.tgz', 
           f'cd {self.builddir}/iozone3_491/src/current; make linux', 
           f'cp {self.builddir}/iozone3_491/src/current/iozone {self.bindir}']

        super().build() 

    def run(self): 
        self.mkoutdir()
        self.write_hostfile() 

        option = (
           f'-s {self.size} '                         # file size per thread 
           f'-r {self.record} '                       # record size 
           f'-+m {self.hostfile} '                    # hostfile: <hostname> <outdir> <iozone bin> 
           f'-t {str(self.thread*len(self.host))} ' # total number of thread 
            '-c '                                     # includes close in timing calculation  
            '-e '                                     # incldues flush in timing calculation
            '-w '                                     # keep temporary files for read test
            '-+n')                                    # skip retests
        
        self.bandwidth = [] 
        
        # write
        self.output = f'iozone-i0-n{self.nodes}-t{self.thread}-s{self.size}-r{self.record}.out'
        self.runcmd = f'RSH=ssh {self.bin} -i 0 {option}'

        sync(self.host)
        super().run(1) 
        
        # read 
        self.output = f'iozone-i1-n{self.nodes}-t{self.thread}-s{self.size}-r{self.record}.out'
        self.runcmd = f'RSH=ssh {self.bin} -i 1 {option}'

        sync(self.host)
        super().run(1) 
        
        # random read/write
        # -I: Use direct IO 
        # -O: Return result in OPS
        self.output = f'iozone-i2-n{self.nodes}-t{self.thread}-s{self.size}-r{self.record}.out'
        self.runcmd = f'RSH=ssh {self.bin} -i 2 -I -O {option}'

        sync(self.host)
        super().run(1) 

        self.result.append([self.nodes, self.thread, self.size, self.record] + self.bandwidth)

        self.clean()

    def write_hostfile(self): 
        outdir = os.path

        with open(self.hostfile, 'w') as fh:
            for host in self.host:
                for thread in range(self.thread): 
                    fh.write(f'{host} {self.outdir} {self.bin}\n')

    def parse(self):
        with open(self.output, 'r') as output_fh: 
            for line in output_fh: 
                if re.search('Children see throughput', line):
                    result, unit = line.split()[-2:]
                    if unit == 'kB/sec': 
                        self.bandwidth.append(float(result)/1024)
                    else: 
                        self.bandwidth.append(float(result))

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
                '-s, --size         file size/thread\n'
                '-r, --record       record size\n'
                '-t, --thread       number of threads/host\n'
                '    --prefix       bin/build/output directory\n' ))
        
        opt.add_argument('-h', '--help'   , action='help'                     , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                            version='%(prog)s ' + self.version, help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'   , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-r', '--record' , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--thread' , type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str, metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
