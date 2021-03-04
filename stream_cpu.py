#!/usr/bin/env python

import re
import os.path 
import argparse
import subprocess

__version__ = '0.1'

# init
parser=argparse.ArgumentParser(
    prog='stream_cpu.py', 
    description='STREAM-CPU Benchmark', 
    usage='%(prog)s -m skylake-avx512 -t 24 -a spread', 
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for stream setup
stream = parser.add_argument_group(
    title='STREAM parameters',
    description='\n'.join([
        '-s, --size        size of matrix (must be at least 4 x LLC)', 
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
    gcc_ver = subprocess.run(['gcc', '--version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    match   = re.match('gcc \(GCC\) (\d)\.\d\.\d', gcc_ver)

    # check minium gcc version
    if int(match.group(1)) < 7: 
        raise Exception("GCC >=7 is required to build CPU-STREAM\n")

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
    os.environ['OMP_NUM_THREADS'] = str(args.thread)
    os.environ['OMP_PROC_BIND'  ] = str(args.affinity)

    cmd = ['./stream_cpu.x']

    subprocess.call(cmd)

if __name__ == "__main__":
    main()
