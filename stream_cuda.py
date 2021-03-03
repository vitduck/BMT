#!/usr/bin/env python

import os.path 

import argparse
import textwrap
import subprocess

__version__ = '0.1'

# init
parser=argparse.ArgumentParser(
    prog='stream_cuda.py', 
    description='STREAM-CUDA', 
    usage='%(prog)s -a sm_70')

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# parse cmd options
parser.add_argument('-a', '--arch'  , type=str, required=True      , metavar='', help='targeting architecture')
parser.add_argument('-m', '--mem'   , type=str, default='DEFAULT'  , metavar='', help='memory mode')
parser.add_argument('-n', '--ntimes', type=int, default=100        , metavar='', help='run each kernel n times')
parser.add_argument('-d', '--device', type=int, default=0          , metavar='', help='device index')
parser.add_argument('-s', '--size'  , type=int                     , metavar='', help='size of matrix (must be multiplier of 1024)')
parser.add_argument('-f', '--float' , action='store_true'                      , help='use floats') 
parser.add_argument('-t', '--triad' , action='store_true'                      , help='only run triad')
parser.add_argument('-c', '--csv'   , action='store_true'                      , help='Output as csv table')

args = parser.parse_args()

print(args)

def main(): 
    download()
    build()
    benchmark()

# download CUDStream src
def download(): 
    source = ['main.cpp', 'Stream.h','CUDAStream.cu', 'CUDAStream.h']

    for file in source: 
        if not os.path.exists(file):
            subprocess.call(['wget', 'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/' + file])

# build with nvcc
def build(): 
    subprocess.call([ 
        'nvcc',
            '-std=c++11', 
            '-O3',
            '-DCUDA',
            '-arch='+ args.arch,
            '-D'    + args.mem, 
            'main.cpp', 
            'CUDAStream.cu', 
            '-o', 'stream_cuda.x'
    ])

def benchmark(): 
    cmd = [
        './stream_cuda.x', 
            '--numtimes', str(args.ntimes), 
            '--device',   str(args.device)
    ] 

    if args.size: 
        cmd.append('--arraysize', str(args.size))

    if args.float:
        cmd.append('--float')
    
    if args.triad:
        cmd.append('--triad-only')

    if args.csv:
        cmd.append('--csv')

    subprocess.call(cmd)

if __name__ == '__main__':
    main()
