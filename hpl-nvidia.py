#!/usr/bin/env python 

import os 
import argparse

from version import __version__
from nvidia  import Hpl

def main():
    hpl = Hpl(
        name    = 'hpl-nvidia', 
        exe     = 'run.sh', 
        output  = 'HPL.log', 
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

    hpl.check_version()

    hpl.mkdir(hpl.output_dir)
    hpl.chdir(hpl.output_dir)

    # automatic mode 
    if hpl.args.auto: 
        hpl.parameter_scan()
        hpl.summary()
    else:
        hpl.run() 

def getopt():
    parser = argparse.ArgumentParser(
        usage           = '%(prog)s -s 40000 -b 256 --host test01 --thread 8 --sif hpc-benchmarks_20.10-hpl.sif', 
        description     = 'hpl benchmark',
        formatter_class = argparse.RawDescriptionHelpFormatter
    )

    # version string
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    # options for problem setup
    g1 = parser.add_argument_group(
        title       = 'hpl arugments',
        description = '\n'.join([
            '-a, --auto                 automatic parameter scan mode',
            '-m, --mem                  device memory',
            '-s, --size                 list of problem size',
            '-b, --blocksize            list of block size',
            '-p, --pgrid                list of P grid',
            '-q, --qgrid                list of Q grid',
            '    --pmap                 MPI processes mapping',
            '    --pfact                list of PFACT variants ',
            '    --nbmin                list of NBMIN',
            '    --ndiv                 list of NDIV',
            '    --rfact                list of RFACT variants',
            '    --broadcast            MPI broadcasting algorithms',
        ])
    )
    g2 = parser.add_argument_group(
        title       = 'ngc arguments',
        description = '\n'.join([
            '    --host                 list of hosts on which to invoke processes',
            '    --device               list of GPU devices',
            '    --device_per_socket    number of device per socket',
            '    --thread               number of omp threads',
            '    --ai                   use hpl-ai bin',
            '    --sif                  path of singularity images',
        ])
    )

    ex = parser.add_mutually_exclusive_group()

    ex.add_argument('-a', '--auto'             , action='store_true', default=False             , help=argparse.SUPPRESS)
    ex.add_argument('-s', '--size'             , type=int, nargs='*', default=40000 , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-m', '--mem'              , type=str           , default='32GB', metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-b', '--blocksize'        , type=int, nargs='*', default=256   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-p', '--pgrid'            , type=int, nargs='*', default=[1]   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-q', '--qgrid'            , type=int, nargs='*', default=[1]   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--pmap'             , type=int,            default=0     , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--pfact'            , type=int, nargs='*', default=[1]   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--nbmin'            , type=int, nargs='*', default=[4]   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--ndiv'             , type=int, nargs='*', default=[2]   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--rfact'            , type=int, nargs='*', default=[2]   , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--bcast'            , type=int, nargs='*', default=[0]   , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--host'             , type=str, nargs='+', required=True , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--device'           , type=int, nargs='*', default=[0]   , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--device_per_socket', type=int, nargs='*', default=[1,0] , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--thread'           , type=int,            required=True , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--ai'               , action='store_true', default=False ,             help=argparse.SUPPRESS)
    g2.add_argument(      '--sif'              , type=str,            required=True , metavar='', help=argparse.SUPPRESS)

    return parser.parse_args()

if __name__ == '__main__': 
    main()
