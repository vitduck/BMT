#!/usr/bin/env python3 

import os
import argparse

from math       import sqrt
from hpc_nvidia import HpcNvidia

class Hpcg(HpcNvidia):
    def __init__(self,
        grid=[256, 256, 256], time=60, 
        gpu=[], thread=4, prefix='./', sif='hpc-benchmarks_20.10-hpcg.sif'): 

        super().__init__(gpu, thread, sif, prefix)

        self.grid    = grid 
        self.time    = time
        self.wrapper = 'hpcg.sh'
        self.input   = 'HPCG.in'

        # cmdline options
        self.getopt() 

        # HPL requires ncpu = ngpu
        self.ntasks = len(self.gpu)
       
        self.check_prerequisite('openmpi', '4')
        self.check_prerequisite('connectx', '4')
        self.check_prerequisite('nvidia', '450.36')
        self.check_prerequisite('singularity', '3.4.1')

    def write_input(self):
        input_file = os.path.join(self.outdir, 'HPCG.in')

        with open(input_file, 'w') as input_fh:
            input_fh.write( 'HPCG input\n')
            input_fh.write( 'KISTI\n')
            input_fh.write(f'{" ".join(str(grid) for grid in self.grid)}\n')
            input_fh.write(f'{self.time}')

    def run(self): 
        super().run() 

        # bug in 20.10 
        os.environ['SINGULARITYENV_LD_LIBRARY_PATH'] = '/usr/local/cuda-11.1/targets/x86_64-linux/lib'

        self.syscmd(self.runcmd, verbose=1)

    def getopt(self): 
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -g 256 256 256 -t 60 --thread 8 --sif hpc-benchmarks_20.10-hpcg.sif',
            description     = 'HPCG benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter, 
            add_help        = False )
    
        # options for problem setup
        opt = parser.add_argument_group(
            title       = 'Optional arugments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '-g, --grid           3-dimensional grid\n'
                '-t, --time           targeted run time\n'
                '    --gpu            list of GPU indices\n'
                '    --thread         number of omp threads\n'
                '    --sif            path of singularity images\n'
                '    --prefix         bin/build/output dir\n' ))
    
        # version string
        opt.add_argument('-h', '--help'   , action='help'                  , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                           version='%(prog)s '+self.version, help=argparse.SUPPRESS)

        opt.add_argument('-g', '--grid'   , type=int, nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--time'   , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--host'   , type=str, nargs='+', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--gpu'    , type=int, nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--thread' , type=int,            metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'    , type=str,            metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str,            metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
