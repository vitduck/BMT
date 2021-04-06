#!/usr/bin/env python 

import os
import re
import sys
import json
import subprocess

from datetime  import datetime
from packaging import version

# disable stact trace
sys.tracebacklimit = 0

class Bmt:
    prequisite = {
        'gcc'         : { 'cmd' : 'gcc --version'        , 'regex' : '\(GCC\)\s*([\d.]+)'  },
        'cuda'        : { 'cmd' : 'nvcc --version'       , 'regex' : 'release\s*([\d.]+)'  },
        'singularity' : { 'cmd' : 'singularity --version', 'regex' : 'version\s*([\d.]+)'  },
        'nvidia'      : { 'cmd' : 'nvidia-smi'           , 'regex' : 'Version:\s*([\d.]+)' },
        'openmpi'     : { 'cmd' : 'mpirun --version'     , 'regex' : 'mpirun.+?([\d.]+)'   },
        'mellanox'    : { 'cmd' : 'lspci'                , 'regex' : 'ConnectX\-(\d)'      }
    }

    def __init__(self, name, exe, output, module, min_ver, url, args):
        self.name    = name
        self.module  = module
        self.exe     = exe
        self.output  = output
        self.args    = args
        self.min_ver = min_ver
        self.url     = url
        
        # mpi job 
        self.mpiprocs = 0
        if hasattr(args, 'host'):
            for host in self.args.host:
                try:
                    self.mpiprocs += int(host.split(':')[1])
                except: 
                    self.mpiprocs += 1

        # directory/file
        self.root       = os.getcwd()
        self.bin_dir    = os.path.join(self.root, 'bin')
        self.build_dir  = os.path.join(self.root, 'build')
        self.output_dir = os.path.join(self.root, 'output', datetime.now().strftime("%Y%m%d_%H:%M:%S")) 

        self.bin        = os.path.join(self.root, self.bin_dir, self.exe)
        self.output     = os.path.join(self.root, self.output_dir, self.output)

        self.run_cmd    = [f'{self.bin}']

    # module list 
    def list(self):
        print(os.environ['LOADEDMODULES'].split(os.pathsep))

    # module purge 
    def purge(self):
        print('=> purging module')

        cmd = subprocess.run(['modulecmd', 'python', 'purge'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        exec(cmd)
    
    # module load 
    def load(self):
        env    = {} 
        module = []

        # read modules from json file
        if self.module:
            self.purge() 

            with open(self.module) as config:
                env = json.load(config)

            module = env[self.name]

            print(f'=> loading module: {", ".join(module)}')
            cmd = subprocess.run(['modulecmd', 'python', 'load'] + module, stdout=subprocess.PIPE).stdout.decode('utf-8')
            exec(cmd)
    
    # enforce minimal versions of module defined by class attributes of a child class
    def check_version(self):
        for module in self.min_ver: 
            module_info = ''

            try: 
                module_info = subprocess.run(self.prequisite[module]['cmd'].split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
            except FileNotFoundError:
                print(f'{module} >= {self.min_ver[module]} is required by {self.name}\n')
                sys.exit(1)
            else:
                module_ver  = re.search(self.prequisite[module]['regex'], module_info).group(1)

                if version.parse(module_ver) < version.parse(self.min_ver[module]):
                    print(f'{module} >= {self.min_ver[module]} is required by {self.name}\n')
                    sys.exit(1) 

    # wrapper for mkdir 
    def mkdir(self, directory): 
        if not os.path.exists(directory):
            print(f'=> mkdir {os.path.relpath(directory, self.root)}')

            os.makedirs(directory)
    
    # wrapper for cd
    def chdir(self, directory): 
        print(f'=> cd {os.path.relpath(directory, self.root)}')

        os.chdir(directory)

    # wrapper for sytem commands
    def sys_cmd(self, cmd, msg='', log='', mode='w'):
        if msg: 
            print(msg)

        if log: 
            with open(log, mode) as log_fh: 
                subprocess.run(cmd, stderr=log_fh, stdout=log_fh)
        else: 
            subprocess.run(cmd)

    # download src 
    def download(self):
        url_list = []

        # check if src files locate in ./build
        for url in self.url:
            file_name = os.path.basename(url)
            file_path = os.path.join(self.build_dir, file_name)
            
            if not os.path.exists(file_path):
                url_list.append(url)

        # re download src files
        if url_list: 
            self.mkdir(self.build_dir)

            log_file = os.path.join(self.root, 'wget.log')

            if os.path.exists(log_file): 
                os.remove(log_file) 

            for url in url_list:
                self.sys_cmd(['wget', url, '-P', self.build_dir], f'=> downloading {url}', log_file, 'a')

    # set omp_* environmental variables
    def set_omp(self, places='threads', num_threads=8, proc_bind='spread'):
        os.environ['OMP_PLACES'     ] = str(places)
        os.environ['OMP_NUM_THREADS'] = str(num_threads)
        os.environ['OMP_PROC_BIND'  ] = str(proc_bind)
    
    # run benchmark
    def run(self): 
        self.sys_cmd(self.run_cmd, f'=> {os.path.relpath(self.output, self.root)}', self.output) 

