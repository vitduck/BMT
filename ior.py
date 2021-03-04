#!/usr/bin/env python 

import os
import argparse
import subprocess 

from shutil import copy

__version__ = '0.1'

# init
parser=argparse.ArgumentParser(
    prog='ior.py', 
    description='IOR Benchmark', 
    usage='%(prog)s -a', 
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for stream setup
ior = parser.add_argument_group(
    title='IOR Parameters',
    description='\n'.join([
        '-n       number of process', 
        '-b       block size', 
        '-t       transfer size', 
        '-s       segment count', 
        '-F       ecah MPI process writes its own file',
        '-C       cyclic distribution of write-read to mitigate cache effect']))

ior.add_argument('-n', type=int, required=True, metavar='', help=argparse.SUPPRESS)
ior.add_argument('-b', type=str, required=True, metavar='', help=argparse.SUPPRESS)
ior.add_argument('-t', type=str, required=True, metavar='', help=argparse.SUPPRESS)
ior.add_argument('-s', type=int, required=True, metavar='', help=argparse.SUPPRESS)
ior.add_argument('-F', action='store_true'                , help=argparse.SUPPRESS)
ior.add_argument('-C', action='store_true'                , help=argparse.SUPPRESS)

args = parser.parse_args()

def main():
    download()
    build()
    benchmark()

def download():
    subprocess.call(['wget', 'https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz'])
 
def build():
    subprocess.call(['tar', 'xf', 'ior-3.3.0.tar.gz'])

    os.chdir('ior-3.3.0')

    subprocess.call([ './configure', 
                        'MPICC=mpicc', 
                        f'CPPFLAGS=-I{os.environ["MPI_ROOT"]}/include', 
                        f'LDFLAGS=-L{os.environ["MPI_ROOT"]}/lib'])
    
    subprocess.call(['make', '-j', '4'])
    
    os.chdir('../')

    copy('ior-3.3.0/src/ior','.')

def benchmark(): 
    cmd = ['mpirun', '-n', str(args.n), './ior', '-b', str(args.b), '-t', str(args.t), '-s', str(args.s)]

    if args.F: 
        cmd += ['-F']
    if args.C: 
        cmd += ['-C']

    subprocess.call(cmd)

if __name__ == "__main__":
    main()
