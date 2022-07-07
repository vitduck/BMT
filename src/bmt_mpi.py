#!/usr/bin/env python3

import argparse

from bmt import Bmt

class BmtMpi(Bmt): 
    def __init__(self, mpi=None, **kwargs):
        super().__init__(**kwargs)
        
        self.mpi          = mpi 
        self.mpi.nodelist = self.nodelist

        # set default number of node
        if not self.mpi.node: 
            self.mpi.node = len(self.nodelist)

    def add_argument(self): 
        super().add_argument()

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
