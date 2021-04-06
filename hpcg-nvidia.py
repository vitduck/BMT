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

    hpcg.mkdir(hpcg.output_dir)

    hpcg.write_input()
    hpcg.write_script() 

    hpcg.chdir(hpcg.output_dir)

    hpcg.run()

def getopt():
    parser = argparse.ArgumentParser(
        usage           = '%(prog)s -g 256 256 256 -t 60 --host test01 --thread 8 --sif hpc-benchmarks_20.10-hpcg.sif',
        description     = 'hpcg benchmark',
        formatter_class = argparse.RawDescriptionHelpFormatter
    )

    # version string
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    # options for problem setup
    g1 = parser.add_argument_group(
        title       = 'hpcg arugments',
        description = '\n'.join([
            '-g, --grid                 3-dimensional grid',
            '-t, --time                 targeted run time',
        ])
    )

    g2 = parser.add_argument_group(
        title       = 'ngc arguments',
        description = '\n'.join([
            '    --host                 list of hosts on which to invoke processes',
            '    --device               list of GPU devices',
            '    --device_per_socket    number of device per socket',
            '    --thread               number of omp threads',
            '    --sif                  path of singularity images',
        ])
    )

    # cmd options with default values
    g1.add_argument('-g', '--grid'             , type=int, nargs='*', default=[256,256,256], metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-t', '--time'             , type=int           , default=60           , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--host'             , type=str, nargs='+', required=True        , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--device'           , type=int, nargs='*', default=[0]          , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--device_per_socket', type=int, nargs='*', required=True        , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--thread'           , type=int,            required=True        , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--sif'              , type=str,            required=True        , metavar='', help=argparse.SUPPRESS)

    return parser.parse_args()

if __name__ == '__main__': 
    main()
