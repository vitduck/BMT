#!/usr/bin/env python

import os.path 
import argparse
import subprocess

from shutil    import move
from modulecmd import env
from utils     import download, timestamp, gcc_ver

__version__ = '0.2'

# init
parser=argparse.ArgumentParser(
    prog            = 'stream_cpu.py', 
    usage           = '%(prog)s -m skylake-avx512 -t 24 -a spread', 
    description     = 'STREAM-CPU Benchmark', 
    formatter_class = argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for stream setup
stream = parser.add_argument_group(
    title='STREAM parameters',
    description='\n'.join([
        '-s, --size        size of matrix', 
        '-n, --ntimes      run each kernel n times',
        '-m, --march       argeting architecture', 
        '-t, --thread      number of OMP threads',
        '-a, --affinity    thread affinity: close|spread']))

stream.add_argument('-s', '--size'    , type=int, default=40000000, metavar='',                             help=argparse.SUPPRESS)
stream.add_argument('-n', '--ntimes'  , type=int, default=100     , metavar='',                             help=argparse.SUPPRESS)
stream.add_argument('-m', '--march'   , type=str, required=True   , metavar='',                             help=argparse.SUPPRESS)
stream.add_argument('-t', '--thread'  , type=int, required=True   , metavar='',                             help=argparse.SUPPRESS)
stream.add_argument('-a', '--affinity', type=str, required=True   , metavar='', choices=['close','spread'], help=argparse.SUPPRESS)

args = parser.parse_args()

def main(): 
    # load modules
    env('stream_cpu')

    gcc_ver('7')
    
    if not os.path.exists('bin/stream_cpu.x'):
        os.makedirs('bin'  , exist_ok=True)
        os.makedirs('build', exist_ok=True)

        download(['https://www.cs.virginia.edu/stream/FTP/Code/stream.c'])

        build() 
   
    benchmark()

def build():
    print('=> Building STREAM_CPU')

    with open('gcc.log', 'w') as log:
        # -O3: libc's memcpy for copy kernel
        # -ffreestanding: force temporal asm instread of memcpy
        subprocess.run([
            'gcc',
                '-O3', 
                '-fopenmp', 
                '-ffreestanding', 
                '-march='              + args.march   ,
                '-DSTREAM_ARRAY_SIZE=' + str(args.size), 
                '-DNTIMES='            + str(args.ntimes), 
                'build/stream.c', 
                '-o', 'bin/stream_cpu.x'])

def benchmark(): 
    # time stamp
    outdir = timestamp()
    output = os.path.join(outdir, 'stream_cpu.out')

    os.makedirs(outdir)
    
    print(f'=> Output: {output}')
    
    # set omp environment variables
    os.environ['OMP_PLACES'     ] = 'threads' # hw thread, no HT
    os.environ['OMP_NUM_THREADS'] = str(args.thread)
    os.environ['OMP_PROC_BIND'  ] = str(args.affinity)

    cmd = ['bin/stream_cpu.x']

    with open(output, 'w') as output:
        subprocess.call(cmd, stdout=output)

if __name__ == "__main__":
    main()
