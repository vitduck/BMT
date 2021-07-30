#!/usr/bin/env python3

import os 
import re
import sys
import pprint
import inspect
import logging
import subprocess
import packaging.version
import datetime

import prerequisite

class Bmt: 
    version  = '0.5'
    
    # initialize root logger 
    logging.basicConfig( 
        stream  = sys.stderr, 
        level   = logging.ERROR, 
        format  = '%(asctime)s | %(message)s', 
        datefmt = '%Y%m%d_%H:%M:%S')

    def __init__(self, name):
        self.name     = name
        self._prefix  = './'
        self._args    = {} 
        
        # info from slrum 
        self.host     = self._parse_slurm_nodelist()
        self.gpu      = [] 
        self.ntasks   = os.environ['SLURM_NTASKS_PER_NODE']
        
        self.rootdir  = os.path.dirname(inspect.stack()[-1][1])
        self.hostfile = 'hostfile'
        self.output   = f'{name}.out'
        self.runcmd   = ''

    # set up sub-directories 
    @property 
    def prefix(self): 
        return self._prefix

    @prefix.setter 
    def prefix(self, prefix): 
        self._prefix  = prefix
        self.bindir   = os.path.join(prefix, 'bin')
        self.builddir = os.path.join(prefix, 'build')
        self.outdir   = os.path.join(prefix, 'output')

        self.bin      = os.path.join(self.bindir, self.name)
        self.buildcmd = [
            f'mkdir -p {self.builddir}', 
            f'mkdir -p {self.bindir}' ]

    # override attributes from cmd line argument
    @property 
    def args(self): 
        return self._args 

    @args.setter 
    def args(self, args): 
        self._args = args 
        for opt in args:   
            if args[opt]: 
                setattr(self, opt, args[opt]) 

    # print object attributeis for debug purpose 
    def debug(self): 
        pprint.pprint(vars(self))
    
    # check for minimum software/hardware requirements 
    def check_prerequisite(self, module, min_ver):  
        host =  re.sub(':\d+', '', self.host[0])
        
        # insert hostname after ssh 
        cmd     = prerequisite.cmd[module].replace('ssh', f'ssh {host}')
        regex   = prerequisite.regex[module]
        version = re.search(regex, self.syscmd(cmd)).group(1)
                
        if packaging.version.parse(version) < packaging.version.parse(min_ver):
            logging.error(f'{module} >= {min_ver} is required by {self.name}')
            sys.exit()

    # returns if previously built binary exists 
    def build(self):
        if os.path.exists(self.bin): 
            return

        for cmd in self.buildcmd: 
            self.syscmd(cmd, verbose=1)

    # run benchmark 
    def run(self):
        self.output = os.path.join(self.outdir, self.output)

        self.syscmd(self.runcmd, verbose=1, output=self.output)
    
    # creat output directory with time stamp 
    def make_outdir(self): 
        self.outdir = os.path.join(self.outdir, datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S"))

        self.syscmd(f'mkdir -p {self.outdir}', verbose=1)

    # OpenMPI: write hostfile
    def write_hostfile(self): 
        self.hostfile = os.path.join(self.outdir, self.hostfile)

        with open(self.hostfile, 'w') as fh:
            for host in self.host:
                fh.write(f'{host} slots={self.ntasks}\n')

    # IO: clear cache on client (root required) 
    def sync(self):
        if os.getuid() == 0: 
            for host in self.host:
                hostname, slots = host.split(':')

                self.syscmd(f'ssh {hostname} "sync; echo 1 > /proc/sys/vm/drop_caches"') 
        else:
            logging.debug('Cannot flush cache')
    
    # wrapper for system commands 
    def syscmd(self, cmd, verbose=0, output=None):
        if verbose: 
            logger = logging.getLogger() 
            logger.setLevel(logging.INFO)

            if output: 
                logger.info(f'{cmd} > {output}') 
            else: 
                logger.info(cmd)

        try: 
            pout = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            logging.error(f'{e.stderr.decode("utf-8").strip()}')
            sys.exit() 
        else: 
            if output: 
                with open(output, "w") as output_fh:
                    output_fh.write(pout)
            else: 
                return pout

    def gpu_selection(self): 
        return f'CUDA_VISIBLE_DEVICES={",".join(str(gpu) for gpu in self.gpu)}'

    def _parse_slurm_nodelist(self): 
        flat = [] 
        name, index = re.search('(.+)\[(.*)\]', os.environ['SLURM_NODELIST']).group(1,2)

        for node in index.split(','):
            if re.search('-', node):
                node_start, node_end = node.split('-')
                
                flat.extend(range(int(node_start), int(node_end)+1))
            else:
                flat.append(node)

        return [ name+str(item) for item in flat ]
    
    # due to bug in slurm, CUDA_VISIBLE_DEVICES cannot be obtained directly
    def _parse_nvidia_smi(self):
        nvidia_smi = self.syscmd(f'ssh {self.host[0]} "nvidia-smi -L"')

        gpu = re.findall('GPU\s+(\d+)', nvidia_smi)

        return [i for i in gpu]
