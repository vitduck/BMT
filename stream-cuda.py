#!/usr/bin/env python 

import os 
import argparse

from version import __version__
from bmt     import Bmt

class StreamCuda(Bmt): 
    def __init__(self, name, exe, output, module, min_ver, url, args): 
        super().__init__(name, exe, output, module, min_ver, url, args)

        self.run_cmd += [
            '-s', str(args.size), 
            '-n', str(args.ntimes)
        ]

def main():
    stream = StreamCuda(
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
        args    = getopt() 
    )

    stream.check_version()

    # download url
    stream.download()
    
    # build
    os.makedirs(stream.bin_dir, exist_ok=True)

    stream.sys_cmd(
        cmd=[ 
            'nvcc',
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
        msg='=> building STREAM-CUDA', 
        log=f'{stream.root}/build.log'
    )
    
    # run benchmark 
    os.makedirs(stream.output_dir, exist_ok=True)

    stream.run()

def getopt(): 
    parser = argparse.ArgumentParser(
        usage           = '%(prog)s -a sm_70',
        description     = 'stream-cuda benchmark', 
        formatter_class = argparse.RawDescriptionHelpFormatter, 
        add_help        = False
    )
    
    opt = parser.add_argument_group(
        title       = 'optional arguments',
        description = '\n'.join([
            '-h, --help          show this help message and exit',
            '-v, --version       show program\'s version number and exit',
            '-a, --arch          targeting architecture',
            '-m, --mem           memory mode',
            '-s, --size          size of matrix', 
            '-n, --ntimes        run each kernel n times', 
        ])
    )

    opt.add_argument('-h', '--help'    , action='help',                                       help=argparse.SUPPRESS)
    opt.add_argument('-v', '--version' , action='version', version='%(prog)s ' + __version__, help=argparse.SUPPRESS)
    opt.add_argument('-a', '--arch'    , type=str, required=True        , metavar=''        , help=argparse.SUPPRESS)
    opt.add_argument('-m', '--mem'     , type=str, default='DEFAULT'    , metavar=''        , help=argparse.SUPPRESS)
    opt.add_argument('-s', '--size'    , type=int, default=eval('2**25'), metavar=''        , help=argparse.SUPPRESS)
    opt.add_argument('-n', '--ntimes'  , type=int, default=100          , metavar=''        , help=argparse.SUPPRESS)
        
    return parser.parse_args()

if __name__ == '__main__': 
    main()
