#!/usr/bin/env python 

import os 
import argparse

from version import __version__
from bmt     import Bmt

def main():
    stream = Bmt(
        name    = 'stream-cpu', 
        exe     = 'stream-cpu.x', 
        output  = 'stream-cpu.out', 
        module  = None, 
        min_ver = { 'gcc': '7'}, 
        url     = ['https://www.cs.virginia.edu/stream/FTP/Code/stream.c'], 
        args    = getopt()
    )

    stream.check_version()
    
    # download url
    stream.download()
   
    # build stream-cpu
    stream.mkdir(stream.bin_dir)
    stream.sys_cmd(
        cmd=[ 
            'gcc',
                '-O3',
                '-fopenmp',
                '-ffreestanding',
                '-march='              + stream.args.march   ,
                '-DSTREAM_ARRAY_SIZE=' + str(stream.args.size),
                '-DNTIMES='            + str(stream.args.ntimes),
                '-o', 
                f'{stream.bin}', 
                f'{stream.build_dir}/stream.c' 
            ], 
        msg='=> building STREAM-CPU', 
        log=f'{stream.root}/build.log'
    )

    # set up thread affinity
    stream.set_omp('threads', stream.args.thread, stream.args.affinity) 
    
    # run benchmark
    stream.mkdir(stream.output_dir)
    stream.run()
    
def getopt(): 
    parser = argparse.ArgumentParser( 
        usage       = '%(prog)s -m skylake-avx512 -t 24 -a spread',
        description = 'stream-cpu benchmark',
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    
    # version string
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    g1 = parser.add_argument_group(
        title       ='build arguments',
        description ='\n'.join([
            '-m, --march    targeting architecture', 
            '-s, --size     size of matrix', 
            '-n, --ntimes   run each kernel n times',
        ])
    )
    
    g2 = parser.add_argument_group(
        title       ='runtime arguments',
        description ='\n'.join([
            '-t, --thread    number of OMP threads',
            '-a, --affinity  thread affinity: (close|spread)'
        ])
    )

    g1.add_argument('-s', '--size'    , type=int, default=40000000, metavar='',                             help=argparse.SUPPRESS)
    g1.add_argument('-n', '--ntimes'  , type=int, default=100     , metavar='',                             help=argparse.SUPPRESS)
    g1.add_argument('-m', '--march'   , type=str, required=True   , metavar='',                             help=argparse.SUPPRESS)
    g2.add_argument('-t', '--thread'  , type=int, required=True   , metavar='',                             help=argparse.SUPPRESS)
    g2.add_argument('-a', '--affinity', type=str, required=True   , metavar='', choices=['close','spread'], help=argparse.SUPPRESS)

    return parser.parse_args()

if __name__ == '__main__': 
    main()
