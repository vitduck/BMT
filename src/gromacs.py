#!/usr/bin/env python 

import os
import argparse

from bmt import Bmt

class Gromacs(Bmt):
    def __init__(self, input='stmv.tpr', gpu=[], thread=1, sif=None, prefix='./'):  
        super().__init__('gromacs')

        self.input  = input
        self.gpu    = gpu or self._parse_nvidia_smi() 
        self.thread = thread 
        self.sif    = None
        self.prefix = prefix
        
        self.bin    = f'{self.bindir}/gmx_mpi'

        # cmdline options 
        self.getopt() 
        
        self.check_prerequisite('gcc', '7.2' )
        self.check_prerequisite('cuda', '10.0')
        self.check_prerequisite('openmpi', '3.0')
        
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
                   f'-DCMAKE_INSTALL_PREFIX={os.path.abspath(self.prefix)};'
                'make -j 16;'
                'make install' )]

    def build(self): 
        if self.sif: 
            return 

        self.check_prerequisite('cmake', '3.16.3')

        super().build() 

    def run(self): 
        output = os.path.join(self.outdir, 'md.log')
        gpu_id = ''.join(self.gpu)

        # NVIDIA NGC (single-node only using thread-mpi)
        if self.sif: 
            self.check_prerequisite('nvidia', '450')

            self.runcmd = ( 
               f'ssh {self.host[0]} '
               f'"cd {self.rootdir}; module load singularity; ' 
               f'singularity run --nv {self.sif} '
               f'gmx mdrun -s {self.input} -g {output} -nsteps 10000 -tunepme -resethway -noconfout -ntmpi {self.ntasks} -ntomp {self.thread} -gpu_id {gpu_id}"' )
        else: 
            self.runcmd = ( 
               f'mpirun --hostfile {self.hostfile} '
               f'{self.bin} mdrun -s {self.input} -g {output} -nsteps 10000 -tunepme -resethway -noconfout -ntomp {self.thread} -gpu_id {gpu_id}' )
        
        self.syscmd(self.runcmd, verbose=1)

        # clean redundant file
        os.remove('ener.edr')

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
                '    --gpu            gpu selection\n'
                '    --thread         openmp thread\n'
                '    --sif            singulariy image\n'
                '    --prefix         bin/build/output directory\n' ))

        opt.add_argument('-h', '--help'   , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                            version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-i', '--input'  , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--gpu'    , type=str, nargs='+', metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--thread' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'    , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str           , metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
