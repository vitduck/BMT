#!/usr/bin/env python3 

import os
import re
import argparse

from hpl  import Hpl
from gpu  import nvidia_smi, gpu_affinity, gpu_memory
from math import sqrt

class HplCuda(Hpl): 
    def __init__(self, ai=False, **kwargs):
        super().__init__(**kwargs)

        self.name   = 'HPL/GPU/CUDA' 
        self.ai     = ai

        self.device = nvidia_smi()
        self.bin    = os.path.join(self.bindir,'hpl.sh') 

        # default cuda visible devices
        if not self.mpi.cuda_devs: 
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))

        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)
            self.mpi.task = self.mpi.gpu

        # NVIDIA-HPL parameters 
        self.blocksize = [288]
        self.l1        = 1

        # HPL-AI 
        self.parser.description  = 'HPL Benchmark (NVIDIA)'

    def run(self):
        self.check_prerequisite('openmpi' , '4'     )
        self.check_prerequisite('connectx', '4'     )
        self.check_prerequisite('nvidia'  , '450.36')

        if self.sif: 
            self.name += '/NGC'

        super().run()

    def execmd(self): 
        if self.sif:
            self.bin   = 'hpl.sh'

        cmd = [ 
            self.bin,
               f'--dat {self.input}', 
               f'--cpu-cores-per-rank {self.mpi.omp}',  
               f'--cpu-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])}', 
               f'--mem-affinity {":".join(gpu_affinity()[0:self.mpi.gpu])}', 
               f'--gpu-affinity {":".join([str(i) for i in range(0, self.mpi.gpu)])}' ]
        
        # ucx transport (2021.4) 
        if self.mpi.ucx: 
            cmd += [
                f'--ucx-tls {",".join(self.mpi.ucx)}' ]

        # HPL-AI 
        if self.ai: 
            cmd += ['--xhpl-ai']

        return cmd

    def parse(self): 
        # HPL-AI
        if self.ai:
            self.header = [
                'node', 'task', 'omp', 'gpu',
                'n', 'nb', 
                'p', 'q', 'bcast', 
                'rfact', 'ndiv', 'pfact', 'nbmin', 
                'status', 'perf(TFLOPS)', 'perf_irs(TFLOPS)','time(s)']

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
                        key = ",".join(
                            map(str, [
                                self.mpi.node, self.mpi.task, self.mpi.omp, self.mpi.gpu, 
                                size, blocksize, p, q, bcast,
                                rfact, ndiv, pfact, nbmin, status]))

                        # hash initialization
                        if not self.result[key]['gflops_half']:
                            self.result[key]['gflops_half']  = []
                            self.result[key]['gflops_mixed'] = []
                            self.result[key]['time']         = []

                        self.result[key]['gflops_half'].append(float(gflops_half)/1000)
                        self.result[key]['gflops_mixed'].append(float(gflops_mixed)/1000)
                        self.result[key]['time' ].append( float(time))

                    line = output_fh.readline()
        else: 
            super().parse()

    def total_device(self): 
        return self.mpi.node*self.mpi.gpu

    def total_memory(self): 
        return self.total_device()*gpu_memory()*1024**2

    def add_argument(self):
        super().add_argument()
        
        self.parser.add_argument('--ai', action='store_true', help='enable HPL-AI benchmark')

    def summary(self): 
        super().summary() 

        # HPL-AI
        if self.ai: 
            print('Perf:     half-precision performance (FP16)')
            print('Perf_IRS: mixed-precision performance (Iteractive Residual Solver)')
