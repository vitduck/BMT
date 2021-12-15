#!/usr/bin/env python3 

import os
import re
import argparse

from math  import sqrt
from env   import module_list
from gpu   import gpu_memory
from hpcnv import Hpcnv

class Hpl(Hpcnv): 
    def __init__(self, size=[], blocksize=[256], pgrid=[], qgrid=[], pmap=0, threshold=16.0, pfact=[0], nbmin=[2], ndiv=[2], rfact=[0], bcast=[0], **kwargs):
        super().__init__(**kwargs)

        self.name      = 'HPL/NGC'
        self.wrapper   = 'hpl.sh'
        self.input     = 'HPL.dat'
        self.output    = ''
        self.header    = ['Node', 'Ngpu', 'Thread', 'T/V', 'N', 'NB', 'P', 'Q', 'Status', 'Perf(Tflops)', 'Time(s)']
        
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
        self._reset    = False

        self.getopt()

        # set matrix size
        if not self.size: 
            self._reset = True
            self._matrix_size() 

        # mpi grid 
        if not self.pgrid and not self.qgrid:
            self._mpi_grid() 
 
    # recalcuate MPI grid and matrix size
    @Hpcnv.nodes.setter
    def nodes(self, nodes): 
        super(Hpl, Hpl).nodes.__set__(self, nodes) 
        
        self._mpi_grid() 

        if self._reset and not self.args['size']:
            self._matrix_size()

    @Hpcnv.ngpus.setter
    def ngpus(self, ngpus): 
        super(Hpl, Hpl).ngpus.__set__(self, ngpus) 

        self._mpi_grid() 
        
        if self._reset and not self.args['size']: 
            self._matrix_size()

    def _mpi_grid(self): 
        self.pgrid = []
        self.qgrid = []
        tot_ngpus  = self.nodes*self.ngpus

        for i in range(1, tot_ngpus + 1):
            if tot_ngpus % i == 0:
                p = i
                q = int(tot_ngpus/i)

                if p >= q:
                    self.pgrid.append(p)
                    self.qgrid.append(q)

        # remove iregular 1 x n grid 
        if len(self.pgrid) > 1:
            self.pgrid.pop()
            self.qgrid.pop()

    def _matrix_size(self):
        tot_mem = self.nodes * self.ngpus * gpu_memory(self.host[0])

        self.size = [10000*int(sqrt(0.95*tot_mem*1024**2/8)/10000)]

    def write_input(self):
        self.input = f'HPL-n{self.nodes}-g{self.ngpus}-t{self.omp}.dat'

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
            fh.write(f'{"1":<20} number of lookahead depth\n')
            fh.write(f'{"1":<20} DEPTHs (>=0)\n')

            # swapping ( ignored by HPL-NVIDIA)
            fh.write(f'{"1":<20} SWAP (0=bin-exch,1=long,2=mix)\n')
            fh.write(f'{"192":<20} swapping threshold \n')

            # LU (L1 = 1, U = 0 required by HPL-NVIDIA)
            fh.write(f'{"1":<20} L1 in (0=transposed,1=no-transposed) form\n')
            fh.write(f'{"0":<20} U  in (0=transposed,1=no-transposed) form\n')

            # equilibration
            fh.write(f'{"1":<20} qquilibration (0=no,1=yes)\n')

            # memory alignment
            fh.write(f'{"8":<20} memory alignment in double (> 0)\n')

    def run(self): 
        self.output = f'HPL-n{self.nodes}-g{self.ngpus}-t{self.omp}.out'

        super().run()

    def parse(self): 
        with open(self.output, 'r') as output_fh:
            line = output_fh.readline()

            while line:
                if re.search('W[RC]', line):
                    config, size, blocksize, p, q, time, gflops = line.split()

                    # passed/failed status
                    output_fh.readline()
                    status = output_fh.readline().split()[-1]

                    self.result.append([self.nodes, self.ngpus, self.omp, config, size, blocksize, p, q, status, float(gflops)/1000, time])
                
                line = output_fh.readline()

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -s 40000 -b 256 --omp 4',
            description     = 'HPL Benchmark',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            add_help        = False )

        # options for problem setup
        opt = parser.add_argument_group(
            title       = 'optional arugments',
            description = (
                '-h, --help             show this help message and exit\n'
                '-v, --version          show program\'s version number and exit\n'
                '-s, --size             list of problem size\n'
                '-b, --blocksize        list of block size\n'
                '-p, --pgrid            MPI pgrid\n'
                '-q, --qgrid            MPI qgrid\n'
                '    --pmap             MPI processes mapping\n'
                '    --broadcast        MPI broadcasting algorithms\n'
                '    --threshold        Validation threshold\n'
                '    --pfact            list of PFACT variants\n'
                '    --nbmin            list of NBMIN\n'
                '    --ndiv             list of NDIV\n'
                '    --rfact            list of RFACT variants\n'
                '    --nodes            number of nodes\n'
                '    --ngpus            number of gpus per node\n'
                '    --omp              number of omp threads\n' ))

        opt.add_argument('-h', '--help'     , action='help'                    , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version'  , action='version', 
                                  version='%(prog)s '+ self.version            , help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'     , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-b', '--blocksize', type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-p', '--pgrid'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-q', '--qgrid'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--pmap'     , type=int             , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--bcast'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--threshold', type=float           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--pfact'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--nbmin'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--ndiv'     , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--rfact'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--nodes'    , type=int             , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--ngpus'    , type=int             , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--omp'      , type=int             , metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
