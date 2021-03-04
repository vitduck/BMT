#!/usr/bin/env python

import os
import argparse

from datetime import datetime

__version__ = '0.1'

parser = argparse.ArgumentParser(
    prog='hpl.py',
    description='HPL Benchmark', 
    usage='%(prog)s -s 40000 60000 -b 512 1024 -p 1 2 -q 4 2',
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for problem setup
hpl = parser.add_argument_group(
    title='HPL parameters',
    description='\n'.join([
        '-s, --size                 list of problem size', 
        '-b, --blocksize            list of block size',
        '-p, --pgrid                list of P grid', 
        '-q, --qgrid                list of Q grid',
        '    --device               list of GPU devices', 
        '    --device_per_socket    number of device per socket', 
        '    --thread               number of omp threads',  
        '    --pmap                 MPI processes mapping',
        '    --broadcast            MPI broadcasting algorithms',
        '    --pfact                list of PFACT variants ', 
        '    --rfact                list of RFACT variants', 
        '    --nbmin                list of NBMIN',
        '    --ndiv                 list of NDIV',
        '    --ai                   use hpl-ai']))
    
# cmd options with default values
hpl.add_argument('-s', '--size'             , type=int, nargs='*', required=True, metavar='', help=argparse.SUPPRESS)
hpl.add_argument('-b', '--blocksize'        , type=int, nargs='*', required=True, metavar='', help=argparse.SUPPRESS)
hpl.add_argument('-p', '--pgrid'            , type=int, nargs='*', default=[1]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument('-q', '--qgrid'            , type=int, nargs='*', default=[1]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--device'           , type=int, nargs='*', default=[0]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--device_per_socket', type=int, nargs='*', default=[1,1], metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--thread'           , type=int,            default=8    , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--pmap'             , type=int,            default=0    , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--bcast'            , type=int, nargs='*', default=[0]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--pfact'            , type=int, nargs='*', default=[2]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--rfact'            , type=int, nargs='*', default=[2]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--nbmin'            , type=int, nargs='*', default=[1]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--ndiv'             , type=int, nargs='*', default=[2]  , metavar='', help=argparse.SUPPRESS)
hpl.add_argument(      '--ai'               , action='store_true', default=False,             help=argparse.SUPPRESS)

args = parser.parse_args()

# output directory
if not os.path.exists('output'):
    os.mkdir('output')

os.chdir('output')

# create time-stamp
current = datetime.now().strftime("%Y%m%d_%H:%M:%S")
os.mkdir(current)
os.chdir(current)

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

with open('run.sh', 'w') as script:
    mpiprocs = args.pgrid[0] * args.qgrid[0]; 
    ngpus    = len(args.device); 

    # check for correct number of mpiprocs and gpus 
    if mpiprocs != ngpus:
        raise Exception("Error: HPL requires CPU/GPU = 1")

    # export cuda devices 
    script.write(f'export CUDA_VISIBLE_DEVICES={",".join(str(gpu) for gpu in args.device)}\n\n')

    cmd    = ['mpirun']

    # mpi options
    cmd.append(f'{"":>4}--np {mpiprocs}')

    # singularity options
    cmd.append(f'{"":>4}singularity')
    cmd.append(f'{"":>8}run')
    cmd.append(f'{"":>8}--nv')
    cmd.append(f'{"":>8}-B $PWD:/input')
    cmd.append(f'{"":>8}../../hpc-benchmarks_20.10-hpl.sif')
    
    # hpl options
    cmd.append(f'{"":>8}hpl.sh')
    cmd.append(f'{"":>12}--cpu-cores-per-rank {args.thread}')
    
    # cpu affinity
    socket       = [0,1]
    cpu_affinity = []
    for affinity_set in zip(args.device, args.device_per_socket, socket):
        # for cas_v100_2: two GPUs in socket #1
        if affinity_set[1] == 0: 
            continue 

        cpu_affinity = cpu_affinity + ([affinity_set[0]]*affinity_set[1])

    cmd.append(f'{"":>12}--cpu-affinity {":".join(str(cpu) for cpu in cpu_affinity)}')
    
    # gpu affinity 
    cmd.append(f'{"":>12}--gpu-affinity {":".join(str(gpu) for gpu in args.device)}' )

    # input file
    cmd.append(f'{"":>12}--dat /input/HPL.dat')

    # switch to hpl-ai
    if args.ai:
        cmd.append(f'{"":>12}--xhpl-ai')

    # max line length
    length = len(max(cmd, key = len)) 

    # join string and print to file
    cmd = '\\\n'.join(f'{line:<{length}} ' for line in cmd)

    script.write(f'{cmd}')
