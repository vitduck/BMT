#!/usr/bin/env python3

import os
import re
import logging
import argparse

from bmt import Bmt

class BabelStream(Bmt):
    def __init__ (self, size=eval('2**25'), ntimes=100, **kwargs):
        super().__init__(**kwargs)

        self.size   = size 
        self.ntimes = ntimes 

        self.model  = ''
        self.stream = ''
        self.src    = []

        self.cc     = '' 
        self.cflags = ''
        
    def build(self): 
        self.buildcmd = [[
          [f'{self.cc}',
                '-I.', 
               f'-D{self.model}',
               f'{self.cflags}',
               f'-o {self.bin}', 
               f'{self.builddir}/main.cpp',
               f'{self.builddir}/{self.stream}' ]]]
        
        super().build()

    def runcmd(self): 
        cmd = [
            self.bin, 
               f'-s {str(self.size)}', 
               f'-n {str(self.ntimes)}' ]

        return [cmd]

    def parse(self):

        key = self.param() 

        with open(self.output, 'r') as output_fh:
            for line in output_fh:
                for kernel in ['Copy', 'Mul', 'Add', 'Triad', 'Dot']: 
                    if re.search(f'{kernel}:?', line):
                        if not self.result[key][kernel]: 
                            self.result[key][kernel] = []

                        self.result[key][kernel].append(float(line.split()[1])/1000)

    def param(self): 
        pass

    def add_argument(self):
        super().add_argument()

        self.parser.add_argument('--size'   , type=int, help='size of matrix (default: 2^35)')
        self.parser.add_argument('--ntimes' , type=int, help='run each kernel n times (default: 100)')
