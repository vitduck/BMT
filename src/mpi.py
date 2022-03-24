#!/usr/bin/env python3 

import os 

from gpu import gpu_affinity

class Mpi: 
    def __init__(self, nodelist=[], node=0, task=1, omp=0, gpu=0, bind=None, map=None, slurm=False, numa=False, verbose=0, hostfile='hostfile'):
        self.nodelist  = nodelist
        self.node      = node
        self.task      = task 
        self._omp      = omp
        self.gpu       = gpu
        self.bind      = bind 
        self.map       = map 
        self.slurm     = slurm
        self.numa      = numa 

        self.verbose   = verbose
        self.hostfile  = hostfile
        self.env       = {} 
        self.cuda_devs = []

        if os.environ['CUDA_VISIBLE_DEVICES']: 
            self.cuda_devs = os.environ['CUDA_VISIBLE_DEVICES'].split(',')

        if omp: 
            self.env['OMP_NUM_THREADS'] = omp

    @property 
    def omp(self): 
        return self._omp 

    @omp.setter
    def omp(self, number_of_threads): 
        self._omp = number_of_threads 

        self.env['OMP_NUM_THREADS'] = number_of_threads 
    
    def write_hostfile(self):
        pass

    def run(self): 
        cmd = [] 

        # srun
        if self.slurm:
            cmd += self.srun() 
        else:
            cmd += self.mpirun()

        # numaclt 
        if self.numa and self.gpu:
            cmd += self.numactl() 
        
        return " ".join(cmd) 

    def numactl(self): 
        cmd      = [] 
        affinity = []  

        for i in gpu_affinity()[0:self.gpu]: 
            for j in range(0, int(self.task/self.gpu)): 
                affinity.append(str(i))

        cmd += [
            'numactl '
               f'--cpunodebind={",".join(affinity)} '
               f'--membind={",".join(affinity)} ' ]

        return cmd

    def srun(self): 
        cmd = [ 
            'srun',
               f'-n {self.node*self.task}' ]
           
        if self.bind: 
            cmd.append(f'--cpu-bind={self.bind}')

        return cmd

    def mpirun(self): 
        pass
