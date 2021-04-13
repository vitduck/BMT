#!/usr/bin/env python 

import os 
import argparse

from version import __version__
from nvidia  import Hpcg

def main():
    hpcg = Hpcg(
        name    = 'hpcg-nvidia', 
        exe     = 'run.sh', 
        output  = 'HPCG.out', 
        module  = None,
        min_ver = { 
            'singularity': '3.4.1',  
            'openmpi'    : '4', 
            'nvidia'     : '450.36',  
            'mellanox'   : '4'
        }, 
        url     = [], 
        args    = getopt()
    )

    hpcg.check_version()

    os.makedirs(hpcg.output_dir, exist_ok=True)
    os.chdir(hpcg.output_dir)

    if hpcg.args.auto: 
        hpcg.parameter_scan()
        hpcg.summary() 
    else:
        hpcg.run()

def getopt():
    parser = argparse.ArgumentParser(
        usage           = '%(prog)s -g 256 256 256 -t 60 --host test01 --thread 8 --sif hpc-benchmarks_20.10-hpcg.sif',
        description     = 'hpcg benchmark',
        formatter_class = argparse.RawDescriptionHelpFormatter, 
        add_help        = False
    )

    
    # options for problem setup
    opt = parser.add_argument_group(
        title       = 'optional arugments',
        description = '\n'.join([
            '-h, --help                     show this help message and exit',
            '-v, --version                  show program\'s version number and exit',
            '-a, --auto                     automatic parameter scan mode', 
            '-g, --grid                     3-dimensional grid',
            '-t, --time                     targeted run time',
            '    --host                     list of hosts on which to invoke processes',
            '    --device                   list of GPU devices',
            '    --device_per_socket        number of device per socket',
            '    --thread                   number of omp threads',
            '    --sif                      path of singularity images',
        ])
    )
    
    # version string
    opt.add_argument('-h', '--help'              , action='help'     ,                                    help=argparse.SUPPRESS)
    opt.add_argument('-v', '--version'          , action='version'   , version='%(prog)s ' + __version__, help=argparse.SUPPRESS)
    opt.add_argument('-a', '--auto'             , action='store_true', default=False                    , help=argparse.SUPPRESS)
    opt.add_argument('-g', '--grid'             , type=int, nargs='*', default=[256,256,256], metavar='', help=argparse.SUPPRESS)
    opt.add_argument('-t', '--time'             , type=int           , default=60           , metavar='', help=argparse.SUPPRESS)
    opt.add_argument(      '--host'             , type=str, nargs='+', required=True        , metavar='', help=argparse.SUPPRESS)
    opt.add_argument(      '--device'           , type=int, nargs='*', default=[0]          , metavar='', help=argparse.SUPPRESS)
    opt.add_argument(      '--device_per_socket', type=int, nargs='*', default=[1,0]       , metavar='' , help=argparse.SUPPRESS)
    opt.add_argument(      '--thread'           , type=int,            required=True        , metavar='', help=argparse.SUPPRESS)
    opt.add_argument(      '--sif'              , type=str,            required=True        , metavar='', help=argparse.SUPPRESS)

    return parser.parse_args()

if __name__ == '__main__': 
    main()
