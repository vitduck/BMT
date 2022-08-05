#!/usr/bin/env python3 

import os
import re
import argparse

from bmt_mpi import BmtMpi
from gpu     import nvidia_smi, gpu_affinity

class Hpcg(BmtMpi):
    def __init__(self, grid=[256, 256, 256], time=60, **kwargs):

        super().__init__(**kwargs)

        self.name   = 'HPCG'
        
        self.grid   = grid 
        self.time   = time

        self.input   = 'HCPG.in'
        self.output  = ''

        self.header  = [
            'node', 'task', 'omp', 'gpu', 'mpi', 'grid', 
            'SpMV(GFlops)', 'SymGS(GFlops)', 'total(GFlops)', 'final(GFlops)', 'time(s)' ]

        self.parser.description  = 'HPCG benchmark'

    def write_input(self):
        input_file = os.path.join(self.outdir, self.input)

        with open(input_file, 'w') as input_fh:
            input_fh.write( 'HPCG input\n')
            input_fh.write( 'KISTI\n')
            input_fh.write(f'{" ".join(str(grid) for grid in self.grid)}\n')
            input_fh.write(f'{self.time}')

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

    def add_argument(self): 
        super().add_argument()

        self.parser.add_argument('--grid', type=int, nargs=3, metavar=('NX','NY','NZ'), help='3d grid (default: 256x256x256)')
        self.parser.add_argument('--time', type=int, help='simulation time (default: 60s)')
