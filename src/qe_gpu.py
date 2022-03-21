#!/usr/bin/env python 

import os
import re
import logging
import argparse

from qe      import Qe
from bmt_mpi import BmtMpi
from gpu     import nvidia_smi, device_query, gpu_affinity

class QeGpu(Qe):
    def __init__(self, sif='', **kwargs): 
        super().__init__(**kwargs)

        self.name   = 'QE/GPU' 
        self.device = nvidia_smi(self.nodelist[0])

        self.sif    = sif

        # For GPU version  
        self.ntg    = 1 
        self.ndiag  = 1

        if sif: 
            self.name = 'QE/NGC'
            self.sif  = os.path.abspath(sif)
        
        # default number of GPUs
        if not self.mpi.gpu: 
            self.mpi.gpu  = len(self.device.keys()) 
            self.mpi.task = self.mpi.gpu

    def build(self): 
        if os.path.exists(self.bin):
            return
        
        self.check_prerequisite('hpc_sdk', '21.5')

        # determine cuda_cc and runtime 
        runtime, cuda_cc = device_query(self.nodelist[0], self.builddir)

        self.buildcmd += [
           f'cd {self.builddir}; tar xf q-e-qe-7.0.tar.gz',
          (f'cd {self.builddir}/q-e-qe-7.0/;' 
               f'./configure '
               f'--prefix={os.path.abspath(self.prefix)} '
               f'--with-cuda={os.environ["NVHPC_ROOT"]}/cuda/{runtime} '
               f'--with-cuda-cc={cuda_cc} '
               f'--with-cuda-runtime={runtime} '
                '--with-scalapack=no '
                '--enable-openmp; '
                'perl -pi -e "s/^(DFLAGS.*)/\$1 -D__GPU_MPI/" make.inc; '
            'make -j 16 pw; ' 
            'make -j 16 neb; '
            'make install' )]

        super(BmtMpi, self).build() 

    def run(self): 
        # Fortran 2003 standard regarding STOP
        self.mpi.env['NO_STOP_MESSAGE'] = 1

        # gpu selection
        self.mpi.env['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in range(0, self.mpi.gpu)]) 

        # singularity run 
        if self.sif: 
            self.check_prerequisite('nvidia'     , '450')
            self.check_prerequisite('openmpi'    , '3'  )
            self.check_prerequisite('singularity', '3.1')
            
            # bug
            self.mpi.env['SINGULARITYENV_NO_STOP_MESSAGE'] = 1

            self.bin = f'singularity run --env NO_STOP_MESSAGE=1 --nv {self.sif} pw.x '
        else: 
            self.check_prerequisite('hpc_sdk', '21.5')
        
        super().run()
