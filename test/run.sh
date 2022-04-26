#!/usr/bin/env bash

#SBATCH --partition=maintenance
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --gres=gpu:2
#SBATCH --job-name=test
#SBATCH --comment=python
#SBATCH --error=%j.stderr
#SBATCH --output=%j.stdout
#SBATCH --time=8:00:00

module purge 
module load python/3.9.5

export PATH=/apps/Modules/3.2.10/bin:$PATH
export PYTHONPATH=$(readlink --canonicalize ../src):$PYTHONPATH

time ./test_all.py     \
    'stream/omp'       \
    'stream/omp/intel' \
    'stream/cuda'      \
    'iozone'           \
    'ior'              \
    'qe/ngc'           \
    'gromacs/ngc'      \
    'hpl'              \
    'hpl-ai'           \
    'hpcg'             
