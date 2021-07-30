#!/usr/bin/env python3 

import os
import argparse

from math       import sqrt
from hpc_nvidia import HpcNvidia

class Hpl(HpcNvidia): 
    def __init__(self, 
        size=[], blocksize=[256], pgrid=[], qgrid=[], pmap=0, 
        threshold=16.0, pfact=[1], nbmin=[4], ndiv=[4], rfact=[1], 
        bcast=[0], ai=False, 
        gpu=[], thread=4, sif='hpc-benchmarks_20.10-hpl.sif', prefix='./'):  

        super().__init__(gpu, thread, sif, prefix)

        self.size       = size
        self.blocksize  = blocksize 
        self.pgrid      = pgrid 
        self.qgrid      = qgrid 
        self.pmap       = pmap 
        self.threshold  = threshold 
        self.pfact      = pfact 
        self.nbmin      = nbmin 
        self.ndiv       = ndiv 
        self.rfact      = rfact 
        self.bcast      = bcast 
        self.ai         = ai 
        self.wrapper    = 'hpl.sh'
        self.input      = 'HPL.in'

        # cmdline options 
        self.getopt() 
        
        # HPL requires ncpu = ngpu
        self.ntasks = len(self.gpu)
        self.ngpus  = len(self.gpu)*len(self.host)

        # automatically set size
        if not self.size: 
            self.set_size() 

        # automatically set prid 
        if not self.pgrid: 
            self.set_mpi_grid() 

        self.check_prerequisite('openmpi', '4')
        self.check_prerequisite('connectx', '4')
        self.check_prerequisite('nvidia', '450.36')
        self.check_prerequisite('singularity', '3.4.1')

    def set_mpi_grid(self): 
        self.pgrid = [] 
        self.qgrid = [] 

        for i in range(1, self.ngpus+1):
            if self.ngpus%i == 0:
                p = i
                q = int(self.ngpus/i)

                if p <= q:
                    self.pgrid.append(p)
                    self.qgrid.append(q)

    def set_size(self):
        total_mem = self.ngpus * self._parse_memory()
        self.size = [10000*int(sqrt(0.9*total_mem*1024**2/8)/10000)]

    def write_input(self):
        input_file = os.path.join(self.outdir, 'HPL.in')

        with open(input_file, 'w') as fh:
            fh.write(f'HPL input\n')
            fh.write(f'KISTI\n')
            fh.write(f'{"HPL.out":<20} output file name\n')
            fh.write(f'{"file":<20} device out (6=stdout,7=stderr,file)\n')

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
            fh.write(f'{"2":<20} SWAP (0=bin-exch,1=long,2=mix)\n')
            fh.write(f'{"60":<20} swapping threshold \n')

            # LU (L1 = 1, U = 0 required by HPL-NVIDIA)
            fh.write(f'{"1":<20} L1 in (0=transposed,1=no-transposed) form\n')
            fh.write(f'{"0":<20} U  in (0=transposed,1=no-transposed) form\n')

            # equilibration
            fh.write(f'{"1":<20} qquilibration (0=no,1=yes)\n')

            # memory alignment
            fh.write(f'{"8":<20} memory alignment in double (> 0)\n')

    def run(self): 
        super().run() 

        if self.ai: 
            self.runcmd += '--xhpl-ai'

        self.syscmd(self.runcmd, verbose=1)

    def getopt(self):
        parser = argparse.ArgumentParser(
            usage           = '%(prog)s -s 40000 -b 256 --thread 8 --sif hpc-benchmarks_20.10-hpl.sif',
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
                '-p, --pgrid            list of P grid\n'
                '-q, --qgrid            list of Q grid\n'
                '    --pmap             MPI processes mapping\n'
                '    --threshold        Validation threshold\n'
                '    --pfact            list of PFACT variants\n'
                '    --nbmin            list of NBMIN\n'
                '    --ndiv             list of NDIV\n'
                '    --rfact            list of RFACT variants\n'
                '    --broadcast        MPI broadcasting algorithms\n'
                '    --ai               using hpl-ai\n'
                '    --gpu              GPU indices\n'
                '    --thread           number of omp threads\n'
                '    --sif              path of singularity images\n'
                '    --prefix           output directory\n' ))

        opt.add_argument('-h', '--help'     , action='help'                    , help=argparse.SUPPRESS)
        opt.add_argument('-v', '--version'  , action='version', 
                                              version='%(prog)s '+ self.version, help=argparse.SUPPRESS)
        opt.add_argument('-m', '--mem'      , type=int             , metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-s', '--size'     , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-b', '--blocksize', type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-p', '--pgrid'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument('-q', '--qgrid'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--pmap'     , type=int             , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--threshold', type=float           , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--pfact'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--nbmin'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--ndiv'     , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--rfact'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--bcast'    , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--ai'       , action='store_true'              , help=argparse.SUPPRESS)
        opt.add_argument(      '--gpu'      , type=int  , nargs='*', metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--thread'   , type=int             , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--sif'      , type=str             , metavar='', help=argparse.SUPPRESS)
        opt.add_argument(      '--prefix'   , type=str             , metavar='', help=argparse.SUPPRESS)

        self.args = vars(parser.parse_args())
