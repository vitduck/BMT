#!/usr/bin/env python3

import os
import re
import logging
import argparse

from bmt import Bmt

class Gromacs(Bmt):
    def __init__(self, input='stmv.tpr', nsteps=10000, resetstep=0, nstlist=0, pin='auto', pme='auto', update='auto', tunepme=False, gpudirect=False, **kwargs):
        super().__init__(**kwargs)

        if self.mpi.name == 'tMPI': 
            self.bin     = os.path.join(self.bindir, 'gmx')
            self.gmx_mpi = 'OFF'
            self.gmx_tmpi= 'ON'
        else:
            self.bin = os.path.join(self.bindir, 'gmx_mpi')
            self.gmx_mpi = 'ON'
            self.gmx_tmpi= 'OFF'

        self.name      = 'GROMACS'
        self.input     = os.path.abspath(input)
        self.nsteps    = nsteps
        self.resetstep = resetstep
        self.pin       = pin
        self.nstlist   = nstlist
        self.pme       = pme
        self.update    = update
        self.tunepme   = tunepme
        self.gpudirect = gpudirect
        self.gmx_gpu   = 'OFF'
        
        # for cpu
        self.nb        = 'cpu'
        self.bonded    = 'auto'
        self.npme      = -1

        self.src       = ['http://ftp.gromacs.org/pub/gromacs/gromacs-2021.3.tar.gz']

        self.header    = [
            'input', 'node', 'task', 'omp', 'gpu', 
            'nstlist', 'pme', 'update', 
            'mpi', 'gpudirect', 
            'nsteps', 'resetsteps',
            'perf(ns/day)', 'time(s)']

        # reset step count if tunepme is turned on 
        if self.tunepme and not self.resetstep: 
            self.resetstep = int(0.8*self.nsteps)

        # default ntasks 
        if not self.mpi.task:
            self.mpi.task = self.host['CPUs']

        self.parser.description  = 'GROMACS Benchmark'

    def build(self): 
        if os.path.exists(self.bin):
            return
        
        self.check_prerequisite('cmake', '3.16.3')
        self.check_prerequisite('gcc'  , '7.2'   )

        # MPI
        if self.mpi.name == 'OpenMPI': 
            self.check_prerequisite('openmpi', '3.0')

        self.buildcmd += [  
            f'cd {self.builddir}; tar xf gromacs-2021.3.tar.gz', 
           (f'cd {self.builddir}/gromacs-2021.3;'
                'mkdir build;'
                'cd build;'
                'cmake .. '  
                   f'-DCMAKE_INSTALL_PREFIX={self.prefix} '
                   f'-DGMX_THREAD_MPI={self.gmx_tmpi} '
                   f'-DGMX_MPI={self.gmx_mpi} '
                   f'-DGMX_GPU={self.gmx_gpu} ' 
                    '-DGMX_OPENMP=ON ' 
                    '-DGMX_SIMD=AUTO '
                    '-DGMX_DOUBLE=OFF '
                    '-DGMX_FFT_LIBRARY=fftw3 '
                    '-DGMX_BUILD_OWN_FFTW=ON; '
                'make -j 16;'
                'make install')]
        
        super().build() 

    def run(self): 
        os.chdir(self.outdir)

        self.mpi.write_hostfile()

        # GROMACS print output to stderr 
        self.runcmd = (
           f'{self.mpi.run()} '
               f'{self.bin} ' 
               f'{self.mdrun()} ' ) 

        self.output = (
           f'{os.path.splitext(os.path.basename(self.input))[0]}-'
               f'n{self.mpi.node}-'
               f't{self.mpi.task}-' 
               f'o{self.mpi.omp}-'
               f'l{self.nstlist}.log' )

        if self.mpi.gpu:
            self.output = re.sub(r'(-o\d+)', rf'\1-g{self.mpi.gpu}', self.output, 1)

        for i in range(1, self.count+1): 
            if self.count > 1: 
                self.output = re.sub('log(\.\d+)?', f'log.{i}', self.output)
                
            super().run(1) 

            os.rename('md.log', self.output)

            # clean redundant files
            if os.path.exists('ener.edr'): 
                os.remove('ener.edr')
   
    def mdrun(self): 
        # gromacs MPI crashes unless thread is explicitly set to 1
        cmd = [
            'mdrun', 
                '-noconfout',  
               f'-s {self.input}', 
               f'-nsteps {str(self.nsteps)}', 
               f'-resetstep {self.resetstep}', 
               f'-pme {self.pme}', 
               f'-update {self.update}', 
               f'-nb {self.nb}', 
               f'-bonded {self.bonded}', 
               f'-npme {self.npme}', 
               f'-ntomp {self.mpi.omp}',
               f'-nstlist {self.nstlist}', 
               f'-pin {self.pin}' ]
        
        if self.tunepme == False: 
            cmd.append('-notunepme')
        else:
            cmd.append('-tunepme')

        if self.mpi.name == 'tMPI': 
            cmd.append(f'-ntmpi {self.mpi.task}')
        else: 
            self.check_prerequisite('openmpi', '3.0')

        return " ".join(cmd)

    def parse(self):
        perf = '-'
        time = '-'

        with open('md.log', 'r') as fh:
            for line in fh:
                nstlist_regex = re.search('^Changing nstlist from \d+ to (\d+)', line)
                omp_regex     = re.search('^Using (\d+) OpenMP threads?', line) 
                perf_regex    = re.search('Performance:', line)
                time_regex    = re.search('Time:', line) 

                if omp_regex: 
                    omp = omp_regex.group(1)

                if nstlist_regex:
                    nstlist = nstlist_regex.group(1)

                if perf_regex:
                    perf = float(line.split()[1])

                if time_regex:
                    time = float(line.split()[2])
            
        key = ",".join(map(str, [
            os.path.basename(self.input), 
            self.mpi.node, self.mpi.task, omp, self.mpi.gpu, 
            nstlist, self.pme, self.update, 
            self.mpi.name, self.gpudirect, 
            self.nsteps, self.resetstep ]))

        if not self.result[key]['perf']: 
            self.result[key]['perf'] = [] 
            self.result[key]['time'] = [] 
        
        self.result[key]['perf'].append(perf) 
        self.result[key]['time'].append(time) 

    def add_argument(self):
        super().add_argument()

        self.parser.add_argument('--input'    , type=str, help='input file (default: None)')
        self.parser.add_argument('--nsteps'   , type=int, help='number of MD steps (default: 10000)')
        self.parser.add_argument('--resetstep', type=int, help='number of MD step after which perf counter is reseted (default: 0)')
        self.parser.add_argument('--node'     , type=int, help='number of nodes (default: $SLUM_NNODES)')
        self.parser.add_argument('--task'     , type=int, help='number of task per node (default: $SLURM_NTASK_PER_NODE)')
        self.parser.add_argument('--omp'      , type=int, help='number of OpenMP threads (default: 1)')
