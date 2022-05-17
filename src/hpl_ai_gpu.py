#!/usr/bin/env python3 

import os
import re
import argparse

from hpl_gpu import HplGpu
from gpu     import nvidia_smi, gpu_affinity, gpu_memory
from math    import sqrt

class HplAiGpu(HplGpu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name   = 'HPL-AI (NGC)'
    
        # NVIDIA-HPL-AI header
        self.header = [
            'node', 'task', 'gpu', 'omp', 
            'n', 'nb', 
            'p', 'q', 'bcast', 
            'rfact', 'ndiv', 'pfact', 'nbmin', 
            'status', 'perf(TFLOPS)', 'perf_irs(TFLOPS)','time(s)']
        
        self.parser.description  = 'HPL-AI Benchmark (GPU)'
   
    def hpl_opt(self): 
        return super().hpl_opt() + '--xhpl-ai'

    def parse(self): 
        with open(self.output, 'r') as output_fh:
            line = output_fh.readline()

            while line:
                if re.search('W[RC]', line):
                    ai, config, size, blocksize, p, q, time, gflops_half, refine, niter, gflops_mixed = line.split()

                    # passed/failed status
                    while True: 
                        status = output_fh.readline()
                        if re.search('(PASSED|FAILED)', status): 
                            status = status.split()[-1]
                            break

                    # split config into string, the first character has no meaning 
                    mu, ordering, depth, bcast, rfact, ndiv, pfact, nbmin = list(config)
                    
                    # hash key 
                    key = ",".join(map(str, [self.mpi.node, self.mpi.task, self.mpi.gpu, self.mpi.omp, size, blocksize, p, q, bcast, rfact, ndiv, pfact, nbmin, status]))
                    
                    # hash initialization
                    if not self.result[key]['gflops_half']: 
                        self.result[key]['gflops_half']  = [] 
                        self.result[key]['gflops_mixed'] = [] 
                        self.result[key]['time']         = [] 

                    self.result[key]['gflops_half'].append(float(gflops_half)/1000) 
                    self.result[key]['gflops_mixed'].append(float(gflops_mixed)/1000) 
                    self.result[key]['time' ].append( float(time)) 

                line = output_fh.readline()
 
    def summary(self): 
        super().summary()

        print('Perf:     half-precision performance (FP16)')
        print('Perf_IRS: mixed-precision performance (Iteractive Residual Solver)')
