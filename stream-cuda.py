#!/usr/bin/env python 

import os 
import argparse

from version import __version__
from bmt     import benchmark

def main():
    stream = benchmark(
        name    = 'stream-cuda', 
        exe     = 'stream-cuda.x', 
        output  = 'stream-cuda.out', 
        module  = None, 
        min_ver = {'cuda' : '10.1'},
        url     = [ 
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/Stream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/main.cpp',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/CUDAStream.h',
            'https://raw.githubusercontent.com/UoB-HPC/BabelStream/main/CUDAStream.cu' 
        ], 
        args   = getopt() 
    )

    stream.load()
    stream.check_version()

    stream.download()
    
    # build
    stream.mkdir(stream.bin_dir)
    stream.sys_cmd(
        ['nvcc',
            '-std=c++11',
            '-O3',
            '-DCUDA',
            '-arch='+ stream.args.arch,
            '-D'    + stream.args.mem,
            '-o', 
            f'{stream.bin}',
            f'{stream.build_dir}/main.cpp',
            f'{stream.build_dir}/CUDAStream.cu'
        ], 
        '=> building STREAM-CUDA', 
        f'{stream.root}/build.log'
    )

    # run benchmark 
    stream.run_cmd += [
        '-s', str(stream.args.size), 
        '-n', str(stream.args.ntimes)
    ]

    stream.mkdir(stream.output_dir)
    stream.run()

def getopt(): 
    parser = argparse.ArgumentParser(
        usage           = '%(prog)s -a sm_70',
        description     = 'stream-cuda benchmark', 
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    
    # version string
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    g1 = parser.add_argument_group(
        title       = 'build arguments',
        description = '\n'.join([
            '-a, --arch     targeting architecture',
            '-m, --mem      memory mode',
        ])
    )

    g2 = parser.add_argument_group(
        title       = 'runtime arguments',
        description = '\n'.join([
            '-s, --size     size of matrix (default: 2^25)', 
            '-n, --ntimes   run each kernel n times', 
        ])
    )

    g1.add_argument('-a', '--arch'  , type=str, required=True        , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-m', '--mem'   , type=str, default='DEFAULT'    , metavar='', help=argparse.SUPPRESS)
    g2.add_argument('-s', '--size'  , type=int, default=eval('2**25'), metavar='', help=argparse.SUPPRESS)
    g2.add_argument('-n', '--ntimes', type=int, default=100          , metavar='', help=argparse.SUPPRESS)
        
    return parser.parse_args()

if __name__ == '__main__': 
    main()
