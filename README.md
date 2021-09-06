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
- Perform all test
```
cd test
./test_all.py
```
- Results
```
[STREAM_OMP] DONE
# Environment: python/3.9.5
# Output: ../run/STREAM/OMP/output/20210906_15:37:14/stream-spread-omp_40.out

   Thread |   Affinity |   Copy(GB/s) |   Scale(GB/s) |   Add(GB/s) |   Triad(GB/s)
----------+------------+--------------+---------------+-------------+---------------
       40 |     spread |        140.1 |         137.4 |       148.8 |         150.7

[STREAM_CUDA] DONE
# Environment: python/3.9.5 cuda/10.1
# Output: ../run/STREAM/CUDA/output/20210906_15:37:17/stream-cuda.out

   Copy(GB/s) |   Mul(GB/s) |   Add(GB/s) |   Triad(GB/s) |   Dot(GB/s)
--------------+-------------+-------------+---------------+-------------
        793.7 |       789.4 |       816.7 |         818.2 |       845.1

[IOZONE] DONE
# Environment: python/3.9.5
# Output: ../run/IOZONE/output/20210906_15:37:20/iozone-0-16m-64k-thr_8.out
# Output: ../run/IOZONE/output/20210906_15:37:20/iozone-1-16m-64k-thr_8.out
# Output: ../run/IOZONE/output/20210906_15:37:20/iozone-2-16m-64k-thr_8.out

   Size |   Record |   Thread |   Write(MB/s) |   Read(MB/s) |   R_Write(OPS) |   R_Read(OPS)
--------+----------+----------+---------------+--------------+----------------+---------------
    16m |      64k |        8 |         460.5 |       1525.2 |        23250.4 |        8560.4

[IOR] DONE
# Environment: python/3.9.5 gcc/8.3.0 mpi/openmpi-3.1.5
# Output: ../run/IOR/output/20210906_15:37:58/ior-n2-p8-t1m-b16m-s16.out

   Node |   Ntask |   Transfer |   Block |   Segment |   Size |   Write(MB/s) |   Read(MB/s) |   Write(Ops) |   Read(Ops)
--------+---------+------------+---------+-----------+--------+---------------+--------------+--------------+-------------
      2 |       8 |         1m |     16m |        16 |     4g |        3804.6 |       3983.4 |       3804.6 |      3983.4

[QE] DONE
# Environment: python/3.9.5 nvidia_hpc_sdk/21.5
# Output: ../run/QE/output/20210906_15:38:03/Si-n2_g2_p2_t1_l1.out

   Node |   Ngpu |   Ntask |   Thread |   Npool |   Time(s)
--------+--------+---------+----------+---------+-----------
      2 |      2 |       2 |        1 |       1 |     157.8

[QE_NGC] DONE
# Environment: python/3.9.5 pgi/19.1 cuda/10.0 cudampi/openmpi-3.1.5_hwloc singularity/3.6.4
# Output: ../run/QE/output/20210906_15:40:47/Si-n2_g2_p2_t1_l1.out

   Node |   Ngpu |   Ntask |   Thread |   Npool |   Time(s)
--------+--------+---------+----------+---------+-----------
      2 |      2 |       2 |        1 |       1 |     125.2

[GROMACS] DONE
# Environment: python/3.9.5 gcc/8.3.0 cuda/10.1 cudampi/openmpi-3.1.5_hwloc
# Output: ../run/GROMACS/output/20210906_15:42:58/stmv-n2_g2_p40_t1.log

   Node |   Ngpu |   Ntask |   Thread |   Perf(ns/day)
--------+--------+---------+----------+----------------
      2 |      2 |      40 |        1 |           19.9

[GROMACS_NGC] DONE
# Environment: python/3.9.5 gcc/8.3.0 cuda/10.1 cudampi/openmpi-3.1.5_hwloc singularity/3.6.4
# Output: ../run/GROMACS/output/20210906_15:43:58/stmv-n1_g2_p40_t1.log

   Node |   Ngpu |   Ntask |   Thread |   Perf(ns/day)
--------+--------+---------+----------+----------------
      1 |      2 |      40 |        1 |           13.3

[HPL] DONE
# Environment: python/3.9.5 gcc/8.3.0 cuda/10.1 cudampi/openmpi-test_2 singularity/3.6.4
# Output: ../run/HPL/output/20210906_15:45:03/HPL-n2-g2-t4.out

   Node |   Ngpu |   Thread |      T/V |      N |   NB |   P |   Q |   Status |   Time(s) |   Perf(Tflops)
--------+--------+----------+----------+--------+------+-----+-----+----------+-----------+----------------
      2 |      2 |        4 | WR00C4C4 | 120000 |  256 |   1 |   4 |   PASSED |      62.3 |           18.1
      2 |      2 |        4 | WR00C4C4 | 120000 |  256 |   2 |   2 |   PASSED |      51.2 |           22.0

[HPL_AI] DONE
# Environment: python/3.9.5 gcc/8.3.0 cuda/10.1 cudampi/openmpi-test_2 singularity/3.6.4
# Output: ../run/HPL/output/20210906_15:48:34/HPL-n2-g2-t4.out

   Node |   Ngpu |   Thread |      T/V |      N |   NB |   P |   Q |   Status |   Time(s) |   Perf(Tflops) |   Perf_IRS(Tflops)
--------+--------+----------+----------+--------+------+-----+-----+----------+-----------+----------------+--------------------
      2 |      2 |        4 | WR00C4C4 | 120000 |  256 |   1 |   4 |   FAILED |      19.3 |           59.7 |               39.5
      2 |      2 |        4 | WR00C4C4 | 120000 |  256 |   2 |   2 |   PASSED |      12.9 |           89.4 |               71.5

Perf:     half-precision performance
Perf_IRS: mixed-precision performance (Iteractive Residual Solver)

[HPCG] DONE
# Environment: python/3.9.5 gcc/8.3.0 cuda/10.1 cudampi/openmpi-test_2 singularity/3.6.4
# Output: ../run/HPCG/output/20210906_15:50:44/HPCG-n2-g2-t4-256x256x256.out

   Node |   Ngpu |   Thread |   Mpi |        Grid |   Time(s) |   SpMV(GFlops) |   SymGS(GFlops) |   Total(GFlops) |   Final(GFlops)
--------+--------+----------+-------+-------------+-----------+----------------+-----------------+-----------------+-----------------
      2 |      2 |        4 | 2x2x1 | 256x256x256 |      62.0 |          445.3 |           640.2 |           587.7 |           557.3

SpMV:  sparse matrix-vector multiplication
SymGS: symmetric Gauss-Seidel method
Total: total performance
Final: total performance including initialization overhead
```
