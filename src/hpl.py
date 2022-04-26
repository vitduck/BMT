#!/usr/bin/env python3 

import os
import re
import argparse
import shutil
import logging 

from math    import sqrt
from cpu     import cpu_memory
from bmt_mpi import BmtMpi

class Hpl(BmtMpi): 
    def __init__(
        self, size=[], blocksize=[], pgrid=[], qgrid=[], pmap=0, bcast=[3],  
        threshold=16.0, pfact=[0], nbmin=[2], ndiv=[2], rfact=[0], 
        memory=[], **kwargs ):

        super().__init__(**kwargs)

        self.name      = 'HPL'
        self.bin       = os.path.join(self.bindir,'xhpl') 

        self.size      = size 
        self.blocksize = blocksize 
        self.pmap      = pmap 
        self.pgrid     = pgrid 
        self.qgrid     = qgrid 
        self.threshold = threshold 
        self.pfact     = pfact 
        self.nbmin     = nbmin 
        self.ndiv      = ndiv 
        self.rfact     = rfact 
        self.bcast     = bcast 

        # use 90% memory by default 
        # note that this may cause problem with cgroups 
        self.memory    = memory or [0.9*self._total_memory()]

        self.input     = 'HPL.dat'
        self.output    = ''

        self.header    = [
            'node', 'task', 'omp', 'gpu', 
            'n', 'nb', 'p', 'q', 'bcast', 
            'rfact', 'ndiv', 'pfact', 'nbmin', 
            'status', 'perf(TFLOPS)', 'time(s)' ]
        
        # cpu-specific parameters 
        self.depth     = [1]  
        self.swap      = 1 
        self.swap_thr  = 64 
        self.l1        = 0 
        self.u         = 0 
        
        # cmdline options 
        self.parser.usage        = '%(prog)s -s 40000 -b 256 --omp 4'
        self.parser.description  = 'HPL Benchmark'

        self.option.description += ( 
            '-s, --size           list of problem size\n'
            '-b, --blocksize      list of block size\n'
            '-p, --pgrid          MPI pgrid\n'
            '-q, --qgrid          MPI qgrid\n'
            '    --pmap           MPI processes mapping\n'
            '    --bcast          MPI broadcasting algorithms\n'
            '    --threshold      Validation threshold\n'
            '    --pfact          list of PFACT variants\n'
            '    --nbmin          list of NBMIN\n'
            '    --ndiv           list of NDIV\n'
            '    --rfact          list of RFACT variants\n'
            '    --memory         memory usage (GB)\n' )

    def info(self): 
        super().info() 
        
        # AMD BLIS
        for env in self.mpi.env: 
            if re.search('BLIS', env): 
                logging.info(f'export {env} = {self.mpi.env[env]}')

    def write_input(self):
        with open(self.input, 'w') as fh:
            fh.write(f'HPL input\n')
            fh.write(f'BMT\n')
            fh.write(f'{"HPL.out":<20} output file name\n')
            fh.write(f'{"6":<20} device out (6=stdout,7=stderr,file)\n')

            # problem size
            fh.write(f'{len(self.size):<20} number of problem size (N)\n')
            fh.write(f'{" ".join(str(s) for s in self.size):<20} Ns\n')

            # block size
            fh.write(f'{len(self.blocksize):<20} number of Nbs\n')
            fh.write(f'{" ".join(str(s) for s in self.blocksize):<20} NBs\n')

            # mpi grid
            fh.write(f'{self.pmap:<20} PMAP process mapping (0=Row-,1=Column-major)\n')
            fh.write(f'{len(self.qgrid):<20} number of process grids (P x Q)\n')
            fh.write(f'{" ".join(str(s) for s in self.pgrid):<20} Ps\n')
            fh.write(f'{" ".join(str(s) for s in self.qgrid):<20} Qs\n')

            # threshold (default)
            fh.write(f'{self.threshold:<20} threshold\n')

            # PFACT
            fh.write(f'{len(self.pfact):<20} number of panel fact\n')
            fh.write(f'{" ".join(str(s) for s in self.pfact):<20} PFACTs (0=left, 1=Crout, 2=Right) \n')

            # NBMIN
            fh.write(f'{len(self.nbmin):<20} of recursive stopping criterium\n')
            fh.write(f'{" ".join(str(s) for s in self.nbmin):<20} NBMINs (>=1)\n')

            # NDIV
            fh.write(f'{len(self.ndiv):<20} number of recursive stopping criterium\n')
            fh.write(f'{" ".join(str(s) for s in self.ndiv):<20} NDIVs\n')

            # RFACT
            fh.write(f'{len(self.rfact):<20} number of recursive panel fact\n')
            fh.write(f'{" ".join(str(s) for s in self.rfact):<20} RFACTs (0=left, 1=Crout, 2=Right) \n')

            # BCAST
            fh.write(f'{len(self.bcast):<20} number of broadcast\n')
            fh.write(f'{" ".join(str(s) for s in self.bcast):<20} BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)\n')

            # look-ahead (ignored by HPL-NVIDIA)
            fh.write(f'{len(self.depth):<20} number of lookahead depth\n')
            fh.write(f'{" ".join(str(s) for s in self.depth):<20} DEPTHs (>=0)\n')

            # swapping (ignored by HPL-NVIDIA)
            fh.write(f'{self.swap:<20} SWAP (0=bin-exch,1=long,2=mix)\n')
            fh.write(f'{self.swap_thr:<20} swapping threshold \n')

            # LU (L1 = 1, U = 0 required by HPL-NVIDIA)
            fh.write(f'{self.l1:<20} L1 in (0=transposed,1=no-transposed) form\n')
            fh.write(f'{self.u:<20} U  in (0=transposed,1=no-transposed) form\n')

            # equilibration
            fh.write(f'{"1":<20} qquilibration (0=no,1=yes)\n')

            # memory alignment
            fh.write(f'{"8":<20} memory alignment in double (> 0)\n')

        # back up input file
        shutil.copy(self.input, f'HPL-n{self.mpi.node}-g{self.mpi.task}-t{self.mpi.omp}.dat')

    def run(self): 
        # default matrix size
        if not self.size: 
            self.opt_matrix_size() 

        # default HPL grid 
        if not self.pgrid or not self.qgrid:
            self.opt_mpi_grid() 

        os.chdir(self.outdir)

        self.write_input()
        self.mpi.write_hostfile()
        
        self.runcmd = f'{self.mpi.run()} {self.bin}'
        self.output = f'HPL-n{self.mpi.node}-t{self.mpi.task}-o{self.mpi.omp}.out'
        
        if self.mpi.gpu:
            self.output = re.sub(r'(-o\d+)', rf'\1-g{self.mpi.gpu}', self.output, 1)
        
        for i in range(1, self.count+1): 
            if self.count > 1: 
                self.output = re.sub('out(\.\d+)?', f'out.{i}', self.output)

            super().run(1)

    def parse(self): 
        with open(self.output, 'r') as output_fh:
            line = output_fh.readline()

            while line:
                if re.search('W[RC]', line):
                    config, size, blocksize, p, q, time, gflops = line.split()

                    # passed/failed status
                    while True: 
                        status = output_fh.readline()
                        if re.search('(PASSED|FAILED)', status): 
                            status = status.split()[-1]
                            break

                    # split config into string, the first character has no meaning 
                    mu, ordering, depth, bcast, rfact, ndiv, pfact, nbmin = list(config)
                    
                    # hash key 
                    key = ",".join(map(str, [self.mpi.node, self.mpi.task, self.mpi.omp, self.mpi.gpu, size, blocksize, p, q, bcast, rfact, ndiv, pfact, nbmin, status]))
                    
                    # hash initialization
                    if not self.result[key]['gflops']: 
                        self.result[key]['gflops'] = [] 
                        self.result[key]['time']   = [] 

                    self.result[key]['gflops'].append(float(gflops)/1000) 
                    self.result[key]['time' ].append( float(time)) 

                line = output_fh.readline()

    def opt_mpi_grid(self): 
        self.pgrid = [] 
        self.qgrid = []

        tot_mpi_ranks  = self.mpi.node * self.mpi.task

        for i in range(1, tot_mpi_ranks + 1):
            if tot_mpi_ranks % i == 0:
                p = i
                q = int(tot_mpi_ranks/i)

                if p >= q:
                    self.pgrid.append(p)
                    self.qgrid.append(q)

                    break

        # remove iregular n x 1 grid
        #  if len(pgrid) > 1:
            #  pgrid.pop()
            #  qgrid.pop()

    def opt_matrix_size(self):
        self.size = [] 

        for memory in self.memory: 
            gigabyte_regex = re.search('(\d+)GB', str(memory))
            percent_regex  = re.search('(\d+)%' , str(memory))
            
            # convert GB -> byte 
            if gigabyte_regex:  
                memory = self._scale()*int(gigabyte_regex.group(1))*1000**3

            # convert % total memory -> byte
            if percent_regex: 
                memory = self._total_memory()*int(percent_regex.group(1))/100
            
            # round matrix size to nearest 10000 
            self.size.append(10000*int(sqrt(memory/8)/10000))

    def getopt(self):
        self.option.add_argument('-s', '--size'     , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument('-b', '--blocksize', type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument('-p', '--pgrid'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument('-q', '--qgrid'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--pmap'     , type=int             , metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--bcast'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--threshold', type=float           , metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--pfact'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--nbmin'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--ndiv'     , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--rfact'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        self.option.add_argument(      '--memory'   , type=float, nargs='*', metavar='', help=argparse.SUPPRESS)

        super().getopt() 

    def _scale(self): 
        return self.mpi.node

    # total memory in Byte
    def _total_memory(self): 
        return self._scale()*cpu_memory()*1000
