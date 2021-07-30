#!/usr/bin/env python3

import re
import os
import argparse
import glob

from bmt import Bmt

class Iozone(Bmt):
    def __init__(self, prefix='./', size='16m', record='64k', thread_per_host=4): 
        super().__init__('iozone')

        self.prefix          = prefix
        self.size            = size
        self.record          = record 
        self.prefix          = prefix 
        self.thread_per_host = thread_per_host 
        self.mode            = 0 
        self.thread          = 0 

        self.buildcmd += [
           f'wget http://www.iozone.org/src/current/iozone3_491.tgz -O {self.builddir}/iozone3_491.tgz',
           f'cd {self.builddir}; tar xf iozone3_491.tgz', 
           f'cd {self.builddir}/iozone3_491/src/current; make linux', 
           f'cp {self.builddir}/iozone3_491/src/current/iozone {self.bindir}' ]

        self.getopt() 

    def run(self): 
        # default number of threads
        if self.thread == 0: 
            self.thread = self.thread_per_host * len(self.host)

        option = (
           f'-i {self.mode} '        # mode
           f'-s {self.size} '        # file size per thread 
           f'-r {self.record} '      # record size 
           f'-+m {self.hostfile} '   # hostfile: <hostname> <outdir> <iozone bin> 
           f'-t {str(self.thread)} ' # total number of thread 
            '-c '                    # includes close in timing calculation  
            '-e '                    # incldues flush in timing calculation
            '-w '                    # keep temporary files for read test
            '-I '                    # use O_Direct 
            '-+n')                   # skip retests

        # random read/write using IOPs 
        if self.mode == 2: 
            option += ' -O'

        self.runcmd = f'RSH=ssh {self.bin} {option}'
        self.output = f'iozone-{self.mode}-{self.size}-{self.record}-thr_{self.thread}.out'
        
        super().run()
    
    def write_hostfile(self): 
        self.hostfile = os.path.join(self.outdir, 'hostfile')

        with open(self.hostfile, 'w') as fh:
            for host in self.host:
                # check if ssh works
                self.syscmd(f'ssh {host} exit')

                for i in range(self.thread_per_host): 
                    fh.write(f'{host} {os.path.abspath(self.outdir)} {os.path.abspath(self.bin)}\n')
    
    def parse_output(self): 
        result = [] 
        
        with open(self.output, 'r') as output_fh: 
            for line in output_fh: 
                if re.search('Children see throughput', line):
                    result.append(float(line.split()[-2]))

        return result[0] if len(result) == 1 else result

    def clean(self): 
        for file in sorted(glob.glob(f'{self.outdir}/*DUMMY*')):
            self.syscmd(f'rm {file}', verbose=1)
        
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
