# KSTBench 
This is a set of scripts to perform benchmark tests on HPC systems.<br/>
The scripts will automatically use mostly sensible parameters, although exhaustive parameters scan can be done using given templates.

## List of benchmarks 

| Caterogy             | Benchmark             | Version | System Requirements                                                        |
|----------------------|-----------------------|---------|----------------------------------------------------------------------------|
| Memory Bandwidth     | STREAM_OMP            | 5.10    | working gcc                                                                |
| Memory Bandwidth     | STREAM_CUDA           | 3.4     | cuda >= 10.1                                                               |
| Disk IO              | IOZONE                | 3.419   | working gcc                                                                |
| Disk IO              | IOR                   | 3.3.0   | openmpi >= 3                                                               |
| Linear Algebra       | HPL<br>HPL-AI<br>HPCG | 1.0.0   | singularity >= 3.4.1<br>openmpi >= 4 <br>nvidia >= 450.36<br>connectx >= 4 |
| Numerical Simulation | QE                    | 6.7     | singularity >= 3.1 <br>openmpi >= 3 <br>nvidia >= 450.36                   |
| Numerical Simulation | GROMACS               | 2020.2  | singularity >= 3.1<br>nvidia >= 450.36                                     |

## Python requirements: 
- python >= 3.6
- packaging (https://pypi.org/project/packaging/)
- tabulate (https://pypi.org/project/tabulate/)

## Usage: 
- Download KSTBench: 
```
git clone https://github.com/vitduck/KSTBench
```
- Add KSTBench modules to python search path 
```
cd KSTBench/src 
export PYTHONPATH=`pwd`
```
- Start slurm iteractive session
```
salloc --partition=cas_v100_2 --nodes=2 --ntasks-per-node=40 --gres=gpu:2 --time=12:00:00 --comment=etc
```
