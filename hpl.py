#!/usr/bin/env python

import argparse

__version__ = '0.1'

parser = argparse.ArgumentParser(
    prog='hpl.py',
    description='HPL input generator', 
    usage='%(prog)s -s 40000 60000 -b 512 1024 -p 1 2 -q 4 2',
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for problem setup
prob = parser.add_argument_group(
    title='Matrix setup',
    description='\n'.join([
        '-s, --size       List of problem size    (80% of total memory)', 
        '-b, --blocksize  List of block size      (multiply of 64)' ]))

# options for MPI communication 
comm = parser.add_argument_group(
    title='MPI setup (PxQ)',
    description='\n'.join([
        '-p, --pgrid  List of P grid              (default: 1)', 
        '-q, --qgrid  List of Q grid              (default: 1)',
        '--pmap       MPI processes mapping       (default: 0, i.e row-major)',
        '--broadcast  MPI broadcasting algorithms (default: 0, i.e ring-topology)']))

# options for algorithmic features
algo = parser.add_argument_group(
    title='Algorithmic features (default is sufficient)',
    description='\n'.join([
        '--pfact  List of PFACT variants ', 
        '--rfact  List of RFACT variants', 
        '--nbmin  List of NBMIN',
        '--ndiv   List of NDIV']))

# cmd options with default values
prob.add_argument('-s', '--size'     , type=int, nargs='*', required=True  , metavar='', help=argparse.SUPPRESS)
prob.add_argument('-b', '--blocksize', type=int, nargs='*', required=True  , metavar='', help=argparse.SUPPRESS)
comm.add_argument('-p', '--pgrid'    , type=int, nargs='*', default=[1]    , metavar='', help=argparse.SUPPRESS)
comm.add_argument('-q', '--qgrid'    , type=int, nargs='*', default=[1]    , metavar='', help=argparse.SUPPRESS)
comm.add_argument(      '--pmap'     , type=int,            default=0      , metavar='', help=argparse.SUPPRESS)
comm.add_argument(      '--bcast'    , type=int, nargs='*', default=[0]    , metavar='', help=argparse.SUPPRESS)
algo.add_argument(      '--pfact'    , type=int, nargs='*', default=[2]    , metavar='', help=argparse.SUPPRESS)
algo.add_argument(      '--rfact'    , type=int, nargs='*', default=[2]    , metavar='', help=argparse.SUPPRESS)
algo.add_argument(      '--nbmin'    , type=int, nargs='*', default=[1]    , metavar='', help=argparse.SUPPRESS)
algo.add_argument(      '--ndiv'     , type=int, nargs='*', default=[2]    , metavar='', help=argparse.SUPPRESS)

args = parser.parse_args()

with open('HPL.dat', 'w') as input:
    # output 
    input.write(f'HPL input\n')
    input.write(f'KISTI\n')
    input.write(f'{"HPL.out":<20} output file name\n')
    input.write(f'{"file":<20} device out (6=stdout,7=stderr,file)\n')

    # problem size
    input.write(f'{len(args.size):<20} number of problem size (N)\n')
    input.write(f'{" ".join(str(s) for s in args.size):<20} Ns\n')

    # block size 
    input.write(f'{len(args.blocksize):<20} number of Nbs\n')
    input.write(f'{" ".join(str(s) for s in args.blocksize):<20} NBs\n')

    # mpi grid
    input.write(f'{args.pmap:<20} PMAP process mapping (0=Row-,1=Column-major)\n')
    input.write(f'{len(args.qgrid):<20} number of process grids (P x Q)\n')
    input.write(f'{" ".join(str(s) for s in args.pgrid):<20} Ps\n')
    input.write(f'{" ".join(str(s) for s in args.qgrid):<20} Qs\n')
    
    # threshold (default)
    input.write(f'{"16.0":<20} threshold\n')

    # PFACT
    input.write(f'{len(args.pfact):<20} number of panel fact\n')
    input.write(f'{" ".join(str(s) for s in args.pfact):<20} PFACTs (0=left, 1=Crout, 2=Right) \n')

    # NBMIN
    input.write(f'{len(args.nbmin):<20} of recursive stopping criterium\n')
    input.write(f'{" ".join(str(s) for s in args.nbmin):<20} NBMINs (>=1)\n')

    # NDIV
    input.write(f'{len(args.ndiv):<20} number of recursive stopping criterium\n')
    input.write(f'{" ".join(str(s) for s in args.ndiv):<20} NDIVs\n')

    # RFACT
    input.write(f'{len(args.rfact):<20} number of recursive panel fact\n')
    input.write(f'{" ".join(str(s) for s in args.rfact):<20} RFACTs (0=left, 1=Crout, 2=Right) \n')

    # BCAST
    input.write(f'{len(args.bcast):<20} number of broadcast\n')
    input.write(f'{" ".join(str(s) for s in args.bcast):<20} BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)\n')

    # look-ahead (ignored by HPL-NVIDIA)
    input.write(f'{"1":<20} number of lookahead depth\n')
    input.write(f'{"1":<20} DEPTHs (>=0)\n')

    # swapping ( igned by HPL-NVIDIA)
    input.write(f'{"2":<20} SWAP (0=bin-exch,1=long,2=mix)\n')
    input.write(f'{"60":<20} swapping threshold \n')

    # LU (L1 = 1, U = 0 for HPL-NVIDIA)
    input.write(f'{"1":<20} L1 in (0=transposed,1=no-transposed) form\n')
    input.write(f'{"0":<20} U  in (0=transposed,1=no-transposed) form\n')

    # equilibration
    input.write(f'{"1":<20} qquilibration (0=no,1=yes)\n')

    # memory alignment 
    input.write(f'{"8":<20} memory alignment in double (> 0)\n')
