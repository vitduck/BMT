#!/usr/bin/env python 

import os
import re
import logging
import argparse

from bmt import Bmt

class Gromacs(Bmt):
    def __init__(self, input='stmv.tpr', nsteps=10000, resetstep=0, gpudirect=False, **kwargs):
        super().__init__(**kwargs)

        self.name      = 'GROMACS'
        self.bin       = 'gmx_mpi'
        self.header    = ['Node', 'Ngpu', 'Ntask', 'Thread', 'Perf(ns/day)', 'Time(s)']

        self.input     = input
        self.nsteps    = nsteps
        self.resetstep = resetstep
        self.gpudirect = gpudirect

        self.getopt() 

        # default ntasks 
        if not self.ntasks: 
            self.ntasks = int(os.environ['SLURM_NTASKS_PER_NODE'])

        # reset perf measure at 80% mark of simulation
        if not self.resetstep: 
            self.resetstep = 1000*int(0.8*self.nsteps/1000)

    def build(self): 
        if os.path.exists(self.bin):
            return

        self.check_prerequisite('cmake'  , '3.16.3')
        self.check_prerequisite('gcc'    , '7.2'   )
        self.check_prerequisite('cuda'   , '10.0'  )
        self.check_prerequisite('openmpi', '3.0'   )

        self.buildcmd += [  
            f'wget --no-check-certificate http://ftp.gromacs.org/pub/gromacs/gromacs-2021.3.tar.gz -O {self.builddir}/gromacs-2021.3.tar.gz',
            f'cd {self.builddir}; tar xf gromacs-2021.3.tar.gz', 
           (f'cd {self.builddir}/gromacs-2021.3;'
                'mkdir build;'
                'cd build;'
                'cmake .. '  
                    '-DGMX_OPENMP=ON ' 
                    '-DGMX_MPI=ON ' 
                    '-DGMX_GPU=CUDA ' 
                    '-DGMX_SIMD=AVX2_256 '
                    '-DGMX_DOUBLE=OFF '
                    '-DGMX_FFT_LIBRARY=fftw3 '
                    '-DGMX_BUILD_OWN_FFTW=ON '
                   f'-DCMAKE_INSTALL_PREFIX={self.prefix};'
                'make -j 16;'
                'make install')]
        
        super().build() 

    def run(self): 
        self.input = os.path.abspath(self.input)

        self.mkoutdir()
        self.write_hostfile()

        # NVIDIA NGC (single-node only using thread-mpi)
        # Experimental support for GPUDirect implementation
        if self.sif: 
            self.nodes = 1 
            gmx_export = ''
            
            self.check_prerequisite('nvidia', '450')

            if self.gpudirect: 
                self.name   = self.name + '/GPUDIRECT'
                self.ntasks = self.ngpus 
                self.omp    = 4

                gmx_export  = ( 
                    'GMX_GPU_DD_COMMS=true '
                    'GMX_GPU_PME_PP_COMMS=true '
                    'GMX_FORCE_UPDATE_DEFAULT_GPU=true ' )
            
            self.runcmd = ( 
               f'ssh -oStrictHostKeyChecking=no {self.host[0]} ' 
               f'"cd {self.outdir}; '
                'module load singularity; ' 
               f'{gmx_export} '
               f'singularity run --nv {self.sif} '
               f'gmx {self._mdrun()}"' )
        else: 
            self.check_prerequisite('gcc'    , '7.2' )
            self.check_prerequisite('cuda'   , '10.0')
            self.check_prerequisite('openmpi', '3.0' )
            
            self.runcmd = ( 
               f'mpirun --hostfile {self.hostfile} --allow-run-as-root '
               f'{self.bin} {self._mdrun()}' )
       
        super().run()

        #  clean redundant files
        os.remove('ener.edr')

    def parse(self):
        with open(self.output, 'r') as fh:
            for line in fh:
                if re.search('Performance:', line):
                    perf = float(line.split()[1])
                if re.search('Time:', line):
                    time = float(line.split()[2])
                    
        self.result.append([self.nodes, self.ngpus, self.ntasks, self.omp, perf, time])

    def _mdrun(self): 
        self.output = (
           f'{os.path.splitext(os.path.basename(self.input))[0]}-'
           f'n{self.nodes}_'
           f'g{self.ngpus}_'
           f'p{self.ntasks}_'
           f't{self.omp}.log' )

        # gromacs MPI crashes unless thread is explicitly set to 1
        cmd = (
            'mdrun ' 
            '-noconfout ' 
           f'-s {self.input} '
           f'-g {self.output} '
           f'-gpu_id {"".join([str(i) for i in range(0, self.ngpus)])} '
           f'-nsteps {str(self.nsteps)} '
           f'-resetstep {self.resetstep} '
           f'-pin on '
           f'-ntomp {self.omp} ' )

        # gromacs thread-MPI requires -ntmpi
        if self.sif:
            cmd += ( 
               f'-ntmpi {self.ntasks} ' )

        if self.gpudirect: 
            cmd += (
                '-nb gpu '
                '-bonded gpu '
                '-pme gpu '
                '-npme 1 ' 
                '-nstlist 200 ' )

        return cmd

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -i stmv.tpr --nsteps 4000',
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
                '    --resetstep      start performance measurement\n'
                '    --gpudirect      enable experimental GPUDirect\n'
                '    --nodes          number of node\n'
                '    --ngpus          number of gpus per node\n'
                '    --ntasks         number of mpi tasks per node\n'
                '    --omp            number of openmp thread\n' ))

        opt.add_argument('-h', '--help'     , action='help'                    , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version'  , action='version', 
                                              version='%(prog)s '+self.version , help=argparse.SUPPRESS)
        opt.add_argument('-i', '--input'    , type=str            , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--nsteps'   , type=int            , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--resetstep', type=int            , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--gpudirect', action='store_true'              , help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'    , type=int            , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'    , type=int            , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--ntasks'   , type=int            , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'      , type=int            , metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
