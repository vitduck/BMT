#!/usr/bin/env python 

import os
import re
import logging
import argparse

from env import module_list
from gpu import device_query
from bmt import Bmt

class Qe(Bmt):
    def __init__(self, input='Ausurf_512.in', npool=1, nimage=1, neb=False, **kwargs): 
        super().__init__(**kwargs)

        self.name   = 'QE'
        self.bin    = 'pw.x'
        self.header = ['Node', 'Ngpu', 'Ntask', 'Thread', 'Npool', 'Nimage', 'Time(s)']

        self.input  = os.path.abspath(input)
        self.npool  = npool
        self.nimage = nimage
        self.neb    = neb

        self.getopt() 

        # default ntasks 
        if not self.ntasks: 
            self.ntasks = self.ngpus
        
        if self.neb: 
            self.name = self.name + '/NEB'
            self.bin  = self.bin.replace('pw.x', 'neb.x')
        
    def build(self): 
        if os.path.exists(self.bin):
            return
                
        runtime, cuda_cc = device_query(self.host[0])

        self.check_prerequisite('hpc_sdk', '21.5')
       
        # test 
        self.buildcmd += [
           f'wget https://gitlab.com/QEF/q-e/-/archive/develop/q-e-develop.tar.gz -O {self.builddir}/q-e-develop.tar.gz', 
           f'cd {self.builddir}; tar xf q-e-develop.tar.gz',
           (f'cd {self.builddir}/q-e-develop;' 
           f'./configure --prefix={os.path.abspath(self.prefix)} '
                '--enable-openmp '
               f'--with-cuda={os.environ["NVHPC_ROOT"]}/cuda/{runtime} '
               f'--with-cuda-cc={cuda_cc} '
               f'--with-cuda-runtime={runtime}; '
            'perl -pi -e "s/^(DFLAGS.*)/\$1 -D__GPU_MPI/" make.inc; '
            'make -j 8 pw; ' 
            'make -j 8 neb; '
            'make install')]

        super().build() 

    def run(self): 
        self.mkoutdir()
        self.write_hostfile()

        os.environ['NO_STOP_MESSAGE']      = 'yes'
        os.environ['OMP_NUM_THREADS']      = str(self.omp)
        os.environ['ESPRESSO_PSEUDO']      = os.path.dirname(self.input)
        os.environ['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in range(0, self.ngpus)])
        
        self.output = (
           f'{os.path.splitext(os.path.basename(self.input))[0]}-'
           f'n{self.nodes}_'
           f'g{self.ngpus}_'
           f'p{self.ntasks}_'
           f't{self.omp}_'
           f'k{self.npool}_'
           f'i{self.nimage}.out')

        # pass CUDA_VISIBLE_DEVICES to remote host
        self.runcmd = ( 
            'mpirun '
            '--allow-run-as-root '
           f'-x CUDA_VISIBLE_DEVICES ' 
           f'-x NO_STOP_MESSAGE '
           f'--hostfile {self.hostfile} ')

        # NVIDIA NGC
        if self.sif: 
            self.check_prerequisite('nvidia'     , '450')
            self.check_prerequisite('openmpi'    , '3'  )
            self.check_prerequisite('singularity', '3.1')

            self.runcmd += (
                f'singularity run --nv {os.path.abspath(self.sif)} '
                f'pw.x -input {self.input} -npool {self.npool}' )
        else: 
            self.check_prerequisite('hpc_sdk', '21.5')
            self.runcmd += f'{self.bin} -input {self.input} -npool {self.npool} -nimage {self.nimage}'
        
        super().run(1) 

    def parse(self): 
        with open(self.output, 'r') as fh:
            regex = re.compile('(?:PWSCF|NEB)\s+\:.*CPU\s*(?:(.+?)m)?\s*(.+?)s')

            for line in fh:
                result = regex.search(line)
                if result:
                    minute, second = result.groups()
                    if not minute: 
                        minute = 0.0
                    exit

        self.result.append([self.nodes, self.ngpus, self.ntasks, self.omp, self.npool, self.nimage, 60*float(minute)+float(second)])

    def getopt(self): 
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -i Si.in',
            description     = 'QE Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False)

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '    --npool          k-points parallelization\n'
                '    --nimage         image parallelization\n'
                '    --neb            nudge elastic band calculation\n'
                '    --nodes          number of node\n'
                '    --ngpus          number of gpus per node\n'            
                '    --ntasks         number of MPI tasks per node\n'
                '    --omp            number of OpenMP thread\n' ))

        opt.add_argument('-h', '--help'   , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                  version='%(prog)s '+self.version          , help=argparse.SUPPRESS)
        opt.add_argument(      '--npool'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--nimage' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--neb'    , action='store_true'             , help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ntasks' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'    , type=int           , metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
