#!/usr/bin/env python 

import os
import argparse

from shutil  import move
from version import __version__
from bmt     import Bmt

class Ior(Bmt): 
    def __init__(self, name, exe, output, module, min_ver, url, args): 
        super().__init__(name, exe, output, module, min_ver, url, args)

        self.run_cmd = [     
            'mpirun', 
                '--hostfile', self.hostfile,
                self.bin, 
                    '-b', args.b,  
                    '-t', args.t,  
                    '-s', str(args.s),  
                    '-F', 
                    '-C'
        ]

    def run(self): 
        self.write_hostfile() 

        super().run()

def main():
    ior = Ior(
        name    = 'ior',
        exe     = 'ior.x',
        output  = 'ior.out',
        module  = None,
        min_ver = { 'openmpi' : '3' },
        url     = ['https://github.com/hpc/ior/releases/download/3.3.0/ior-3.3.0.tar.gz'], 
        args    = getopt()
    )
    
    ior.check_version()
    
    # download url
    ior.download()
    
    if not os.path.exists(ior.bin): 
        # extracting 
        os.chdir(ior.build_dir)

        ior.sys_cmd(
            cmd=['tar', 'xf', 'ior-3.3.0.tar.gz'], 
            msg='=> extracting ior-3.3.0.tar.gz'
        )
        
        # configure
        os.chdir('ior-3.3.0')

        ior.sys_cmd(
            cmd=[  
                './configure', 
                    'MPICC=mpicc', 
                    f'CPPFLAGS=-I{os.environ["MPI_ROOT"]}/include', 
                    f'LDFLAGS=-L{os.environ["MPI_ROOT"]}/lib'
                ],
            msg='=> configuring ior', 
            log=f'{ior.root}/configure.log'
        )
    
        # make 
        ior.sys_cmd(
            cmd=['make', '-j', '4'], 
            msg='=> building ior', 
            log=f'{ior.root}/build.log'
        )
        
        # move to bin
        os.makedirs(ior.bin_dir, exist_ok=True)

        move('src/ior', f'{ior.bin}')

    # run benchmark
    os.makedirs(ior.output_dir, exist_ok=True)

    ior.run()

def getopt():
    parser=argparse.ArgumentParser(
        prog            = 'ior.py', 
        usage           = '%(prog)s -b 16m -t 1m -s 16 --host test1:2 test2:2',
        description     = 'ior benchmark', 
        formatter_class = argparse.RawDescriptionHelpFormatter, 
        add_help        = False
    )

    # version string

    opt = parser.add_argument_group(
        title='optional arguments',
        description='\n'.join([
            '-h, --help           show this help message and exit',
            '-v, --version        show program\'s version number and exit',
            '-b, --block          block size',
            '-t, --transfer       transfer size',
            '-s, --segment        segment count',
            '    --host           list of hosts on which to invoke processes'
        ])
    )

    # options for stream setup
    opt.add_argument('-h', '--help'   , action='help'                                      , help=argparse.SUPPRESS)
    opt.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__, help=argparse.SUPPRESS)
    opt.add_argument('-b'             , type=str,            required=True, metavar=''     , help=argparse.SUPPRESS)
    opt.add_argument('-t'             , type=str,            required=True, metavar=''     , help=argparse.SUPPRESS)
    opt.add_argument('-s'             , type=int,            required=True, metavar=''     , help=argparse.SUPPRESS)
    opt.add_argument('--host'         , type=str, nargs='+', required=True, metavar=''     , help=argparse.SUPPRESS)

    return parser.parse_args()

if __name__ == "__main__":
    main()
