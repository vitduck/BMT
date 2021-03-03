#!/usr/bin/env python

import os.path 
import argparse
import subprocess

__version__ = '0.1'

# init
parser=argparse.ArgumentParser(
    prog='stream_cpu.py', 
    description='STREAM-CPU', 
    usage='%(prog)s -m skylake-avx512 -t 24 -a spread')

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# parse cmd options
parser.add_argument('-s', '--size'    , type=int, default=40000000, metavar='',                             help='size of matrix (must be at least 4xLLC)')
parser.add_argument('-n', '--ntimes'  , type=int, default=100     , metavar='',                             help='run each kernel n times')
parser.add_argument('-m', '--march'   , type=str, required=True   , metavar='',                             help='targeting architecture')
parser.add_argument('-t', '--threads' , type=int, required=True   , metavar='',                             help='number of OMP threads')
parser.add_argument('-a', '--affinity', type=str, required=True   , metavar='', choices=['close','spread'], help='thread affinity')

args = parser.parse_args()

def main(): 
    download()
    build()
    benchmark()

# download stream.c
def download(): 
    if not os.path.exists('stream.c'): 
        subprocess.call(['wget', 'https://www.cs.virginia.edu/stream/FTP/Code/stream.c'])

# build with gcc 
# -ffreestanding: generates temporal asm instruction instead of libc's memcpy
def build(): 
    subprocess.run([
        'gcc',
            '-O3', 
            '-fopenmp', 
            '-ffreestanding', 
            '-march='              + args.march   ,
            '-DSTREAM_ARRAY_SIZE=' + str(args.size), 
            '-DNTIMES='            + str(args.ntimes), 
            'stream.c', 
            '-o', 'stream_cpu.x'
    ])

def benchmark(): 
    os.environ['OMP_DISPLAY_ENV'] = 'true'
    os.environ['OMP_PLACES'     ] = 'threads' # hw thread, no HT
    os.environ['OMP_NUM_THREADS'] = str(args.threads)
    os.environ['OMP_PROC_BIND'  ] = str(args.affinity)

    cmd = ['./stream_cpu.x']

    subprocess.call(cmd)

if __name__ == "__main__":
    main()
