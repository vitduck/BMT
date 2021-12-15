#!/usr/bin/env python3 

import os
import re
import argparse

from math  import sqrt
from env   import module_list
from hpcnv import Hpcnv

class Hpcg(Hpcnv): 
    def __init__(self, grid=[256, 256, 256], time=180, **kwargs):

        super().__init__(**kwargs)

        self.name    = 'HPCG/NGC'
        self.wrapper = 'hpcg.sh'
        self.input   = 'HPCG.in'
        self.output  = ''
        self.header  = ['Node', 'Ngpu', 'Thread', 'Mpi', 'Grid', 'SpMV(GFlops)', 'SymGS(GFlops)', 'Total(GFlops)', 'Final(GFlops)', 'Time(s)']

        self.grid    = grid 
        self.time    = time
        
        self.getopt() 

    def write_input(self):
        input_file = os.path.join(self.outdir, 'HPCG.in')

        with open(input_file, 'w') as input_fh:
            input_fh.write( 'HPCG input\n')
            input_fh.write( 'KISTI\n')
            input_fh.write(f'{" ".join(str(grid) for grid in self.grid)}\n')
            input_fh.write(f'{self.time}')

    def run(self): 
        # bug in 21.4
        os.environ['SINGULARITYENV_LD_LIBRARY_PATH'] = '/usr/local/cuda-11.2/targets/x86_64-linux/lib'
        
        self.output = f'HPCG-n{self.nodes}-g{self.ngpus}-t{self.omp}-{"x".join([str(grid) for grid in self.grid])}.out'
        
        super().run()

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

        self.result.append([self.nodes, self.ngpus, self.omp, grid, domain, SpMV, SymGS, total, final, time])

    def summary(self, sort=0, order='>'): 
        super().summary(sort, order)

        print('SpMV:  sparse matrix-vector multiplication')
        print('SymGS: symmetric Gauss-Seidel method')
        print('Total: GPU performance')
        print('Final: GPU + CPU initialization overhead')

    def getopt(self): 
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -g 256 256 256 -t 60 --omp 8',
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
                '    --omp            number of omp threads\n' ))
    
        # version string
        opt.add_argument('-h', '--help'   , action='help'                  , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                  version='%(prog)s '+self.version         , help=argparse.SUPPRESS)
        opt.add_argument('-g', '--grid'   , type=int, nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--time'   , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'  , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'  , type=int           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'    , type=int           , metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
