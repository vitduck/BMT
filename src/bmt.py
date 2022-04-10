#!/usr/bin/env python3

import os 
import re
import sys
import time
import inspect
import logging
import argparse
import datetime
import prerequisite
import packaging.version

from tabulate    import tabulate
from statistics  import mean
from pprint      import pprint

from cpu         import lscpu, cpu_info
from gpu         import gpu_info
from env         import module_list
from utils       import syscmd, autovivification
from slurm       import slurm_nodelist

class Bmt: 
    version = '0.9'
    
    # initialize the root logger 
    logging.basicConfig( 
        stream  = sys.stderr,
        level   = os.environ.get('LOGLEVEL', 'INFO').upper(), 
        format  = '[%(levelname)-5s] %(message)s')

    def __init__(self, count=1, prefix='./', outdir=None):
        # BMT type  
        self.name     = ''

        # Parse SLUM_NODELIST 
        self.nodelist = slurm_nodelist()

        # CPU and GPU
        self.host     = lscpu()
        self.device   = {} 

        # Number of repeted runs 
        self.count    = count

        # Build directory setup
        self.prefix   = os.path.abspath(prefix)
        self.bin      = ''
        self.rootdir  = os.path.dirname(inspect.stack()[-1][1])
        self.bindir   = os.path.join(self.prefix, 'bin')
        self.builddir = os.path.join(self.prefix, 'build')

        # Output directory 
        if outdir:
            self.outdir = '/'.join([os.path.abspath(outdir), datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")])
        else: 
            self.outdir = os.path.join(self.prefix, 'output', datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S"))

        # Required files 
        self.input    = ''
        self.output   = ''
        self.hostfile = 'hostfile'

        # Build instructions 
        self.src       = []
        self.buildcmd  = []

        # Run command 
        self.runcmd    = ''

        # Result summation   
        self.header    = []
        self.table     = [] 
        self.result    = autovivification() 

        # Command line arguments 
        self._args      = {} 

        self.parser     = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False )

        self.option = self.parser.add_argument_group(
            title       = 'Optional arguments',
            description = (
                '-h, --help           show this help message and exit\n'
                '-v, --version        show program\'s version number and exit\n' )) 

        # Create directories
        os.makedirs(self.builddir, exist_ok=True) 
        os.makedirs(self.bindir,   exist_ok=True) 
        os.makedirs(self.outdir,   exist_ok=True) 

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
        cmd     = prerequisite.cmd[module]
        regex   = prerequisite.regex[module]
        version = re.search(regex, syscmd(cmd)).group(1)
                
        if packaging.version.parse(version) < packaging.version.parse(min_ver):
            logging.error(f'{module} >= {min_ver} is required by {self.name}')
            sys.exit() 

    # download src 
    def download(self): 
        for url in self.src: 
            file_name = url.split('/')[-1]
            file_path = os.path.join(self.builddir, file_name)

            if not os.path.exists(file_path): 
                syscmd(f'wget --no-check-certificate {url} -O {file_path}')

    # build 
    def build(self):
        for cmd in self.buildcmd: 
            syscmd(cmd)
    
    def run(self, redirect=0):
        #logging.info(f'{"Output":7} : {os.path.relpath(self.output, self.rootdir)}')
        logging.info(f'{"Output":7} : {os.path.join(self.outdir, self.output)}')
       
        # redirect output to file 
        if redirect: 
            syscmd(self.runcmd, self.output)

            self.parse()
        else: 
            syscmd(self.runcmd) 

        time.sleep(5)
    
    def parse(self):  
        pass

    def info(self): 
        cpu_info(self.host)

        if self.device:
            gpu_info(self.device)

        module_list()

    def summary(self): 
        sys_info = self.host['Model'] 

        if self.device:
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

        print(tabulate(self.table, self.header, tablefmt='pretty', stralign='center', numalign='center'))

    def getopt(self): 
        self.option.add_argument('-h', '--help',     action='help', help=argparse.SUPPRESS )
        self.option.add_argument('-v', '--version' , action='version', version='%(prog)s ' + self.version, help=argparse.SUPPRESS )

        self.args = vars(self.parser.parse_args())

    def _cell_format(self, cell):  
        # crash test
        for item in cell: 
            if item == '-': 
                return '-' 

        average   = mean(cell)
        formatted = '' 

        if self.count > 1: 
            formatted = "\n".join(list(map("{:.2f}".format, cell)) + [f'-<{average:.2f}>-'])
        else:
            formatted = f'{cell[0]:.2f}'

        return formatted
