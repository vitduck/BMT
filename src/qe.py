#!/usr/bin/env python 

import os
import re
import logging
import argparse

from env import module_list
from cpu import cpu_info
from gpu import gpu_id, gpu_info, device_query
from bmt import Bmt

class Qe(Bmt):
    def __init__(self, input='Ausurf_512.in', npool=1, nimage=1, neb=False, nodes=0, ngpus=0, ntasks=0, omp=1, sif=None, prefix='./'): 
        super().__init__('qe')

        self.bin    = 'pw.x'
        self.gpu_id = gpu_id(self.host[0])
        
        self.input  = input
        self.npool  = npool
        self.nimage = nimage
        self.neb    = neb
        self.nodes  = nodes  or len(self.host)
        self.ngpus  = ngpus  or len(self.gpu_id)
        self.ntasks = ntasks or self.ngpus
        self.omp    = omp
        self.sif    = sif 
        self.prefix = prefix 
        self.header = ['Node', 'Ngpu', 'Ntask', 'Thread', 'Npool', 'Nimage', 'Time(s)']

        self.getopt() 
        
        self.input  = os.path.abspath(self.input) 

        if self.neb: 
            self.bin = self.bin.replace('pw.x', 'neb.x')
        
        if self.sif: 
            self.sif = os.path.abspath(self.sif)

        cpu_info(self.host[0])
        gpu_info(self.host[0])
        module_list()

    def build(self): 
        if self.sif: 
            logging.info('Using NGC image')
            return 

        if os.path.exists(self.bin):
            return
                
        runtime, cuda_cc = device_query(self.host[0])

        self.check_prerequisite('hpc_sdk', '21.5')
        
        self.buildcmd += [
           f'wget https://gitlab.com/QEF/q-e/-/archive/develop/q-e-develop.tar.gz -O {self.builddir}/q-e-develop.tar.gz', 
           f'cd {self.builddir}; tar xf q-e-develop.tar.gz',
           (f'cd {self.builddir}/q-e-develop;' 
           f'./configure --prefix={os.path.abspath(self.prefix)} '
                '--enable-openmp '
               f'--with-cuda={os.environ["NVHPC_ROOT"]}/cuda/{runtime} '
               f'--with-cuda-cc={cuda_cc} '
               f'--with-cuda-runtime={runtime} '
                '--with-scalapack=yes CC=nvcc;'
            'make -j 8 pw;' 
            'make -j 8 neb;'
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
           f'-x CUDA_VISIBLE_DEVICES ' 
           f'-x NO_STOP_MESSAGE '
           f'--hostfile {self.hostfile} ')

        # NVIDIA NGC
        if self.sif: 
            self.check_prerequisite('nvidia', '450')
            self.check_prerequisite('openmpi', '3')
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
            usage           = '%(prog)s -i Si.in --sif QE-6.7.sif',
            description     = 'QE Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False)

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '-i, --input          input file\n' 
                '    --npool          k-points parallelization\n'
                '    --nimage         image parallelization\n'
                '    --neb            nudge elastic band calculation\n'
                '    --nodes          number of node\n'
                '    --ngpus          number of gpus per node\n'            
                '    --ntasks         number of mpi tasks per node\n'
                '    --omp            number of openmp thread\n'
                '    --sif            singulariy image\n'
                '    --prefix         bin/build/output directory\n' ))

        opt.add_argument('-h', '--help'   , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                            version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-i', '--input'  , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--npool'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--nimage' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--neb'    , action='store_true'             , help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ntasks' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'    , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'    , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str           , metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
