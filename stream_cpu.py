#!/usr/bin/env python

import os
import os.path 

import argparse
import subprocess

# fix the format of the help text
parser=argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=40))

# parse cmd options
parser.add_argument("-m", "--march" ,   default="skylake-avx512", type=str, help="targeting architecture")
parser.add_argument("-s", "--size"  ,   default=40000000        , type=int, help="size of matrix")
parser.add_argument("-n", "--ntimes",   default=100             , type=int, help="run each kernel n times")
parser.add_argument("-t", "--threads",  default=1               , type=int, help="number of OMP threads")
parser.add_argument("-a", "--affinity", default="spread"        , type=str, help="thread affinity")

args = parser.parse_args()

# download stream.c
def download(): 
    if not os.path.exists('stream.c'): 
        subprocess.call(['wget', 'https://www.cs.virginia.edu/stream/FTP/Code/stream.c'])

# build with gcc 
# -ffreestanding: generates temporal asm instruction instead of libc's memcpy
def build(): 
    subprocess.call([ 'gcc',
                      '-O3', 
                      '-fopenmp', 
                      '-ffreestanding', 
                      '='.join(['-march', args.march]), 
                      '='.join(['-DSTREAM_ARRAY_SIZE', str(args.size)]), 
                      '='.join(['-DNTIMES', str(args.ntimes)]), 
                      'stream.c', 
                      '-o', 'stream_cpu.x'])

def benchmark(): 
    os.environ['OMP_DISPLAY_ENV'] = 'true'
    os.environ['OMP_PLACES']      = 'threads' # hw thread, no HT
    os.environ['OMP_NUM_THREADS'] = str(args.threads)
    os.environ['OMP_PROC_BIND']   = str(args.affinity)

    subprocess.call(['./stream_cpu.x'])

download()
build()
benchmark()
