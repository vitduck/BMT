#!/usr/bin/env python3 

import os
import re
import logging
import argparse

from bmt_mpi import BmtMpi

class Qe(BmtMpi):
    def __init__(self, input='Ausurf_512.in', npool=1, ntg=1, ndiag=1, nimage=1, neb=False, **kwargs): 
        super().__init__(**kwargs)

        self.name   = 'QE'
        self.bin    = os.path.join(self.bindir, 'pw.x')

        self.input  = os.path.abspath(input)
        self.npool  = npool
        self.ntg    = ntg
        self.ndiag  = ndiag
        self.nimage = nimage
        self.neb    = neb

        self.src    = ['https://gitlab.com/QEF/q-e/-/archive/qe-6.8/q-e-qe-6.8.tar.gz'] 

        self.header = ['input', 'node', 'task', 'omp', 'gpu', 'nimage', 'npool', 'ntg', 'ndiag', 'time(s)']
        
        # cmdline option
        self.parser.usage        = '%(prog)s -i Si.in'
        self.parser.description  = 'QE Benchmark'

        self.option.description += (
            '    --npool          k-points parallelization\n'
            '    --ntg            planewave parallelization\n'
            '    --ndiag          linear algebra parallelization\n'
            '    --nimage         image parallelization\n'
            '    --neb            nudge elastic band calculation\n' )

    def build(self): 
        if os.path.exists(self.bin):
            return
        
        # intel-mkl
        scalapack = 'yes'
        if os.environ.get('FC') == 'ifort':  
            scalapack = 'intel'
        
        self.buildcmd += [
            f'cd {self.builddir}; tar xf q-e-qe-6.8.tar.gz',
           (f'cd {self.builddir}/q-e-qe-6.8/;' 
               f'./configure '
                   f'--prefix={os.path.abspath(self.prefix)} '
                   f'--with-scalapack={scalapack} '
                    '--enable-openmp; '
                'make -j 16 pw; ' 
                'make -j 16 neb; '
                'make install')]
        
        super().build() 

    def run(self): 
        os.chdir(self.outdir)

        self.mpi.write_hostfile()
        
        # Fortran 2003 standard regarding STOP (PGI)
        # Unfortunately this no longer works with NVIDIA_HPC_SDK
        self.mpi.env['NO_STOP_MESSAGE'] = 1
        self.mpi.env['ESPRESSO_TMPDIR'] = self.outdir
        self.mpi.env['ESPRESSO_PSEUDO'] = os.path.dirname(self.input)

        # NEB calculation
        #  if self.neb: 
            #  self.name = self.name + '/NEB'
            #  self.bin  = os.path.join(self.bindir, 'neb.x')

        self.runcmd = (
            f'{self.mpi.run()} '  
               f'{self.bin} ' 
                   f'-input  {self.input} ' 
                   f'-nimage {self.nimage} '
                   f'-npool  {self.npool} ' 
                   f'-ndiag  {self.ndiag} ' )

        # Pencil decomposition 
        # This is an undocmmented option
        if self.ntg > 1: 
            self.runcmd += (
                f'-pd true '
                f'-ntg {self.ntg}' )
        
        self.output = ( 
           f'{os.path.splitext(os.path.basename(self.input))[0]}-'
                f'n{self.mpi.node}-'
                f't{self.mpi.task}-' 
                f'o{self.mpi.omp}-'
                f'ni{self.nimage}-' 
                f'nk{self.npool}-'
                f'nt{self.ntg}-'
                f'nd{self.ndiag}.out' )

        if self.mpi.gpu: 
            self.output = re.sub(r'(-o\d+)', rf'\1-g{self.mpi.gpu}', self.output, 1)

        for i in range(1, self.count+1): 
            if self.count > 1: 
                self.output = re.sub('out(\.\d+)?', f'out.{i}', self.output)

            super().run(1) 

    def parse(self): 
        key = ",".join(map(str, [
            os.path.basename(self.input), 
            self.mpi.node, self.mpi.task, self.mpi.omp, self.mpi.gpu,
            self.nimage, self.npool, self.ntg, self.ndiag ]))

        with open(self.output, 'r') as fh:
            regex = re.compile('(?:PWSCF|NEB)\s+\:.*CPU\s*(?:(.+?)m)?\s*(.+?)s')

            for line in fh:
                result = regex.search(line)

                if result:
                    minute, second = result.groups()
                    if not minute: 
                        minute = 0.0
                    exit

        if not self.result[key]['time']: 
            self.result[key]['time'] = [] 

        self.result[key]['time'].append(60*float(minute)+float(second))

    def getopt(self): 
        self.option.add_argument('--npool' , type=int           , metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--ntg'   , type=int           , metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--ndiag' , type=int           , metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--nimage', type=int           , metavar='' , help=argparse.SUPPRESS)
        self.option.add_argument('--neb'   , action='store_true'             , help=argparse.SUPPRESS)
        
        super().getopt()
