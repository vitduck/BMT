#!/usr/bin/env python

import os.path 

import argparse
import textwrap
import subprocess

from datetime import datetime

__version__ = '0.1'

# init
parser=argparse.ArgumentParser(
    prog='stream_cuda.py', 
    description='STREAM-CUDA Benchmark', 
    usage='%(prog)s -a sm_70', 
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for stream setup
stream = parser.add_argument_group(
    title='STREAM parameters',
    description='\n'.join([
        '-a, --arch      targeting architecture',
        '-m, --mem       memory mode',
        '-n, --ntimes    run each kernel n times', 
        '-d, --device    device index',
        '-s, --size      size of matrix (must be multiplier of 1024)', 
        '-f, --float     use floats', 
        '-t, --triad     only run triad kernel', 
        '-c, --csv       output as csv table']))
       
# parse cmd options
stream.add_argument('-a', '--arch'  , type=str, required=True      , metavar='', help=argparse.SUPPRESS) 
stream.add_argument('-m', '--mem'   , type=str, default='DEFAULT'  , metavar='', help=argparse.SUPPRESS) 
stream.add_argument('-n', '--ntimes', type=int, default=100        , metavar='', help=argparse.SUPPRESS) 
stream.add_argument('-d', '--device', type=int, default=0          , metavar='', help=argparse.SUPPRESS) 
stream.add_argument('-s', '--size'  , type=int                     , metavar='', help=argparse.SUPPRESS) 
stream.add_argument('-f', '--float' , action='store_true'                      , help=argparse.SUPPRESS) 
stream.add_argument('-t', '--triad' , action='store_true'                      , help=argparse.SUPPRESS) 
stream.add_argument('-c', '--csv'   , action='store_true'                      , help=argparse.SUPPRESS) 

args = parser.parse_args()

root = os.getcwd()

def main(): 
    download()
    build()
    benchmark()

# download CUDStream src
def download(): 
    if not os.path.exists('build'):
        os.mkdir('build')

    os.chdir('build')

    source = ['main.cpp', 'Stream.h','CUDAStream.cu', 'CUDAStream.h']

    for file in source: 
        if not os.path.exists(file):
            subprocess.call(['wget', 'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/' + file])

    os.chdir(root)

# build with nvcc
def build(): 
    os.chdir('build')

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

    os.chdir(root)

def benchmark(): 
     # output directory
    if not os.path.exists('output'):
        os.mkdir('output')
    os.chdir('output')

    # create time-stamp
    current = datetime.now().strftime("%Y%m%d_%H:%M:%S")
    os.mkdir(current)
    os.chdir(current)

    cmd = [
        '../../build/stream_cuda.x', 
            '--numtimes', str(args.ntimes), 
            '--device',   str(args.device)
    ] 

    if args.size: 
        cmd += ['--arraysize', str(args.size)]
    if args.float:
        cmd += ['--float']
    if args.triad:
        cmd += ['--triad-only']
    if args.csv:
        cmd += ['--csv']

    with open('stream_cuda.out', 'w') as output:
        subprocess.call(cmd, stdout=output)

    os.chdir(root)

if __name__ == '__main__':
    main()
