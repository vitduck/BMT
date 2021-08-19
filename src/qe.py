#!/usr/bin/env python 

import os
import re
import logging
import argparse

from utils import init_gpu, device_query, syscmd
from bmt   import Bmt

class Qe(Bmt):
    def __init__(self, input='Ausurf.in', npool=1, nodes=0, ngpus=0, ntasks=0, omp=1, sif=None, prefix='./'): 
        super().__init__('qe')

        self.bin    = 'pw.x'
        self.gpu_id = init_gpu(self.host[0])
        
        self.input  = os.path.abspath(input)
        self.npool  = npool
        self.nodes  = nodes  or len(self.host)
        self.ngpus  = ngpus  or len(self.gpu_id)
        self.ntasks = ntasks or self.ngpus
        self.omp    = omp
        self.sif    = sif 
        self.prefix = prefix 
        self.header = ['Node', 'Ngpu', 'Ntask', 'Thread', 'Npool', 'Time(s)']

        self.getopt() 

        if self.sif: 
            self.sif = os.path.abspath(self.sif)

        #  self.check_prerequisite('hpc_sdk', '21.5')

    def build(self): 
        if self.sif: 
            logging.info('Using NGC image')
            return 
                
        runtime, cuda_cc = device_query(self.host[0])

        # HPC_SDK
        self.buildcmd += [
           f'wget https://gitlab.com/QEF/q-e/-/archive/develop/q-e-develop.tar.gz -O {self.builddir}/q-e-develop.tar.gz', 
           f'cd {self.builddir}; tar xf q-e-develop.tar.gz',
           (f'cd {self.builddir}/q-e-develop;' 
           f'./configure --prefix={os.path.abspath(self.prefix)} '
                '--enable-openmp '
               f'--with-cuda={os.environ["NVHPC_ROOT"]}/cuda/{runtime} '
               f'--with-cuda-cc={cuda_cc} '
               f'--with-cuda-runtime={runtime} '
                '--with-scalapack=no CC=nvcc;'
            'make -j 16 pw;' 
            'make install')]

        super().build() 

    def run(self): 
        self.mkoutdir()
        self.write_hostfile()

        os.environ['NO_STOP_MESSAGES']     = '1'
        os.environ['OMP_NUM_THREADS' ]     = str(self.omp)
        os.environ['ESPRESSO_PSEUDO' ]     = os.path.dirname(self.input)
        os.environ['CUDA_VISIBLE_DEVICES'] = ",".join([str(i) for i in range(0, self.ngpus)])
        
        self.output = (
           f'{os.path.splitext(os.path.basename(self.input))[0]}-'
           f'n{self.nodes}_'
           f'g{self.ngpus}_'
           f'p{self.ntasks}_'
           f't{self.omp}_'
           f'l{self.npool}.out')

        # pass CUDA_VISIBLE_DEVICES to remote host
        self.runcmd = ( 
            'mpirun '
           f'--hostfile {self.hostfile} '
           f'-x CUDA_VISIBLE_DEVICES ' )

        # NVIDIA NGC
        if self.sif: 
            self.check_prerequisite('nvidia', '450')
            self.check_prerequisite('singularity', '3.1')

            self.runcmd += (
                f'singularity run --nv {os.path.abspath(self.sif)} '
                f'pw.x -input {self.input} -npool {self.npool}' )
        else: 
            self.runcmd += f'{self.bin} -input {self.input} -npool {self.npool}'
        
        super().run(1) 

    def parse(self): 
        with open(self.output, 'r') as fh:
            regex = re.compile('PWSCF\s+\:.*CPU\s*(.+?)m\s*(.+?)s')
            for line in fh:
                result = regex.search(line)
                if result:
                    minute, second = result.groups()
                    exit

        self.result.append([self.nodes, self.ngpus, self.ntasks, self.omp, self.npool, 60*float(minute)+float(second)])

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
        opt.add_argument(      '--nodes'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ntasks' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'    , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'    , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str           , metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
