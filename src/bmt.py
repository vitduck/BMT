#!/usr/bin/env python3

import os 
import re
import sys
import inspect
import logging
import packaging.version
import datetime
import prerequisite

from tabulate    import tabulate
from statistics  import mean
from pprint      import pprint

from cpu         import lscpu, cpu_info
from gpu         import gpu_info
from env         import module_list
from utils       import syscmd, autovivification
from ssh         import ssh_cmd
from slurm       import slurm_nodelist

class Bmt: 
    version = '0.8'
    
    # initialize root logger 
    logging.basicConfig( 
        stream  = sys.stderr,
        level   = os.environ.get('LOGLEVEL', 'INFO').upper(), 
        format  = '# %(message)s')

    def __init__(self, name, prefix='./', count=1, nnodes=0, ntasks=0, omp=0, ngpus=0, mpi=None):
        # sys info
        self.nodelist = slurm_nodelist()

        self.host     = lscpu(self.nodelist[0])
        self.device   = {} 

        self.name     = name
        self.prefix   = os.path.abspath(prefix)
        self.count    = count

        self._nnodes  = nnodes or len(self.nodelist)
        self._ntasks  = ntasks or self.host['CPUs']
        self._ngpus   = ngpus  
        self._omp     = omp
        self._args    = {} 

        self.mpi      = mpi
        
        self.bin      = ''
        self.input    = ''
        self.output   = ''
        self.hostfile = 'hostfile'
        self.rootdir  = os.path.dirname(inspect.stack()[-1][1])
        self.bindir   = os.path.join(self.prefix, 'bin')
        self.builddir = os.path.join(self.prefix, 'build')
        self.outdir   = os.path.join(self.prefix, 'output', datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S"))

        self.src       = []
        self.buildcmd  = []
        self.runcmd    = ''

        self.header    = []
        self.table     = [] 
        self.result    = autovivification() 

        # Propagate parameters to mpi
        if mpi:
            self.mpi.nodelist = self.nodelist
            self.mpi.nnodes   = self._nnodes 
            self.mpi.ntasks   = self._ntasks 
            self.mpi.omp      = self._omp

        os.makedirs(self.builddir, exist_ok=True) 
        os.makedirs(self.bindir  , exist_ok=True) 

    # trigger: number of nodes 
    @property 
    def nnodes(self): 
        return self._nnodes 

    @nnodes.setter
    def nnodes(self, number_of_nodes): 
        self._nnodes = number_of_nodes 

        if self.mpi: 
            self.mpi.nnodes = number_of_nodes 

    # trigger: number of tasks 
    @property 
    def ntasks(self): 
        return self._ntasks 

    @ntasks.setter
    def ntasks(self, number_of_tasks): 
        self._ntasks = number_of_tasks 

        if self.mpi: 
            self.mpi.ntasks = number_of_tasks

    # trigger: number of omp threads 
    @property 
    def omp(self): 
        return self._omp 

    @omp.setter
    def omp(self, number_of_threads): 
        self._omp = number_of_threads 

        if self.mpi: 
            self.mpi.omp = number_of_threads 

    # trigger: default number of gpus 
    @property 
    def ngpus(self): 
        return self._ngpus

    @ngpus.setter
    def ngpus(self, number_of_gpus): 
        self._ngpus = number_of_gpus
        
    # override attributes with cmd line arguments
    @property 
    def args(self): 
        return self._args 

    @args.setter 
    def args(self, args): 
        self._args = args 

        for opt in args:   
            if args[opt]: 
                setattr(self, opt, args[opt]) 

    # print object attributeis for debug purpose 
    def debug(self): 
        pprint(vars(self))
    
    # check for minimum software/hardware requirements 
    def check_prerequisite(self, module, min_ver):  
        # insert hostname after ssh 
        cmd     = prerequisite.cmd[module].replace('ssh', f'{ssh_cmd} {self.nodelist[0]}')
        regex   = prerequisite.regex[module]
        version = re.search(regex, syscmd(cmd)).group(1)
                
        if packaging.version.parse(version) < packaging.version.parse(min_ver):
            logging.error(f'{module} >= {min_ver} is required by {self.name}')
            sys.exit() 

    # download src 
    def download(self): 
        for url in self.src: 
            file_name = url.split('/')[-1]
            file_path = '/'.join([self.builddir, file_name])

            if not os.path.exists(file_path): 
                syscmd(f'wget {url} -O {file_path}')

    # build 
    def build(self):
        for cmd in self.buildcmd: 
            syscmd(cmd)

    def mkoutdir(self):  
        os.makedirs(self.outdir, exist_ok=True) 
        os.chdir(self.outdir)

    def run(self, redirect=0):
        logging.info(f'{"Output":7} : {os.path.relpath(self.output, self.rootdir)}')
       
        # redirect output to file 
        if redirect: 
            syscmd(self.runcmd, self.output) 
        else: 
            syscmd(self.runcmd)

        self.parse()
    
    def parse(self):  
        pass

    def info(self): 
        cpu_info(self.host)

        if self.ngpus: 
            gpu_info(self.device)

        module_list()

    def summary(self, sort=0, order='>'): 
        sys_info = self.host['Model'] 

        if self.ngpus: 
            sys_info += ' / ' + self.device['0'][0]

        print(f'\n>> {self.name}: {sys_info}')
        
        # unpact hash key 
        for key in self.result: 
            row = key.split(',')

            for perf in self.result[key]: 
                row.append(self._cell_format(self.result[key][perf])) 

            self.table.append(row)

        # sort data 
        #  if sort:  
            #  if order == '>': 
                #  self.result =  sorted(self.result, key=lambda x : float(x[-1]), reverse=True)
            #  else:
                #  self.result =  sorted(self.result, key=lambda x : float(x[-1]))

        print(tabulate(self.table, self.header, tablefmt='grid', stralign='center', numalign='center'))

    def _cell_format(self, cell):  
        average   = mean(cell)
        formatted = '' 

        if self.count > 1: 
            formatted = "\n".join(list(map("{:.2f}".format, cell))+[f'<{average:.2f}>'])
        else:
            formatted = f'{cell[0]:.2f}'

        return formatted
