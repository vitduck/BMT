#!/usr/bin/env python 

import os
import sys
import argparse

from shutil  import move
from version import __version__
from bmt     import Bmt

class Iozone(Bmt): 
    def __init__(self, name, exe, output, module, min_ver, url, args): 
        super().__init__(name, exe, output, module, min_ver, url, args)

        # automatic mode
        if args.a: 
            self.run_cmd += [ 
                '-a',
                '-n', args.n, 
                '-g', args.g, 
                '-y', args.y, 
                '-b', args.b, 
            ]
        # manual mode -i
        elif args.i: 
            for mode in args.i: 
                self.run_cmd += ['-i', str(mode)] 

            self.run_cmd += [
                '-s', args.s, 
                '-r', args.r, 
            ]

        #  excel file
        self.run_cmd += [
            '-b', os.path.join(self.output_dir, args.b)
        ]

def main():
    iozone = Iozone(
        name    = 'iozone',
        exe     = 'iozone.x',
        output  = 'iozone.out',
        module  = None,
        min_ver = {}, 
        url     = ['http://www.iozone.org/src/current/iozone3_491.tgz'], 
        args    = getopt()
    )
    
    # download url
    iozone.download()

    # build
    if not os.path.exists(iozone.bin):
        # extract
        os.chdir(iozone.build_dir)
        iozone.sys_cmd(
            cmd=['tar', 'xf', 'iozone3_491.tgz'], 
            msg=f'=> extracting iozone3_491.tgz'
        )

        # make
        os.chdir('iozone3_491/src/current')
        iozone.sys_cmd(
            cmd=['make', 'linux'], 
            msg=f'=> building iozone', 
            log=f'{iozone.root}/build.log'
        )
    
        # move to bin
        os.makedirs(iozone.bin_dir, exist_ok=True)
        move('iozone', f'{iozone.bin}')

    # run benchmark 
    os.makedirs(iozone.output_dir, exist_ok=True)

    iozone.run()
    
def getopt(): 
    parser=argparse.ArgumentParser(
        prog            = 'iozone.py', 
        usage           = '%(prog)s -a -n 16k -g 64m -y 4k -q 16m ', 
        description     = 'iozone benchmark', 
        formatter_class = argparse.RawDescriptionHelpFormatter,  
        add_help        = False
    )

    opt = parser.add_argument_group(
        title='optional arguments',
        description='\n'.join([
            '-h, --help          show this help message and exit',
            '-v, --version       show program\'s version number and exit',
            '-a                  full automatic mode', 
            '-i                  test mode:',
            '                       0 = write/re-write',
            '                       1 = read/re-read',
            '                       2 = random-read/write',
            '                       3 = read-backwards',
            '                       4 = re-write-records',
            '                       5 = stride-read',
            '                       6 = fwrite/re-fwrite',
            '                       7 = fread/re-fread',
            '                       8 = random-mix',
            '                       9 = pwrite/re-pwrite',
            '                      10 = pread/re-pread',
            '                      11 = pwritev/re-pwritev',
            '                      12 = preadv/re-preadv',
            '-n                  minimum file size in auto mode   (default: 64k)',
            '-g                  maximum file size in auto mode   (default: 512m)',
            '-y                  minimum record size in auto mode (default: 4k)', 
            '-q                  maximum record size in auto mode (default: 16m)',
            '-s                  size of file to test             (default: 4k)',
            '-r                  record size to test              (default: 512k)',
            '-b                  excel output file                (default: io.xls)', 
        ])
    )
    
    opt.add_argument('-h', '--help'    , action='help',                                       help=argparse.SUPPRESS)
    opt.add_argument('-v', '--version' , action='version', version='%(prog)s ' + __version__, help=argparse.SUPPRESS)
    opt.add_argument('-a'              , action='store_true'                                , help=argparse.SUPPRESS)
    opt.add_argument('-i'              , type=int, nargs='+'       , metavar='*'            , help=argparse.SUPPRESS) 
    opt.add_argument('-n'              , type=str, default='64k'   , metavar=''             , help=argparse.SUPPRESS)
    opt.add_argument('-g'              , type=str, default='512m'  , metavar=''             , help=argparse.SUPPRESS)
    opt.add_argument('-y'              , type=str, default='4k'    , metavar=''             , help=argparse.SUPPRESS)
    opt.add_argument('-q'              , type=str, default='16m'   , metavar=''             , help=argparse.SUPPRESS)
    opt.add_argument('-b'              , type=str, default='io.xls', metavar=''             , help=argparse.SUPPRESS)
    opt.add_argument('-s'              , type=str, default='512k'  , metavar=''             , help=argparse.SUPPRESS)
    opt.add_argument('-r'              , type=str, default='4k'    , metavar=''             , help=argparse.SUPPRESS)

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()

if __name__ == "__main__":
    main()
