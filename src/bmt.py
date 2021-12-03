#!/usr/bin/env python3

import os 
import re
import sys
import inspect
import logging
import pprint
import packaging.version
import datetime
import prerequisite

from tabulate import tabulate
from utils    import syscmd
from slurm    import slurm_nodelist, slurm_ntasks

class Bmt: 
    version  = '0.5'
    
    # initialize root logger 
    logging.basicConfig( 
        stream  = sys.stderr,
        level   = os.environ.get('LOGLEVEL', 'INFO').upper(), 
        format  = '# %(message)s')

    def __init__(self, name):
        self.cpu      = '' 
        self.gpu      = ''
        self.name     = name

        self._prefix  = './'
        self._args    = {} 
        
        self.nodes    = 1 
        self.ntasks   = slurm_ntasks() 
        self.host     = slurm_nodelist()
        self.hostfile = 'hostfile'
        
        self.rootdir  = os.path.dirname(inspect.stack()[-1][1])
        self.bin      = ''
        self.input    = ''
        self.buildcmd = []
        self.runcmd   = ''
        self.output   = ''

        self.header   = []
        self.result   = []
    
    # set up sub-directories 
    @property 
    def prefix(self): 
        return self._prefix

    @prefix.setter 
    def prefix(self, prefix): 
        self._prefix  = os.path.abspath(prefix)
        self.bindir   = os.path.join(self._prefix, 'bin')
        self.builddir = os.path.join(self._prefix, 'build')
        self.outdir   = os.path.join(self._prefix, 'output', datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S"))
        self.bin      = os.path.join(self.bindir, self.bin)

    # override attributes from cmd line argument
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
        pprint.pprint(vars(self))
    
    # check for minimum software/hardware requirements 
    def check_prerequisite(self, module, min_ver):  
        # insert hostname after ssh 
        cmd     = prerequisite.cmd[module].replace('ssh', f'ssh {self.host[0]}')
        regex   = prerequisite.regex[module]
        version = re.search(regex, syscmd(cmd)).group(1)
                
        if packaging.version.parse(version) < packaging.version.parse(min_ver):
            logging.error(f'{module} >= {min_ver} is required by {self.name}')
            sys.exit() 

    # OpenMPI: write hostfile
    def write_hostfile(self): 
        with open(self.hostfile, 'w') as fh:
            for host in self.host[0:self.nodes]:
                fh.write(f'{host} slots={self.ntasks}\n')

    # returns if previously built binary exists 
    def build(self):
        os.makedirs(self.builddir, exist_ok=True) 
        os.makedirs(self.bindir  , exist_ok=True) 

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

    def summary(self, sort=0, order='>'): 
        if sort:  
            if order == '>': 
                self.result =  sorted(self.result, key=lambda x : float(x[-1]), reverse=True)
            else:
                self.result =  sorted(self.result, key=lambda x : float(x[-1]))

        if self.gpu: 
            print(f'\n[{"/".join([self.cpu, self.gpu])}]')
        else: 
            print(f'\n[{self.cpu}]')
        
        print(tabulate(self.result, self.header, tablefmt='fancy_grid', floatfmt='.2f', numalign='decimal', stralign='right'))
