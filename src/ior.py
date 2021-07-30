#/usr/bin/env python3

import os
import argparse

from bmt import Bmt

class Ior(Bmt):
    def __init__(self, prefix): 
        super().__init__('ior')

        self.prefix = prefix 

        self.check_prerequisite('openmpi', '3')

        self.buildcmd += [
           f'wget https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz -O {self.builddir}/ior-3.3.0.tar.gz',
           f'cd {self.builddir}; tar xf ior-3.3.0.tar.gz', 
          (f'cd {self.builddir}/ior-3.3.0;' 
            './configure '
               f'--prefix={os.path.abspath(self.prefix)} '
                'MPICC=mpicc ' 
               f'CPPFLAGS=-I{os.environ["MPI_ROOT"]}/include '
               f'LDFLAGS=-L{os.environ["MPI_ROOT"]}/lib;' 
            'make -j 8;' 
            'make install' )]
