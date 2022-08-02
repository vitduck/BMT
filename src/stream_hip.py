#!/usr/bin/env python3

import os
import re
import argparse

from gpu          import device_query, nvidia_smi, gpu_info
from babel_stream import BabelStream

class StreamHip(BabelStream):
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        
        self.name   = 'STREAM/HIP'
        self.bin    = os.path.join(self.bindir,'babelstream_hip')

        self.model  = 'HIP'
        self.stream = 'HIPStream.cpp'
        self.src    = [ 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/Stream.h', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/main.cpp', 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/hip/HIPStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/src/hip/HIPStream.cpp' ]
        
        self.cc     = 'hipcc'
        self.cflags = '-O3'

        self.header = ['size', 'ntimes', 'copy(GB/s)', 'mul(GB/s)', 'add(GB/s)', 'triad(GB/s)', 'dot(GB/s)']

        self.parser.description = 'STREAM_GPU benchmark'
    
    def run(self): 
        os.chdir(self.outdir)
    
        self.output = f'stream-hip.log'
        
        super().run(1) 

    def param(self): 
        return ",".join(map(str, [self.size, self.ntimes]))
