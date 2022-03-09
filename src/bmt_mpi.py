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

        # set default number of task 
        if not self.mpi.task: 
            self.mpi.task = self.host['CPUs']

        # cmdline options
        self.option.description += (
            '    --node           number of nodes\n'
            '    --task           number of MPI tasks per node\n' )

    @Bmt.args.setter 
    def args(self, args): 
        self._args = args 

        for opt in args:   
            if args[opt]: 
                # Pass attributes to MPI role
                if opt == 'node' or opt == 'task' or opt == 'omp': 
                    setattr(self.mpi, opt, args[opt]) 
                else: 
                    setattr(self, opt, args[opt]) 

    def getopt(self): 
        self.option.add_argument('--node', type=int, metavar='', help=argparse.SUPPRESS)
        self.option.add_argument('--task', type=int, metavar='', help=argparse.SUPPRESS)

        super().getopt() 
