#!/usr/bin/env python 

import glob 
import shutil 

for rundir in [
                    '../run/STREAM/OMP', 
                    '../run/STREAM/CUDA', 
                    '../run/IOZONE', 
                    '../run/IOR', 
                    '../run/HPL', 
                    '../run/HPCG', 
                    '../run/QE', 
                    '../run/GROMACS']: 

    for subdir in glob.glob('/'.join([rundir, '*'])): 
        shutil.rmtree(subdir)
