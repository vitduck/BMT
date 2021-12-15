#!/usr/bin/env python3 

import os
import re

def slurm_nodelist(): 
    nodelist    = [] 
    name, index = re.search('([a-zA-Z]+)\[?([0-9\-,]+)\]?', os.environ['SLURM_NODELIST']).group(1,2)

    for node in index.split(','):
        if re.search('-', node):
            istart, iend = node.split('-')
                
            # return the list of node with leading zeroes
            nodelist += [ name + str(node).zfill(len(istart)) for node in range(int(istart), int(iend)+1) ]
        else:
            nodelist += [ name + str(node) ]

    return nodelist
