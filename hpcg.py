#!/usr/bin/env python

import os
import argparse

from datetime import datetime

__version__ = '0.1'

parser = argparse.ArgumentParser(
    prog='hpcg.py',
    description='HPCG Benchmark', 
    usage='%(prog)s -g 256 256 256 -t 60',
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for problem setup
hpcg = parser.add_argument_group(
    title='HPCG parameters',
    description='\n'.join([
        '-g, --grid                 3-dimensional grid', 
        '-t, --time                 targeted run time',
        '    --device               list of GPU devices',
        '    --device_per_socket    number of device per socket', 
        '    --thread               number of omp threads']))

            
# cmd options with default values
hpcg.add_argument('-g', '--grid'             , type=int, nargs='*', default=[256,256,256], metavar='', help=argparse.SUPPRESS)
hpcg.add_argument('-t', '--time'             , type=int           , default=60           , metavar='', help=argparse.SUPPRESS)
hpcg.add_argument(      '--device'           , type=int, nargs='*', default=[0]          , metavar='', help=argparse.SUPPRESS)
hpcg.add_argument(      '--device_per_socket', type=int, nargs='*', default=[1,1]        , metavar='', help=argparse.SUPPRESS)
hpcg.add_argument(      '--thread'           , type=int           , default=8            , metavar='', help=argparse.SUPPRESS)

args = parser.parse_args()

# output directory
if not os.path.exists('output'):
    os.mkdir('output')

os.chdir('output')

# create time-stamp
current = datetime.now().strftime("%Y%m%d_%H:%M:%S")
os.mkdir(current)
os.chdir(current)

with open('HPCG.dat', 'w') as input:
    # output 
    input.write(f'HPCG input\n')
    input.write(f'KISTI\n')
    input.write(f'{" ".join(str(grid) for grid in args.grid)}\n')
    input.write(f'{args.time}')

with open('run.sh', 'w') as script:
    ngpus    = len(args.device); 

    # export cuda devices 
    script.write(f'export CUDA_VISIBLE_DEVICES={",".join(str(gpu) for gpu in args.device)}\n')

    # environment bug in hpcg image: 
    script.write(f'export SINGULARITYENV_LD_LIBRARY_PATH=/usr/local/cuda-11.1/targets/x86_64-linux/lib:$LD_LIBRARY_PATH\n\n')

    cmd = ['mpirun']

    # mpi options
    cmd.append(f'{"":>4}--np {ngpus}')

    # singularity options
    cmd.append(f'{"":>4}singularity')
    cmd.append(f'{"":>8}run')
    cmd.append(f'{"":>8}--nv')
    cmd.append(f'{"":>8}-B $PWD:/input')
    cmd.append(f'{"":>8}../../hpc-benchmarks_20.10-hpcg.sif')
    
    # hpl options
    cmd.append(f'{"":>8}hpcg.sh')
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
    cmd.append(f'{"":>12}--gpu-affinity {":".join(str(gpu) for gpu in args.device)}')

    # input file
    cmd.append(f'{"":>12}--dat /input/HPCG.dat')

    # max line length
    length = len(max(cmd, key = len)) 

    # join string and print to file
    cmd = '\\\n'.join(f'{line:<{length}} ' for line in cmd)

    script.write(f'{cmd}')
