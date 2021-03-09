#!/usr/bin/env python

import os.path 
import argparse
import subprocess

from shutil    import move
from modulecmd import env
from utils     import download, timestamp

__version__ = '0.2'

# init
parser=argparse.ArgumentParser(
    prog            ='stream_cuda.py', 
    usage           = '%(prog)s -a sm_70', 
    description     = 'STREAM-CUDA Benchmark', 
    formatter_class = argparse.RawDescriptionHelpFormatter)

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

def main(): 
    # load modules
    env('stream_cuda')

    if not os.path.exists('bin/stream_gpu.x'):
        os.makedirs('bin'  , exist_ok=True)
        os.makedirs('build', exist_ok=True)

        download([
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/Stream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/main.cpp',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/CUDAStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/CUDAStream.cu'])

        build() 
    
    benchmark()

def build(): 
    print('=> Building STREAM_CUDA')

    with open('nvcc.log', 'w') as log:
        subprocess.call([ 
            'nvcc',
            '-std=c++11', 
            '-O3',
            '-DCUDA',
            '-arch='+ args.arch,
            '-D'    + args.mem, 
            'build/main.cpp', 
            'build/CUDAStream.cu', 
            '-o', 'bin/stream_cuda.x'])
    
def benchmark(): 
    # time stamp
    outdir = timestamp()
    output = os.path.join(outdir, 'stream_cuda.out')

    os.makedirs(outdir)

    print(f'=> Output: {output}')

    cmd = [
        'bin/stream_cuda.x', 
            '--numtimes', str(args.ntimes), 
            '--device',   str(args.device)]

    if args.size: 
        cmd.extend(['--arraysize', str(args.size)])

    if args.float:
        cmd.extend(['--float'])

    if args.triad:
        cmd.extend(['--triad-only'])

    if args.csv:
        cmd.extend(['--csv'])

    with open(output, 'w') as output:
        subprocess.call(cmd, stdout=output)

if __name__ == '__main__':
    main()
