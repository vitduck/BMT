#!/usr/bin/env bash 

# HPC
singularity pull amdih_rochpl_5.0.sif       docker://amdih/rochpl:5.0.5_49
singularity pull amdih_rochpcg_3.1.sif      docker://amdih/rochpcg:3.1.0_97

# MD
singularity pull amdih_gromacs_2021.1.sif   docker://amdih/gromacs:2021.1.amd1
singularity pull amdih_lammps_14May2021.sif docker://amdih/lammps:2021.5.14_121

# DFT
singularity pull amdih_cp2k_8.2.sif         docker://amdih/cp2k:8.2

# ML
singularity pull amdih_tf2.7.sif            docker://amdih/tensorflow:rocm5.0-tf2.7-dev
singularity pull amdih_pytorch_1.10.sif     docker://amdih/pytorch:rocm5.0_ubuntu18.04_py3.7_pytorch_1.10.0
