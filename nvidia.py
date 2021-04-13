#!/usr/bin/env python 

import os
import re
import glob

from math import sqrt
from bmt  import Bmt

class Nvidia(Bmt): 
    def __init__(self, name, exe, output, module, min_ver, url, args): 
        super().__init__(name, exe, output, module, min_ver, url, args)

        # total number of gpus 
        self.socket = [0,1]
        self.ngpus  = len(args.host)*len(args.device)
       
        # nvidia-hpc input & wrapper script 
        self.input   = ''
        self.wrapper = ''

        # benchmark script 
        self.script  = 'run.sh'
        self.run_cmd = ['sh', './run.sh']

        # path to singularity image
        self.sif  =  os.path.relpath(self.args.sif, self.output_dir)

    def __cpu_affinity(self):
        affinity = []
        
        # requies python >=3
        for affinity_set in zip(self.socket, self.args.device_per_socket):
            # for cas_v100_2: two GPUs in socket #1
            if affinity_set[1] == 0: 
                continue 

            affinity = affinity + ([affinity_set[0]]*affinity_set[1])

        return affinity

    def mpirun_cmd(self):
        cmd      = ['mpirun']
        affinity = self.__cpu_affinity()
        
        # mpi options 
        cmd.append(f'{"":>4}--np {self.mpiprocs}')
        cmd.append(f'{"":>4}--host {",".join(self.args.host)}')

        # disabled infiniband verb
        cmd.append(f'{"":>4}--mca btl ^openib')

        # singularity options
        cmd.append(f'{"":>4}singularity')
        cmd.append(f'{"":>8}run')
        cmd.append(f'{"":>8}--nv')
        cmd.append(f'{"":>8}{self.sif}')

        # hpc-nvidia wrapper
        cmd.append(f'{"":>8}{self.wrapper}')
        cmd.append(f'{"":>12}--dat {self.input}')
        cmd.append(f'{"":>12}--cpu-cores-per-rank {self.args.thread}')
        cmd.append(f'{"":>12}--cpu-affinity {":".join(str(cpu) for cpu in affinity)}')
        cmd.append(f'{"":>12}--gpu-affinity {":".join(str(gpu) for gpu in self.args.device)}')

        return cmd

    def write_env(self, fh): 
        fh.write(f'export CUDA_VISIBLE_DEVICES={",".join(str(gpu) for gpu in self.args.device)}\n')

    def write_mpirun_cmd(self, cmd, fh): 
        # formatted cmd block
        length = len(max(cmd, key = len)) 

        # join cmd with newline print to file
        formatted_cmd = '\\\n'.join(f'{line:<{length}} ' for line in cmd)
        
        fh.write(f'{formatted_cmd}')

    def write_input(self): 
        pass 

    def write_script(self): 
        cmd    = self.mpirun_cmd()
        script = os.path.join(self.output_dir, self.script)

        with open(script, 'w') as fh:  
            self.write_env(fh)
            fh.write('\n')
            self.write_mpirun_cmd(cmd, fh)

    def run(self): 
        self.write_input() 
        self.write_script() 

        super().run()

class Hpl(Nvidia): 
    def __init__(self, name, exe, output, module, min_ver, url, args): 
        super().__init__(name, exe, output, module, min_ver, url, args)

        self.wrapper  = 'hpl.sh'
        self.input    = 'HPL.in'

        #  if args.pgrid[0] * args.qgrid[0] != self.ngpus:
            #  raise Exception("Error: HPL requires CPU/GPU = 1")

    # mpi grid scan
    def __mpi_grid(self): 
        p_scan = []
        q_scan = []

        for i in range(1,self.ngpus+1):
            if self.ngpus%i == 0:
                p = i
                q = int(self.ngpus/i)

                if p <= q:
                    p_scan.append(p)
                    q_scan.append(q)

        return p_scan, q_scan

    # add ai options 
    def mpirun_cmd(self): 
        cmd = super().mpirun_cmd()

        # switch to hpl-ai
        if self.args.ai:
            cmd.append(f'{"":>12}--xhpl-ai')

        return cmd 

    def parameter_scan(self):
        device_mem = re.search('(\d+)\s*[g|G]B', self.args.mem)
        total_mem  = self.ngpus * float(device_mem.group(1))
        
        # matrix size
        # 90% of total memeory
        self.args.size = [10000*int(sqrt(0.9*total_mem*1024**3/8)/10000)]

        # blocksize 
        self.args.blocksize = [64, 128, 256, 512, 1024]

        # mpi grid 
        self.args.pgrid, self.args.qgrid = self.__mpi_grid()

        # general algorithms
        self.args.pfact = [0, 1, 2] 
        self.args.rfact = [0, 1, 2] 

        self.args.nbmin = [2, 4, 8] 
        self.args.ndiv  = [2, 3, 4]
        
        # bcast algorithms 
        # 4 leads to buffer overflown
        self.args.bcast = [0, 1, 2, 3, 5]

        self.run()

    def summary(self): 
        scan    = [] 
        output  = os.path.join(self.output_dir, 'HPL.out')

        # extract perf param from HPL.out
        with open(output, 'r') as output_fh:  
            for line in output_fh:
                if re.search('^W[RC]', line): 
                    scan.append(line.split())
        
        # sorted data according to gflops, i.e last column 
        sorted_scan = sorted(scan, key=lambda x : float(x[-1]), reverse=True)

        # write sorted data to perf.dat 
        output = os.path.join(self.output_dir, 'perf.dat')
        
        with open(output, 'w') as output_fh: 
            # print header
            header = ['T/V', 'N', 'NB', 'P', 'Q', 'Time', 'Gflops'] 
            output_fh.write(' '.join(map('{:10}'.format, header))+'\n')

            for line in sorted_scan: 
                output_fh.write(' '.join(map('{:10}'.format, line))+'\n')

        #  write input with optimized parameter
        self.input = 'HPL.in_opt'
        
        # algorithm string 
        algo = re.search('W[RC]0(\d)([RCL])(\d)([RCL])(\d)', sorted_scan[0][0])
        
        # bcast 
        self.args.bcast = algo.group(1)

        # rfacts 
        if algo.group(2) == 'L': self.args.rfact = [0]
        if algo.group(2) == 'C': self.args.rfact = [1]
        if algo.group(2) == 'R': self.args.rfact = [2]

        # nbdiv 
        self.args.ndiv = [algo.group(3)]

        # pfacts 
        if algo.group(4) == 'L': self.args.pfact = [0]
        if algo.group(4) == 'C': self.args.pfact = [1]
        if algo.group(4) == 'R': self.args.pfact = [2]

        # nbmin 
        self.args.nbmin = [algo.group(5)]

        # blocksize 
        self.args.blocksize = [sorted_scan[0][2]]

        # mpi grid 
        self.args.pgrid     = [sorted_scan[0][3]]
        self.args.qgrid     = [sorted_scan[0][4]]

        self.write_input() 

    def write_input(self): 
        input_file = os.path.join(self.output_dir, self.input)

        with open(input_file, 'w') as fh: 
            fh.write(f'HPL input\n')
            fh.write(f'KISTI\n')
            fh.write(f'{"HPL.out":<20} output file name\n')
            fh.write(f'{"file":<20} device out (6=stdout,7=stderr,file)\n')
        
            # problem size
            fh.write(f'{len(self.args.size):<20} number of problem size (N)\n')
            fh.write(f'{" ".join(str(s) for s in self.args.size):<20} Ns\n')

            # block size
            fh.write(f'{len(self.args.blocksize):<20} number of Nbs\n')
            fh.write(f'{" ".join(str(s) for s in self.args.blocksize):<20} NBs\n')

            # mpi grid
            fh.write(f'{self.args.pmap:<20} PMAP process mapping (0=Row-,1=Column-major)\n')
            fh.write(f'{len(self.args.qgrid):<20} number of process grids (P x Q)\n')
            fh.write(f'{" ".join(str(s) for s in self.args.pgrid):<20} Ps\n')
            fh.write(f'{" ".join(str(s) for s in self.args.qgrid):<20} Qs\n')

            # threshold (default)
            fh.write(f'{"-16.0":<20} threshold\n')

            # PFACT
            fh.write(f'{len(self.args.pfact):<20} number of panel fact\n')
            fh.write(f'{" ".join(str(s) for s in self.args.pfact):<20} PFACTs (0=left, 1=Crout, 2=Right) \n')

            # NBMIN
            fh.write(f'{len(self.args.nbmin):<20} of recursive stopping criterium\n')
            fh.write(f'{" ".join(str(s) for s in self.args.nbmin):<20} NBMINs (>=1)\n')

            # NDIV
            fh.write(f'{len(self.args.ndiv):<20} number of recursive stopping criterium\n')
            fh.write(f'{" ".join(str(s) for s in self.args.ndiv):<20} NDIVs\n')

            # RFACT
            fh.write(f'{len(self.args.rfact):<20} number of recursive panel fact\n')
            fh.write(f'{" ".join(str(s) for s in self.args.rfact):<20} RFACTs (0=left, 1=Crout, 2=Right) \n')

            # BCAST
            fh.write(f'{len(self.args.bcast):<20} number of broadcast\n')
            fh.write(f'{" ".join(str(s) for s in self.args.bcast):<20} BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)\n')

            # look-ahead (ignored by HPL-NVIDIA)
            fh.write(f'{"1":<20} number of lookahead depth\n')
            fh.write(f'{"1":<20} DEPTHs (>=0)\n')

            # swapping ( ignored by HPL-NVIDIA)
            fh.write(f'{"2":<20} SWAP (0=bin-exch,1=long,2=mix)\n')
            fh.write(f'{"60":<20} swapping threshold \n')

            # LU (L1 = 1, U = 0 required by HPL-NVIDIA)
            fh.write(f'{"1":<20} L1 in (0=transposed,1=no-transposed) form\n')
            fh.write(f'{"0":<20} U  in (0=transposed,1=no-transposed) form\n')

            # equilibration
            fh.write(f'{"1":<20} qquilibration (0=no,1=yes)\n')

            # memory alignment
            fh.write(f'{"8":<20} memory alignment in double (> 0)\n')

class Hpcg(Nvidia): 
    def __init__(self, name, exe, output, module, min_ver, url, args): 
        super().__init__(name, exe, output, module, min_ver, url, args)

        self.wrapper = 'hpcg.sh'
        self.input   = 'HPCG.in'

    # bug in hpcg image where LD_LIBRARY_PATH is not set correctly
    def write_env(self, fh): 
        super().write_env(fh)

        fh.write(f'export SINGULARITYENV_LD_LIBRARY_PATH=/usr/local/cuda-11.1/targets/x86_64-linux/lib:$LD_LIBRARY_PATH\n')

    def write_input(self):
        input_file = os.path.join(self.output_dir, self.input)

        with open(input_file, 'w') as input:
            input.write(f'HPCG input\n')
            input.write(f'KISTI\n')
            input.write(f'{" ".join(str(grid) for grid in self.args.grid)}\n')
            input.write(f'{self.args.time}')

    def parameter_scan(self):
        grid = [8, 16, 32, 64, 128, 256]

        for n in grid:
            self.args.grid = [n,n,n]

            self.input  = f'HPCG-{"x".join([str(n)]*3)}.in'
            self.output = f'HPCG-{"x".join([str(n)]*3)}.out'

            self.run() 

    def summary(self):
        scan = []

        # parse output file 
        for output in glob.glob('*.out'):
            nx, ny, nz = re.search('(\d+)x(\d+)x(\d+)', output).groups()

            with open(output, 'r') as fh:
                for line in fh:
                    if re.search('final =', line):
                        scan.append([nx, ny, nz, float(line.split()[2])])

        #  sorted perf 
        sorted_scan = sorted(scan, key=lambda x : x[-1], reverse=True)

        # write sorted gflops to file 
        output = os.path.join(self.output_dir, 'perf.dat')
        with open(output, 'w') as output_fh:
            # header
            header = ['nx', 'ny', 'nz', 'Gflops'] 
            output_fh.write(' '.join(map('{:7}'.format, header))+'\n')

            for perf in sorted_scan:
                output_fh.write(' '.join(map('{:7}'.format, perf))+'\n')

        # write optimized input file 
        self.input     = 'HPCG.in_opt'
        self.args.grid = sorted_scan[0][0:3]
        self.write_input() 
