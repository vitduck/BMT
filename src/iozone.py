#!/usr/bin/env python3

import re
import os
import argparse

from glob  import glob 
from cpu   import cpu_info
from utils import sync
from bmt   import Bmt

class Iozone(Bmt):
    def __init__(self, size='16m', record='64k', thread_per_host=4, prefix='./'): 
        super().__init__('iozone')
        
        self.bin             = 'iozone'

        self.size            = size
        self.record          = record
        self.thread_per_host = thread_per_host
        self.prefix          = prefix

        self.bandwidth       = []
        self.header          = ['Size', 'Record', 'Thread', 'Write(MB/s)', 'Read(MB/s)', 'RWrite(OPS)', 'RRead(OPS)']
        
        self.buildcmd += [
           f'wget http://www.iozone.org/src/current/iozone3_491.tgz -O {self.builddir}/iozone3_491.tgz',
           f'cd {self.builddir}; tar xf iozone3_491.tgz', 
           f'cd {self.builddir}/iozone3_491/src/current; make linux', 
           f'cp {self.builddir}/iozone3_491/src/current/iozone {self.bindir}' ]

        self.getopt() 

        # default thread 
        self.thread = self.thread_per_host * len(self.host) 

        cpu_info(self.host[0])

    def run(self): 
        self.mkoutdir()
        self.write_hostfile() 

        option = (
           f'-s {self.size} '        # file size per thread 
           f'-r {self.record} '      # record size 
           f'-+m {self.hostfile} '   # hostfile: <hostname> <outdir> <iozone bin> 
           f'-t {str(self.thread)} ' # total number of thread 
            '-c '                    # includes close in timing calculation  
            '-e '                    # incldues flush in timing calculation
            '-w '                    # keep temporary files for read test
            '-I '                    # use O_Direct 
            '-+n')                   # skip retests
        
        self.bandwidth = [] 
        
        # write
        self.output = f'iozone-0-{self.size}-{self.record}-thr_{self.thread}.out'
        self.runcmd = f'RSH=ssh {self.bin} -i 0 {option}'

        sync(self.host)
        super().run(1) 
        
        # read 
        self.output = f'iozone-1-{self.size}-{self.record}-thr_{self.thread}.out'
        self.runcmd = f'RSH=ssh {self.bin} -i 1 {option}'

        sync(self.host)
        super().run(1) 
        
        # random read/write
        self.output = f'iozone-2-{self.size}-{self.record}-thr_{self.thread}.out'
        self.runcmd = f'RSH=ssh {self.bin} -i 2 -O {option}'

        sync(self.host)
        super().run(1) 

        self.result.append([self.size, self.record, self.thread] + self.bandwidth)

        self.clean()

    def write_hostfile(self): 
        outdir = os.path

        with open(self.hostfile, 'w') as fh:
            for host in self.host:
                for thread in range(self.thread_per_host): 
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
            usage           = '%(prog)s -s 1G -r 1024K -t 8',
            description     = 'IOZONE Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False )

        opt = parser.add_argument_group(
            title='Optional arguments',
            description=(
                '-h, --help                  show this help message and exit\n'
                '-v, --version               show program\'s version number and exit\n'
                '-s, --size                  file size/thread (default: 16m)\n'
                '-r, --record                record size (default: 64k)\n'
                '-t, --thread_per_host       number of threads/host (default: 4)\n'
                '    --prefix                bin/build/output directory\n' ))
        
        opt.add_argument('-h', '--help'           , action='help'                     , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version'        , action='version', 
                                                    version='%(prog)s ' + self.version, help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'           , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-r', '--record'         , type=str, metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--thread_per_host', type=int, metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix'         , type=str, metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
