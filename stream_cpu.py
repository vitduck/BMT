#!/usr/bin/env python

import os.path 
import argparse
import subprocess

# increase the width of help text
parser=argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=40))

# parse cmd options
parser.add_argument('-m', '--march' ,   type=str, default='skylake-avx512', help='targeting architecture')
parser.add_argument('-s', '--size'  ,   type=int, default=40000000        , help='size of matrix')
parser.add_argument('-n', '--ntimes',   type=int, default=100             , help='run each kernel n times')
parser.add_argument('-t', '--threads',  type=int, default=1               , help='number of OMP threads')
parser.add_argument('-a', '--affinity', type=str, default='spread'        , help='thread affinity')

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
    subprocess.call([
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
