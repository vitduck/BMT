#!/usr/bin/env python 

import os
import glob 
import shutil 

for rundir in [
        '../run/STREAM/ORG',
        '../run/STREAM/CUDA',
        '../run/IOZONE', 
        '../run/IOR', 
        '../run/HPL', 
        '../run/HPCG', 
        '../run/QE', 
        '../run/GROMACS']: 

    for subdir in glob.glob('/'.join([rundir, '*'])): 
        if os.path.isdir(subdir):
            shutil.rmtree(subdir)
