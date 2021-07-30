#!/usr/bin/env python 

import os
import re
import argparse

from bmt import Bmt

class Qe(Bmt):
    def __init__(self, input='Ausurf.in', npool=1, gpu=[], thread=4, sif=None, prefix='./'): 
        super().__init__('qe')

        self.input  = input 
        self.npool  = 1
        self.gpu    = gpu or self._parse_nvidia_smi() 
        self.thread = 4 
        self.sif    = sif
        self.prefix = prefix 

        self.bin    = f'{self.bindir}/pw.x'

        # cmdline options
        self.getopt() 
        
        self.output = os.path.basename(self.input).replace('.in', '.out')
        self.ntasks = len(self.gpu) 

        #  self.check_prerequisite('hpc_sdk', '21.0')
        self.check_prerequisite('pgi', '18.0')
        self.check_prerequisite('cuda', '10.0')
        self.check_prerequisite('openmpi', '3.0')

        # using deviceQuerry from CUDA samples
        runtime, compute = self._device_querry() 

        # HPC_SDK
        #  self.buildcmd += [  
           #  f'wget https://gitlab.com/QEF/q-e-gpu/-/archive/qe-gpu-6.7-ngc/q-e-gpu-qe-gpu-6.7-ngc.tar.gz -O {self.builddir}/q-e-gpu-qe-gpu-6.7-ngc.tar.gz', 
           #  f'cd {self.builddir}; tar xf q-e-gpu-qe-gpu-6.7-ngc.tar.gz',
           # (f'cd {self.builddir}/q-e-gpu-qe-gpu-6.7-ngc;'
           #  f'./configure --prefix={os.path.abspath(self.prefix)} '
                #  '--enable-openmp '
               #  f'--with-cuda={os.environ["NVHPC_ROOT"]}/cuda '
               #  f'--with-cuda-cc={compute} '
               #  f'--with-cuda-runtime={runtime} '
                #  '--with-scalapack=no;'
            #  'make -j 16 pw;' 
            #  'make install' )]
        
        self.buildcmd += [
           f'wget https://gitlab.com/QEF/q-e-gpu/-/archive/qe-gpu-6.7/q-e-gpu-qe-gpu-6.7.tar.gz -O {self.builddir}/q-e-gpu-qe-gpu-6.7.tar.gz',
           f'cd {self.builddir}; tar xf q-e-gpu-qe-gpu-6.7.tar.gz',
          (f'cd {self.builddir}/q-e-gpu-qe-gpu-6.7;'
           f'./configure --prefix={os.path.abspath(self.prefix)} '
                '--enable-openmp '
               f'--with-cuda={os.environ["CUDADIR"]} '
               f'--with-cuda-cc={compute} '
               f'--with-cuda-runtime={runtime} '
                '--with-scalapack=no;'
            'make -j 16 pw;'
            'make install' )]

    def build(self): 
        if self.sif: 
            return 
                
        super().build() 

    def run(self): 
        os.environ['NO_STOP_MESSAGE'] = 'yes' 
        os.environ['OMP_NUM_THREADS'] = str(self.thread)
        os.environ['ESPRESSO_PSEUDO'] = os.path.dirname(self.input)
        os.environ['ESPRESSO_TMPDIR'] = self.outdir

        self.runcmd = ( 
            f'{self.gpu_selection()} ' 
            f'mpirun --hostfile {self.hostfile} ')

        # NVIDIA NGC
        if self.sif: 
            self.check_prerequisite('nvidia', '450')
            self.check_prerequisite('singularity', '3.1')

            self.runcmd += (
                f'singularity run --nv {self.sif} '
                f'pw.x -input {self.input} -npool {self.npool}' )
        else: 
            self.runcmd += f'{self.bin} -input {self.input} -npool {self.npool}'

        super().run()
    
    def getopt(self): 
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -i Si.in --sif QE-6.7.sif',
            description     = 'QE Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False )

        opt = parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n'
                '-i, --input          input file\n' 
                '    --npool          k-points parallelization\n'
                '    --gpu            gpu selection\n'
                '    --thread         openmp thread\n'
                '    --sif            singulariy image\n'
                '    --prefix         bin/build/output directory\n' ))

        opt.add_argument('-h', '--help'   , action='help'                   , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version', action='version', 
                                            version='%(prog)s '+self.version, help=argparse.SUPPRESS)
        opt.add_argument('-i', '--input'  , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--npool'  , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--gpu'    , type=str, nargs='+', metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--thread' , type=int           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'    , type=str           , metavar='' , help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix' , type=str           , metavar='' , help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())

    def _device_querry(self): 
        # HPC_SDK
        #  querry = self.syscmd(
            #  f'cp {os.environ["NVHPC_ROOT"]}/examples/CUDA-Fortran/SDK/deviceQuery/* .;'
            #  f'make' )

        querry = self.syscmd( 
            f'cp {os.environ["CUDADIR"]}/samples/1_Utilities/deviceQuery/deviceQuery.cpp .;'
            f'nvcc -I{os.environ["CUDADIR"]}/samples/common/inc deviceQuery.cpp;'
            './a.out' )
         
        for line in querry.splitlines():
            # HPC_SDK 
            #  if re.search('Runtime version', line): 
                #  runtime = line.split()[-1].strip('0')
            
            #  if re.search('Compute Capability', line): 
                #  cuda_cc = line.split()[-1].replace('.', '')
                #  break

            if re.search('\/ Runtime Version', line): 
                runtime = line.split()[-1]

            if re.search('Minor version number', line): 
                cuda_cc = line.split()[-1].replace('.', '')
                break

        # HPC_SDK
        #  os.remove('Makefile')
        #  os.remove('deviceQuery.cuf')
        #  os.remove('deviceQuery.out')

        # clean up 
        os.remove('deviceQuery.cpp')
        os.remove('a.out')

        return runtime, cuda_cc
