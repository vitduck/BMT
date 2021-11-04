#!/usr/bin/env python3 

import os
import re

def slurm_nodelist(): 
    nodelist    = [] 
    name, index = re.search('([a-zA-Z]+)\[?([0-9\-,]+)\]?', os.environ['SLURM_NODELIST']).group(1,2)

    for node in index.split(','):
        if re.search('-', node):
            node_start, node_end = node.split('-')
            length = len(node_start)
                
            # return the list of node with leading zeroes
            nodelist.extend(
                map(lambda x: str(x).zfill(length), 
                range(int(node_start), int(node_end)+1)))
        else:
            nodelist.append(node)

    return [ name+str(node) for node in nodelist ]

def slurm_ntasks(): 
    return int(os.environ['SLURM_NTASKS_PER_NODE'])
