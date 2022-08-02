#!/usr/bin/env bash 

# HPC
singularity pull ngc_hpl_5.0.sif          docker://nvcr.io/nvidia/hpc-benchmarks:21.4-hpl
singularity pull ngc_hpcg_3.1.sif         docker://nvcr.io/nvidia/hpc-benchmarks:21.4-hpcg

# MD
singularity pull ngc_gromacs_2022.1.sif   docker://nvcr.io/hpc/gromacs:2022.1
singularity pull ngc_lammps_4May2022.sif  docker://nvcr.io/hpc/lammps:patch_4May2022

# DFT
singularity pull ngc_cp2k_9.1.sif         docker://nvcr.io/hpc/cp2k:v9.1.0


# ML
singularity pull ngc_tf_22.07.sif         docker://nvcr.io/nvidia/tensorflow:22.07-tf1-py3
singularity pull ngc_pytorch_22.07.sif    docker://nvcr.io/nvidia/pytorch:22.07-py3
