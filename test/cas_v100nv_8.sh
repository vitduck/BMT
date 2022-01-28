#!/usr/bin/env bash

#SBATCH --partition=cas_v100nv_8
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --gres=gpu:4
#SBATCH --job-name=test
#SBATCH --comment=python
#SBATCH --error=%j.stderr
#SBATCH --output=%j.stdout
#SBATCH --time=08:00:00

module purge 
module load python/3.9.5

export PYTHONPATH=/scratch/optpar01/KSTBench/src:$PYTHONPATH

./test_all.py          \
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
