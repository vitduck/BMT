#!/usr/bin/env bash

#SBATCH --partition=cas_v100_2
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --gres=gpu:2
#SBATCH --job-name=test
#SBATCH --comment=python
#SBATCH --error=cas_v100_2.time
#SBATCH --output=cas_v100_2.out
#SBATCH --time=08:00:00

module purge 
module load python/3.9.5

export PATH=/apps/Modules/3.2.10/bin/modulecmd:$PATH
export PYTHONPATH=$(readlink --canonicalize ../src):$PYTHONPATH

time -p ./test_all.py  \
    'stream/omp/'      \
    'stream/omp/intel' \
    'stream/cuda'      \
    'iozne'            \
    'ior'              \
    'qe/ngc'           \
    'gromacs/ngc'      \
    'hpl'              \
    'hpl-ai'           \
    'hpcg'             
