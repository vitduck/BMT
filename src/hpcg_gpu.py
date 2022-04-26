#!/usr/bin/env python3 

import os
import re
import argparse

from bmt_mpi import BmtMpi
from gpu     import nvidia_smi, gpu_affinity

class HpcgGpu(BmtMpi): 
    def __init__(self, grid=[256, 256, 256], time=60, sif='', **kwargs):

        super().__init__(**kwargs)

        self.name   = 'HPCG/GPU'
        self.device = nvidia_smi()
        
        self.grid   = grid 
        self.time   = time
        self.sif    = sif

        if self.sif:
            self.name += '/NGC'
            self.sif   = os.path.abspath(sif)
            self.bin   = f'singularity run --nv {self.sif} hpcg.sh'

        # default cuda visible devices
        if not self.mpi.cuda_devs:
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu:
            self.mpi.gpu  = len(self.mpi.cuda_devs)
            self.mpi.task = self.mpi.gpu

        self.input   = 'HCPG.in'
        self.output  = ''

        self.header  = [
            'node', 'task', 'omp', 'mpi', 'grid', 
            'SpMV(GFlops)', 'SymGS(GFlops)', 'total(GFlops)', 'final(GFlops)', 'time(s)' ]

        self.parser.usage        = '%(prog)s -g 256 256 256 -t 60 --omp 8'
        self.parser.description  = 'HPCG benchmark'

        self.option.description += ( 
            '-h, --help           show this help message and exit\n'
            '-v, --version        show program\'s version number and exit\n'
            '-g, --grid           3-dimensional grid\n'
            '-t, --time           targeted run time\n' )
                
    def write_input(self):
        input_file = os.path.join(self.outdir, self.input)

        with open(input_file, 'w') as input_fh:
            input_fh.write( 'HPCG input\n')
            input_fh.write( 'KISTI\n')
            input_fh.write(f'{" ".join(str(grid) for grid in self.grid)}\n')
            input_fh.write(f'{self.time}')

    def run(self): 
        # bug in 21.4
        os.environ['SINGULARITYENV_LD_LIBRARY_PATH'] = '/usr/local/cuda-11.2/targets/x86_64-linux/lib'

        os.chdir(self.outdir)

        self.write_input()
        self.mpi.write_hostfile()

        self.runcmd = ( 
            f'{self.mpi.run()} '
            f'{self.bin} '
            f'--dat {self.input} '
            f'--cpu-cores-per-rank {self.mpi.omp} '
            f'--cpu-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])} '
            f'--mem-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])} '
            f'--gpu-affinity {":".join([str(i) for i in range(0, self.mpi.gpu)])} ' )

        self.output = f'HPCG-n{self.mpi.node}-t{self.mpi.task}-o{self.mpi.omp}-g{self.mpi.gpu}-{"x".join([str(grid) for grid in self.grid])}.out'

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

        key = ",".join(map(str, [self.mpi.node, self.mpi.task, self.mpi.omp, self.mpi.gpu, grid, domain]))

        if not self.result[key] ['SpMV']: 
            self.result[key]['SpMV']  = [] 
            self.result[key]['SymGS'] = [] 
            self.result[key]['total'] = [] 
            self.result[key]['final'] = [] 
            self.result[key]['time']  = [] 
        
        self.result[key]['SpMV'].append(SpMV) 
        self.result[key]['SymGS'].append(SymGS)
        self.result[key]['total'].append(total)
        self.result[key]['final'].append(final)
        self.result[key]['time'].append(time)

    def summary(self):
        super().summary()

        print('SpMV:  sparse matrix-vector multiplication')
        print('SymGS: symmetric Gauss-Seidel method')
        print('Total: GPU performance')
        print('Final: GPU + CPU initialization overhead')

    def getopt(self): 
        opt.add_argument('-g', '--grid', type=int, nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-t', '--time', type=int           , metavar='', help=argparse.SUPPRESS)

        super().getopt() 
