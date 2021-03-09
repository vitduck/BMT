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
    prog            = 'ior.py', 
    usage           = '%(prog)s -a', 
    description     = 'IOR Benchmark', 
    formatter_class = argparse.RawDescriptionHelpFormatter)

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

# top directory
root = os.getcwd()

def main():
    env('ior')

    if not os.path.exists('bin/ior'):
        os.makedirs('bin'  , exist_ok=True)
        os.makedirs('build', exist_ok=True)

        download(['https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz'])

        build() 

    benchmark()

def build():
    os.chdir('build')

    # extract 
    print('=> Extracting ior')
    subprocess.call(['tar', 'xf', 'ior-3.3.0.tar.gz'])

    os.chdir('ior-3.3.0')

    # configure
    with open('configure.log', 'w') as log:
        print('=> Configuring ior')
        subprocess.call([ 
            './configure', 
                'MPICC=mpicc', 
                f'CPPFLAGS=-I{os.environ["MPI_ROOT"]}/include', 
                f'LDFLAGS=-L{os.environ["MPI_ROOT"]}/lib'],
                stderr=log, stdout=log)
    
    # make
    with open('make.log', 'w') as log:
        print('=> Building ior')
        subprocess.call(['make', '-j', '4'], stderr=log, stdout=log)
    
    move('src/ior'      , f'{root}/bin')
    move('configure.log', f'{root}'    )
    move('make.log'     , f'{root}'    )

    os.chdir(root)

def benchmark(): 
    # time stamp
    outdir = timestamp()
    output = os.path.join(outdir, 'iozone.out')

    os.makedirs(outdir)

    print(f'=> Output: {output}')

    cmd = [
        'mpirun', 
            '--n', str(args.n), 
            'bin/ior', 
            '-b', str(args.b), 
            '-t', str(args.t), 
            '-s', str(args.s)]

    if args.F: 
        cmd.extend(['-F'])

    if args.C: 
        cmd.extend(['-C'])

    with open(output, 'w') as output:
        subprocess.call(cmd, stdout=output)

if __name__ == "__main__":
    main()
