#!/usr/bin/env python 

import os
import argparse

from shutil  import move
from version import __version__
from bmt     import benchmark

def main():
    ior = benchmark(
        name    = 'ior',
        exe     = 'ior.x',
        output  = 'ior.out',
        module  = ['gcc/8.3.0', 'mpi/openmpi-3.1.5'], 
        min_ver = {}, 
        url     = ['https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz'], 
        args    = getopt()
    )
    
    # env
    ior.purge()
    ior.load()
    ior.check_version()
    
    # download src files 
    ior.download()
    
    # build
    if not os.path.exists(ior.bin): 
        ior.mkdir(ior.bin_dir)
        ior.chdir(ior.build_dir)
        
        # extracting 
        ior.sys_cmd(
            ['tar', 'xf', 'ior-3.3.0.tar.gz'], 
            '=> extracting ior-3.3.0.tar.gz'
        )

        ior.chdir('ior-3.3.0')

        # configure
        ior.sys_cmd(
            [  './configure', 
               'MPICC=mpicc', 
              f'CPPFLAGS=-I{os.environ["MPI_ROOT"]}/include', 
              f'LDFLAGS=-L{os.environ["MPI_ROOT"]}/lib'
            ],
            '=> configuring ior', 
            f'{ior.root}/configure.log'
        )
    
        # make 
        ior.sys_cmd(
            ['make', '-j', '4'], 
            '=> building ior', 
            f'{ior.root}/build.log'
        )
        
        # move to bin
        move('src/ior', f'{ior.bin}')

    # benchmark
    ior.run_cmd = [     
            'mpirun', 
            '-n', str(ior.mpiprocs), 
            '-H', ','.join(ior.args.host) 
        ] +\
        ior.run_cmd + [
            '-b',     ior.args.b,  
            '-t',     ior.args.t,  
            '-s', str(ior.args.s),  
            '-F', 
            '-C'
        ]

    ior.mkdir(ior.output_dir)
    ior.run()

def getopt():
    parser=argparse.ArgumentParser(
        prog            = 'ior.py', 
        usage           = '%(prog)s -b 16m -t 1m -s 16 --host test1:2 test2:2',
        description     = 'IOR Benchmark', 
        formatter_class = argparse.RawDescriptionHelpFormatter
    )

    # version string
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    g1 = parser.add_argument_group(
        title='runtime arguments',
        description='\n'.join([
            '-b, --block     block size',
            '-t, --transfer  transfer size',
            '-s, --segment   segment count',
            '    --host      list of hosts on which to invoke processes'
        ])
    )

    # options for stream setup
    g1.add_argument('-b',     type=str,            required=True, metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-t',     type=str,            required=True, metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-s',     type=int,            required=True, metavar='', help=argparse.SUPPRESS)
    g1.add_argument('--host', type=str, nargs='+', required=True, metavar='', help=argparse.SUPPRESS)

    return parser.parse_args()

if __name__ == "__main__":
    main()
