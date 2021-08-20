#!/usr/bin/env python 

import os
import re
import logging
import argparse

from slurm import slurm_ntasks
from cpu   import cpu_info
from gpu   import gpu_id, gpu_info
from bmt   import Bmt

class Gromacs(Bmt):
    def __init__(self, input='stmv.tpr',nsteps=10000, tune_pme=0, nodes=0, ngpus=0, ntasks=0, omp=1, sif=None, prefix='./'):  
        super().__init__('gromacs')

        self.bin      = 'gmx_mpi'
        self.gpu_id   = gpu_id(self.host[0])

        self.input    = os.path.abspath(input)
        self.nsteps   = nsteps
        self.tune_pme = tune_pme
        self.nodes    = nodes  or len(self.host)
        self.ngpus    = ngpus  or len(self.gpu_id)
        self.ntasks   = ntasks or slurm_ntasks()
        self.omp      = omp
        self.sif      = sif
        self.prefix   = prefix
        self.header   = ['Node', 'Ngpu', 'Ntask', 'Thread', 'Perf(ns/day)']
        
        # cmdline options 
        self.getopt() 

        # sif aboslution path 
        if self.sif: 
            self.sif   = os.path.abspath(self.sif)
            self.nodes = 1 

        self.check_prerequisite('gcc', '7.2' )
        self.check_prerequisite('cuda', '10.0')
        self.check_prerequisite('openmpi', '3.0')
        
        cpu_info(self.host[0])
        gpu_info(self.host[0])

    def build(self): 
        if self.sif: 
            logging.info('Using NGC image')
            return 

        self.check_prerequisite('cmake', '3.16.3')
        
        self.buildcmd += [  
            f'wget http://ftp.gromacs.org/pub/gromacs/gromacs-2020.2.tar.gz -O {self.builddir}/gromacs-2020.2.tar.gz',
            f'cd {self.builddir}; tar xf gromacs-2020.2.tar.gz', 
           (f'cd {self.builddir}/gromacs-2020.2;'
                'mkdir build;'
                'cd build;'
                'cmake .. '  
                    '-DGMX_OPENMP=ON ' 
                    '-DGMX_MPI=ON ' 
                    '-DGMX_GPU=ON ' 
                    '-DGMX_SIMD=AVX2_256 '
                    '-DGMX_DOUBLE=OFF '
                    '-DGMX_FFT_LIBRARY=fftpack '
                   f'-DCMAKE_INSTALL_PREFIX={self.prefix};'
                'make -j 16;'
                'make install')]
        
        super().build() 

    def run(self): 
        self.mkoutdir()
        self.write_hostfile()

        self.output = (
           f'{os.path.splitext(os.path.basename(self.input))[0]}-'
           f'n{self.nodes}_'
           f'g{self.ngpus}_'
           f'p{self.ntasks}_'
           f't{self.omp}.log')

        gmx_opts = (
            'mdrun ' 
           f'-s {self.input} '
           f'-g {self.output} '
           f'-nsteps {str(self.nsteps)} '
            '-noconfout ' 
           f'-gpu_id {"".join([str(i) for i in range(0, self.ngpus)])} '
           f'-ntomp {self.omp} '
           f'-pin on ')
        
        # for real test with load-balancing 
        if self.tune_pme: 
            gmx_opts += '-tunepme -resethway'

        # NVIDIA NGC (single-node only using thread-mpi)
        if self.sif: 
            self.check_prerequisite('nvidia', '450')
            
            gmx_opts += f'-ntmpi {self.ntasks}'

            self.runcmd = ( 
               f'ssh {self.host[0]} '
               f'"cd {self.outdir}; module load singularity; ' 
               f'singularity run --nv {self.sif} '
               f'gmx {gmx_opts}"' )
        else: 
            self.runcmd = ( 
               f'mpirun --hostfile {self.hostfile} '
               f'{self.bin} {gmx_opts}' )
               
        super().run()

        # clean redundant files
        os.remove('ener.edr')

    def parse(self):
        with open(self.output, 'r') as fh:
            for line in fh:
                if re.search('Performance:', line):
                    self.result.append([self.nodes, self.ngpus, self.ntasks, self.omp, float(line.split()[1])])
        
    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -i stmv.tpr --sif gromacs-2020_2.sif',
            description     = 'GROMACS Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False)

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '-i, --input          input file\n'
                '    --nsteps         number of md steps\n'
                '    --tune_pme       optimize pme grids and shift workload to GPU\n'
                '    --nodes          number of node\n'
                '    --ngpus          number of gpus per node\n'
                '    --ntasks         number of mpi tasks per node\n'
                '    --omp            number of openmp thread\n'
                '    --sif            singulariy image\n'
                '    --prefix         bin/build/output directory\n' ))

        opt.add_argument('-h', '--help'     , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version'  , action='version', 
                                              version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-i', '--input'    , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--nsteps'   , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--tune_pme' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'    , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'    , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ntasks'   , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'      , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'      , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix'   , type=str           , metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
