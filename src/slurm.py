#!/usr/bin/env python3 

import os
import re

def slurm_nodelist():
    nodelist    = []

    match = re.search('(.*?)\[(.*?)\]', os.environ['SLURM_NODELIST'])

    # multi-node job
    if match:
        name, index = match.groups()

        for node in index.split(','):
            if re.search('-', node):
                istart, iend = node.split('-')

                # return the list of node with leading zeroes
                nodelist += [name + str(node).zfill(len(istart)) for node in range(int(istart), int(iend)+1)]
            else:
                nodelist += [ name + str(node) ]
    # single-node job / local host
    else:
        nodelist = [os.environ['SLURM_NODELIST']]

    return nodelist
