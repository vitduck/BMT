#!/usr/bin/env python3 

import os
import re
import argparse

from math import sqrt
from env  import module_list
from gpu  import gpu_memory
from hpl  import Hpl

class Hpl_Ai(Hpl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name   = 'HPL-AI/NGC'
        self.header = ['Node', 'Ngpu', 'Thread', 'T/V', 'N', 'NB', 'P', 'Q', 'Status', 'Perf(Tflops)', 'Perf_IRS(Tflops)', 'Time(s)']
    
    def _matrix_size(self):
        tot_mem = self.nodes * self.ngpus * gpu_memory(self.host[0])

        if re.search("A100", self.gpu['0'][0]):
            self.size = [10000*int(sqrt(1.6*tot_mem*1024**2/8)/10000)]
        else: 
            self.size = [10000*int(sqrt(0.95*tot_mem*1024**2/8)/10000)]

    def ngc_cmd(self):
        return super().ngc_cmd() + '--xhpl-ai'

    def parse(self):
        with open(self.output, 'r') as output_fh:
            line = output_fh.readline()

            while line:
                if re.search('W[RC]', line):
                    ai, config, size, blocksize, p, q, time, gflops_half, refine, niter, gflops_mixed = line.split()

                    # passed/failed status
                    output_fh.readline()
                    status = output_fh.readline().split()[-1]

                    self.result.append([self.nodes, self.ngpus, self.omp, config, size, blocksize, p, q, status, float(gflops_half)/1000, float(gflops_mixed)/1000, time])
                
                line = output_fh.readline()

    def summary(self, sort=0, order='>'): 
        super().summary(sort, order)

        print('Perf:     half-precision performance (FP16)')
        print('Perf_IRS: mixed-precision performance (Iteractive Residual Solver)')
