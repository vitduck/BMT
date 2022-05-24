#!/usr/bin/env python 

import os
import re
import logging
import argparse

from qe import Qe
from gpu import nvidia_smi, device_query, gpu_affinity
from utils import syscmd

class QeGpu(Qe):
    def __init__(self, cuda_aware=False, sif='', **kwargs): 
        super().__init__(**kwargs)

        self.name     = 'QE (GPU)' 
        self.device   = nvidia_smi()

        self.cuda_aware = cuda_aware
        self.sif        = sif

        # For GPU version  
        self.ntg      = 1 
        self.ndiag    = 1

        
        if sif: 
            self.name = 'QE (NGC)'
            self.sif  = os.path.abspath(sif)

        # default cuda visible devices
        if not self.mpi.cuda_devs: 
            self.mpi.cuda_devs = list(range(0, len(self.device.keys())))
        
        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.mpi.cuda_devs)
            self.mpi.task = self.mpi.gpu

        self.parser.description = 'QE Benchmark (GPU)'

    def build(self): 
        if os.path.exists(self.bin):
            return
        
        # determine cuda_cc and runtime 
        runtime, cuda_cc = device_query(self.builddir)

        # make.inc patch 
        patch = ( 
            'perl -pi -e "s/(cusolver)/\$1,curand/" make.inc;' ) 

        # __GPU_MPI 
        if self.cuda_aware: 
            patch += 'perl -pi -e "s/^(DFLAGS.*)/\$1 -D__GPU_MPI/" make.inc;'

        # system hangs: https://gitlab.com/QEF/q-e/-/issues/475
        self.buildcmd += [
           f'cd {self.builddir}; tar xf q-e-qe-6.8.tar.gz',
          (f'cd {self.builddir}/q-e-qe-6.8/;' 
               f'./configure '
               f'--prefix={os.path.abspath(self.prefix)} '
               f'--with-cuda={os.environ["CUDA_HOME"]} '
               f'--with-cuda-cc={cuda_cc} '
               f'--with-cuda-runtime={runtime} '
                '--with-scalapack=no; '
               f'{patch}'
            'make -j 16 pw; ' 
            'make -j 16 neb; '
            'make install' )]
        
        super(Qe, self).build() 

    def run(self): 
        # Fortran 2003 standard regarding STOP
        self.mpi.env['NO_STOP_MESSAGE'] = 1

        # This leads to segmentation fault !!
        #  if self.mpi.ucx: 
            #  self.mpi.env['UCX_MEMTYPE_CACHE'] = 'n'
    
        # bugs in HCOLL leads to hang at 1st SCF
        if self.cuda_aware:
            # NCCL backend leads to segmentation fault (non-critical)
            #  self.mpi.env['HCOLL_CUDA_BCOL'] = 'nccl'
            self.mpi.env['HCOLL_BCOL_P2P_CUDA_ZCOPY_ALLREDUCE_ALG'] = '2'

        # gpu selection
        self.mpi.env['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in self.mpi.cuda_devs[0:self.mpi.gpu]])

        # singularity run 
        if self.sif: 
            self.check_prerequisite('nvidia'     , '450')
            self.check_prerequisite('openmpi'    , '3'  )
            self.check_prerequisite('singularity', '3.1')
            
            # bug
            self.mpi.env['SINGULARITYENV_NO_STOP_MESSAGE'] = 1

            self.bin = f'singularity run --env NO_STOP_MESSAGE=1 --nv {self.sif} pw.x '
        
        super().run()

    def add_argument(self): 
        super().add_argument() 
        
        self.parser.add_argument('--gpu', type=int, help='number of GPU per node (default: $SLURM_GPUS_ON_NODE)')
