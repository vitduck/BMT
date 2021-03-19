#!/usr/bin/env python

import re
import os.path
import subprocess

from shutil    import copy
from datetime  import datetime
from packaging import version

def download(file): 
    with open('wget.log', 'w') as log:
        for url in file:
            if not os.path.exists(f'build/{os.path.basename(url)}'):
                print(f'=> Downloading {url}')

                subprocess.call(['wget', url, '-P', 'build'], stderr=log)

def timestamp(): 
    outdir = f'output/{datetime.now().strftime("%Y%m%d_%H:%M:%S")}'

    return outdir

def gcc_ver(min_ver):
    gcc = subprocess.run(['gcc', '--version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ver = re.search('\(GCC\)\s*([\d.]+)', gcc).group(1)

    if version.parse(ver) < version.parse(min_ver):
        raise Exception(f'GCC >= {min_ver} is required to build STREAM-CPU\n')

def cuda_ver(min_ver):
    nvcc = subprocess.run(['nvcc', '--version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ver = re.search('release\s*([\d.]+)', nvcc).group(1)

    if version.parse(ver) < version.parse(min_ver):
        raise Exception(f'CUDA >= {min_ver} is required to build STREAM-CUDA\n')

def sig_ver(min_ver):
    sig = subprocess.run(['singularity', '--version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ver = re.search('version\s*([\d.]+)', sig).group(1)

    if version.parse(ver) < version.parse(min_ver):
        raise Exception(f'Singularity >= {min_ver} is required to run HPL/HPCG-NVIDIA\n')

def nvidia_ver(min_ver):
    sig = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ver = re.search('Version:\s*([\d.]+)', sig).group(1)

    if version.parse(ver) < version.parse(min_ver):
        raise Exception(f'NVIDIA driver >= {min_ver} is required to run HPL/HPCG-NVIDIA\n')

def ompi_ver(min_ver):
    sig = subprocess.run(['mpirun', '--version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ver = re.search('mpirun.+?([\d.]+)', sig).group(1)

    if version.parse(ver) < version.parse(min_ver):
        raise Exception(f'Open MPI >= {min_ver} is required to run HPL/HPCG-NVIDIA\n')

def mellanox_ver(min_ver):
    sig = subprocess.run(['lspci'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ver = re.search('ConnectX\-(\d)', sig).group(1)

    if version.parse(ver) < version.parse(min_ver):
        raise Exception(f'ConnectX >= {min_ver} is required to run HPL/HPCG-NVIDIA\n')
