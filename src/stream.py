#!/usr/bin/env python 

import re 

from bmt import Bmt

class Stream(Bmt):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        
        # stream kernel
        self.kernel   = ['Copy', 'Scale', 'Add', 'Triad']
    
    def parse(self):
        bandwidth = [] 

        with open(self.output, 'r') as output_fh: 
            for line in output_fh: 
                for kernel in self.kernel:
                    if re.search(f'{kernel}:?', line):
                        bandwidth.append(float(line.split()[1])/1000)

        self.result.append(bandwidth)
