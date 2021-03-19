#!/usr/bin/env python 

import os
import sys
import argparse

from shutil  import move
from version import __version__
from bmt     import benchmark

def main():
    iozone = benchmark(
        name    = 'iozone',
        exe     = 'iozone.x',
        output  = 'iozone.out',
        module  = [],
        min_ver = {}, 
        url     = ['http://www.iozone.org/src/current/iozone3_491.tgz'], 
        args    = getopt()
    )
    
    # download src files
    iozone.download()

    # build
    if not os.path.exists(iozone.bin):
        iozone.mkdir(iozone.bin_dir)
        iozone.chdir(iozone.build_dir)
        
        # extract
        iozone.sys_cmd(
            ['tar', 'xf', 'iozone3_491.tgz'], 
            f'=> extracting iozone3_491.tgz'
        )

        iozone.chdir('iozone3_491/src/current')
        
        # make
        iozone.sys_cmd(
            ['make', 'linux'], 
            f'=> building iozone', 
            f'{iozone.root}/build.log'
        )
    
        # move to bin
        move('iozone', f'{iozone.bin}')

    # automatic mode
    if iozone.args.a: 
        iozone.run_cmd += [ 
            '-a',
            '-n', iozone.args.n, 
            '-g', iozone.args.g, 
            '-y', iozone.args.y, 
            '-b', iozone.args.b, 
        ]
    # manual
    elif iozone.args.i: 
        for mode in iozone.args.i: 
            iozone.run_cmd += [ '-i', str(mode)] 

        iozone.run_cmd += [
            '-s', iozone.args.s, 
            '-r', iozone.args.r, 
        ]
   
    #  excel file
    iozone.run_cmd += [ '-b', os.path.join(iozone.output_dir, iozone.args.b) ]

    # benchmark 
    iozone.mkdir(iozone.output_dir)
    iozone.run()
    
def getopt(): 
    parser=argparse.ArgumentParser(
        prog            = 'iozone.py', 
        usage           = '%(prog)s -a -n 16k -g 64m -y 4k -q 16m ', 
        description     = 'IOZONE Benchmark', 
        formatter_class = argparse.RawDescriptionHelpFormatter)

    # version string
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    # check for exclusivity betwen '-a' and '-i'
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', action='store_true'             , help=argparse.SUPPRESS)
    group.add_argument('-i', type=int, nargs='+', metavar='*', help=argparse.SUPPRESS) 
    
    g1 = parser.add_argument_group(
        title='benchamrk arguments',
        description='\n'.join([
            '-a    full automatic mode', 
            '-i    test mode:',
            '         0 = write/re-write',
            '         1 = read/re-read',
            '         2 = random-read/write',
            '         3 = read-backwards',
            '         4 = re-write-records',
            '         5 = stride-read',
            '         6 = fwrite/re-fwrite',
            '         7 = fread/re-fread',
            '         8 = random-mix',
            '         9 = pwrite/re-pwrite',
            '        10 = pread/re-pread',
            '        11 = pwritev/re-pwritev',
            '        12 = preadv/re-preadv',
            '-n    minimum file size in auto mode   (default: 64k)',
            '-g    maximum file size in auto mode   (default: 512m)',
            '-y    minimum record size in auto mode (default: 4k)', 
            '-q    maximum record size in auto mode (default: 16m)',
            '-s    size of file to test             (default: 4k)',
            '-r    record size to test              (default: 512k)',
            '-b    excel output file                (default: io.xls)', 
        ])
    )

    g1.add_argument('-n', type=str, default='64k'   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-g', type=str, default='512m'  , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-y', type=str, default='4k'    , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-q', type=str, default='16m'   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-b', type=str, default='io.xls', metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-s', type=str, default='512k'  , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-r', type=str, default='4k'    , metavar='', help=argparse.SUPPRESS)

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()

if __name__ == "__main__":
    main()
