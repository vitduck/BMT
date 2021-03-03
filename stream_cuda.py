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
    usage='%(prog)s -a sm_70', 
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for stream setup
stream = parser.add_argument_group(
    title='STREAM parameters',
    description='\n'.join([
        '-a, --arch   (required)  targeting architecture',
        '-m, --mem                memory mode',
        '-n, --ntimes             run each kernel n times', 
        '-d, --device             device index',
        '-s, --size               size of matrix (must be multiplier of 1024)', 
        '-f, --float              use floats', 
        '-t, --triad              only run triad kernel', 
        '-c, --csv                output as csv table']))
       
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
