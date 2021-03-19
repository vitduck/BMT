#!/usr/bin/env python 

import os 
import argparse

from version import __version__
from nvidia  import hpl_nvidia

def main():
    hpl = hpl_nvidia(
        name    = 'hpl-nvidia', 
        exe     = 'run.sh', 
        output  = 'HPL.out', 
        module  = [ 
            'singularity/3.6.4', 
            'gcc/8.3.0', 
            'cuda/10.1', 
            'cudampi/openmpi-test'
        ], 
        min_ver = { 
            'singularity': '3.4.1',  
            'openmpi'    : '4', 
            'nvidia'     : '450.36',  
            'mellanox'   : '4'
        }, 
        url     = [], 
        args    = getopt()
    )

    hpl.purge()
    hpl.load()
    hpl.check_version()

    hpl.mkdir(hpl.output_dir)
    
    hpl.write_input()
    hpl.write_script() 
    
    hpl.chdir(hpl.output_dir)

    hpl.run() 

def getopt():
    parser = argparse.ArgumentParser(
        usage           = (
            '%(prog)s -s 40000 -b 256 --host test01 --sif hpc-benchmarks_20.10-hpl.sif'
        ),
        description     = 'hpl Benchmark',
        formatter_class = argparse.RawDescriptionHelpFormatter
    )

    # version string
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    # options for problem setup
    g1 = parser.add_argument_group(
        title       = 'HPL arugments',
        description = '\n'.join([
            '-s, --size                 list of problem size',
            '-b, --blocksize            list of block size',
            '-p, --pgrid                list of P grid',
            '-q, --qgrid                list of Q grid',
            '    --pmap                 MPI processes mapping',
            '    --broadcast            MPI broadcasting algorithms',
            '    --pfact                list of PFACT variants ',
            '    --rfact                list of RFACT variants',
            '    --nbmin                list of NBMIN',
            '    --ndiv                 list of NDIV',
        ])
    )
    g2 = parser.add_argument_group(
        title       = 'NVIDIA arguments',
        description = '\n'.join([
            '    --host                 list of hosts on which to invoke processes',
            '    --device               list of GPU devices',
            '    --device_per_socket    number of device per socket',
            '    --thread               number of omp threads',
            '    --ai                   use hpl-ai bin',
            '    --sif                  path of singularity images',
        ])
    )
    
    # cmd options with default values
    g1.add_argument('-s', '--size'             , type=int, nargs='*', required=True, metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-b', '--blocksize'        , type=int, nargs='*', required=True, metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-p', '--pgrid'            , type=int, nargs='*', default=[1],   metavar='', help=argparse.SUPPRESS)
    g1.add_argument('-q', '--qgrid'            , type=int, nargs='*', default=[1],   metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--pmap'             , type=int,            default=0    , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--bcast'            , type=int, nargs='*', default=[0]  , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--pfact'            , type=int, nargs='*', default=[2]  , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--rfact'            , type=int, nargs='*', default=[2]  , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--nbmin'            , type=int, nargs='*', default=[1]  , metavar='', help=argparse.SUPPRESS)
    g1.add_argument(      '--ndiv'             , type=int, nargs='*', default=[2]  , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--host'             , type=str, nargs='+', required=True, metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--device'           , type=int, nargs='*', default=[0]  , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--device_per_socket', type=int, nargs='*', default=[1,1], metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--thread'           , type=int,            default=8    , metavar='', help=argparse.SUPPRESS)
    g2.add_argument(      '--ai'               , action='store_true', default=False,             help=argparse.SUPPRESS)
    g2.add_argument(      '--sif'              , type=str,            required=True, metavar='', help=argparse.SUPPRESS)

    return parser.parse_args()

if __name__ == '__main__': 
    main()
