#!/usr/bin/env python3 

import os
import re
import argparse

from math  import sqrt
from env   import module_list
from cpu   import cpu_info
from gpu   import gpu_info, gpu_id
from hpcnv import Hpcnv

class Hpcg(Hpcnv): 
    def __init__(self,
        grid=[256, 256, 256], time=60, 
        nodes=0, ngpus=0, omp=4, sif='hpc-benchmarks_20.10-hpcg.sif', prefix='./'):

        super().__init__('hpcg-nvidia', nodes, ngpus, omp, sif, prefix)

        self.wrapper = 'hpcg.sh'
        self.input   = 'HPCG.in'
        self.output  = 'HPCG.out'

        self.grid    = grid 
        self.time    = time
        self.header  = ['Node', 'Ngpu', 'Thread', 'Mpi', 'Grid', 'Time(s)', 'SpMV(GFlops)', 'SymGS(GFlops)', 'Total(GFlops)', 'Final(GFlops)']
        
        self.getopt() 

        cpu_info(self.host[0])
        gpu_info(self.host[0])
        module_list()

    def write_input(self):
        input_file = os.path.join(self.outdir, 'HPCG.in')

        with open(input_file, 'w') as input_fh:
            input_fh.write( 'HPCG input\n')
            input_fh.write( 'KISTI\n')
            input_fh.write(f'{" ".join(str(grid) for grid in self.grid)}\n')
            input_fh.write(f'{self.time}')

    def run(self): 
        # bug in 20.10 
        os.environ['CUDA_VISIBLE_DEVICES']           = ",".join([str(i) for i in range(0, self.ngpus)])
        os.environ['SINGULARITYENV_LD_LIBRARY_PATH'] = '/usr/local/cuda-11.1/targets/x86_64-linux/lib'
        
        # ncpus = ngpus
        self.ntasks = self.ngpus

        self.mkoutdir() 
        self.write_hostfile() 
        self.write_input() 

        self.output = f'HPCG-n{self.nodes}-g{self.ngpus}-t{self.omp}-{"x".join([str(grid) for grid in self.grid])}.out'
        self.runcmd = self.ngc_cmd() 
        
        super().run(1)

    def parse(self): 
        with open(self.output, 'r') as output_fh: 
            for line in output_fh: 
                regex_time   = re.search('Total Time', line)
                regex_grid   = re.search('process grid', line) 
                regex_domain = re.search('local domain', line)  
                regex_SpMV   = re.search('SpMV\s+=', line)
                regex_SymGS  = re.search('SymGS\s+=', line)
                regex_total  = re.search('total\s+=', line)
                regex_final  = re.search('final\s+=', line)
                
                if regex_time: 
                    time = float(line.split()[2])
                if regex_grid:
                    grid = line.split()[0]
                if regex_domain:
                    domain = line.split()[0]
                if regex_SpMV: 
                    SpMV = float(line.split()[2])
                if regex_SymGS: 
                    SymGS = float(line.split()[2])
                if regex_total: 
                    total = float(line.split()[2])
                if regex_final: 
                    final = float(line.split()[2])

        self.result.append([self.nodes, self.ngpus, self.omp, grid, domain, time, SpMV, SymGS, total, final])

    def summary(self, sort=0, order='>'): 
        super().summary(sort, order)

        print() 
        print('SpMV:  sparse matrix-vector multiplication')
        print('SymGS: symmetric Gauss-Seidel method')
        print('Total: total performance')
        print('Final: total performance including initialization overhead')

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
                '    --nodes          number of nodes\n'
                '    --ngpus          number of gpus per node\n'
                '    --omp            number of omp threads\n'
                '    --sif            path of singularity images\n'
                '    --prefix         bin/build/output dir\n' ))
    
        # version string
        opt.add_argument('-h', '--help'   , action='help'                  , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                           version='%(prog)s '+self.version, help=argparse.SUPPRESS)

        opt.add_argument('-g', '--grid'   , type=int, nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--time'   , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'  , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'  , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'    , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'    , type=str           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str           , metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
