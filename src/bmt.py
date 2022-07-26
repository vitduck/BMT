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

from tabulate import tabulate
from statistics import mean
from pprint import pprint

from cpu import lscpu, cpu_info
from gpu import gpu_info
from env import module_list
from slurm import slurm_nodelist
from utils import syscmd, autovivification

class Bmt:
    version = '1.0'

    # initialize the root logger
    logging.basicConfig(
        stream = sys.stderr,
        level  = os.environ.get('LOGLEVEL', 'INFO').upper(),
        format = '%(message)s')
        #format = '[%(levelname)-5s] %(message)s')

    def __init__(self, repeat=1, prefix='./', outdir=None):
        self.name     = ''

        # parse $SLUM_NODELIST
        self.nodelist = slurm_nodelist()

        # host/device info
        self.host     = lscpu()
        self.device   = {}

        # number of repeted measurements
        self.repeat   = repeat

        # Build directory setup
        self.bin       = []
        self.prefix    = os.path.abspath(prefix)
        self.rootdir   = os.path.dirname(inspect.stack()[-1][1])
        self.bindir    = os.path.join(self.prefix, 'bin')
        self.builddir  = os.path.join(self.prefix, 'build')

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
        self.src      = []
        self.buildcmd = []

        # Result summation
        self.header   = []
        self.table    = []
        self.result   = autovivification()

        # Command line arguments
        self.parser   = argparse.ArgumentParser(
            formatter_class = lambda prog: argparse.HelpFormatter(prog, max_help_position=40, width=100))

        # Create directories
        os.makedirs(self.builddir, exist_ok=True)
        os.makedirs(self.bindir,   exist_ok=True)
        os.makedirs(self.outdir,   exist_ok=True)

    # print object attributeis for debug purpose
    def debug(self):
        pprint(vars(self))

    # check for minimum software/hardware requirements
    def check_prerequisite(self, module, min_ver):
        cmd     = prerequisite.cmd[module]
        regex   = prerequisite.regex[module]
        version = re.search(regex, syscmd([cmd])).group(1)

        if packaging.version.parse(version) < packaging.version.parse(min_ver):
            logging.error(f'{module} >= {min_ver} is required by {self.name}')
            sys.exit()

    # download src
    def download(self):
        for url in self.src:
            file_name = url.split('/')[-1]
            file_path = os.path.join(self.builddir, file_name)

            if not os.path.exists(file_path):
                syscmd([
                   [f'wget', 
                       f'--no-check-certificate {url}', 
                       f'-O {file_path}']])
    # build
    def build(self):
        for cmd in self.buildcmd:
            syscmd(cmd)

    def run(self, redirect=0):
        for i in range(1, self.repeat+1): 
            if self.repeat > 1: 
                self.output = re.sub('log(\.\d+)?', f'log.{i}', self.output)
        
            logging.info(f'{"Output":7} : {os.path.join(self.outdir, self.output)}')
                
            # redirect output to file
            if redirect:
                syscmd(self.runcmd(), self.output)
            else:
                syscmd(self.runcmd())

            self.parse()

            time.sleep(5)

    def runcmd(self): 
        pass

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
            ndevices  = len(self.device.keys())
            sys_info += ' / ' + f"{ndevices} x {self.device['0'][0]}"

        print(f'\n<> {self.name}: {sys_info}')

        # unpact hash key
        for key in self.result:
            row = key.split(',')

            for perf in self.result[key]:
                row.append(self.__cell_format(self.result[key][perf]))

            self.table.append(row)

        # sort data
        #  if sort:
            #  if order == '>':
                #  self.result =  sorted(self.result, key=lambda x : float(x[-1]), reverse=True)
            #  else:
                #  self.result =  sorted(self.result, key=lambda x : float(x[-1]))

        print(tabulate(self.table, self.header, tablefmt='pretty', stralign='center', numalign='center'))

    def add_argument(self): 
        self.parser.add_argument('-v', '--version' , action='version', version='%(prog)s ' + self.version)
        self.parser.add_argument('--repeat' , type=int, help='number of repeated measurements')

    def getopt(self):
        self.add_argument()

        args = vars(self.parser.parse_args())

        for opt in args:
            if args[opt]:
                setattr(self, opt, args[opt]) 
    
    def __cell_format(self, cell):
        for item in cell:
            if item == '-':
                return '-'

        average = mean(cell)

        if self.repeat > 1:
            formatted = "\n".join(list(map("{:.2f}".format, cell)) + [f'-<{average:.2f}>-'])
        else:
            formatted = f'{cell[0]:.2f}'

        return formatted
