#!/usr/bin/env python 

import re 

from bmt import Bmt

class Stream(Bmt):
   def parse_output(self, function): 
        with open(self.output, 'r') as output_fh: 
            for line in output_fh: 
                if re.search(f'{function}:?', line):
                    return float(line.split()[1])
