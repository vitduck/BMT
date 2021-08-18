#!/usr/bin/env python3

import os 
import re
import sys
import pprint
import inspect
import logging
import packaging.version
import datetime
import collections
import prerequisite

from tabulate import tabulate
from utils    import init_nodelist, syscmd

class Bmt: 
    version  = '0.5'
    
    # initialize root logger 
    logging.basicConfig( 
        stream  = sys.stderr,
        level   = os.environ.get('LOGLEVEL', 'INFO').upper(), 
        format  = '%(message)s')

    def __init__(self, name):
        self.name     = name
        self._prefix  = './'
        self._args    = {} 
        
        self.nodes    = 0
        self.ntasks   = 0
        self.host     = init_nodelist() 
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
                setattr(self, opt, 
                        args[opt]) 

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
        if os.path.exists(self.bin): 
            logging.info('Skipping build phase')
            return

        logging.info(f'Building {self.name}')
        os.makedirs(self.builddir, exist_ok=True) 
        os.makedirs(self.bindir  , exist_ok=True) 

        for cmd in self.buildcmd: 
            syscmd(cmd)

    def mkoutdir(self):  
        os.makedirs(self.outdir, exist_ok=True) 
        os.chdir(self.outdir)

    def run(self, redirect=0):
        # redirect output to file 
        if redirect: 
            syscmd(self.runcmd, self.output) 
        else: 
            syscmd(self.runcmd)

        logging.info(f'Testing {self.name} > {os.path.relpath(self.output, self.rootdir)}')

        self.parse()
    
    def parse(self):  
        pass

    def summary(self): 
        print()
        print(tabulate(self.result, self.header, tablefmt='psql', floatfmt=".2f", numalign='decimal', stralign='right'))
