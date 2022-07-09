#!/usr/bin/env python3

import os
import argparse

from bmt import Bmt

class BmtMpi(Bmt): 
    def __init__(self, sif=None, mpi=None, **kwargs):
        super().__init__(**kwargs)

        self._sif = sif

        if sif: 
            self._sif = os.path.abspath(sif)

        self.mpi          = mpi 
        self.mpi.nodelist = self.nodelist
 
        # set default number of node
        if not self.mpi.node: 
            self.mpi.node = len(self.nodelist)

        # set default number of MPI tasks
        if not self.mpi.task: 
            self.mpi.task = os.environ['SLURM_NTASKS_PER_NODE']

        # set default number of OpenMP threads
        if not self.mpi.omp:
            self.mpi.omp = 1

    @property
    def sif(self): 
        return self._sif 

    @sif.setter
    def sif(self, sif): 
        self._sif = os.path.abspath(sif)

    def download(self): 
        if self.sif or os.path.exists(self.bin):
            return

        super().download()

    def runcmd(self): 
        runcmd = [] 

        # mpi options
        if self.mpi.name == 'OpenMPI' or self.mpi.name == 'IMPI': 
            self.mpi.write_hostfile()

            runcmd = [self.mpi.runcmd(), self.execmd()] 
            
            # numactl 
            if self.mpi.numa: 
                runcmd.insert(1,self.mpi.numactl())
        else: 
            runcmd = [self.execmd()]

        # singularity 
        if self.sif: 
            runcmd.insert(-1, ['singularity', 'run', f'--nv {self.sif}'])

        return [runcmd]

    def execmd(self): 
        pass

    def add_argument(self): 
        super().add_argument()

        self.parser.add_argument('--sif' , type=str, help='path to singularity image')
        self.parser.add_argument('--node', type=int, help='number of nodes (default: $SLUM_NNODES)')
        self.parser.add_argument('--task', type=int, help='number of task per node (default: $SLURM_NTASK_PER_NODE)') 
        self.parser.add_argument('--omp' , type=int, help='number of OpenMP threads (default: 1)')
        self.parser.add_argument('--gpu' , type=int, help='number of GPU per node (default: $SLURM_GPUS_ON_NODE)')

    def getopt(self): 
        self.add_argument() 

        args = vars(self.parser.parse_args())
        
        for opt in args:   
            if args[opt]: 
                # Pass attributes to MPI role
                if opt == 'node' or opt == 'task' or opt == 'omp' or opt == 'gpu': 
                    setattr(self.mpi, opt, args[opt]) 
                else: 
                    setattr(self, opt, args[opt]) 
