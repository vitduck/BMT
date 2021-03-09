#!/usr/bin/env python

import re
import os.path
import subprocess

from shutil import copy
from datetime import datetime

def download(file): 
    with open('wget.log', 'w') as log:
        for url in file:
            if not os.path.exists(f'build/{os.path.basename(url)}'):
                print(f'=> Downloading {url}')

                subprocess.call(['wget', url, '-P', 'build'], stderr=log)

def timestamp(): 
    outdir = f'output/{datetime.now().strftime("%Y%m%d_%H:%M:%S")}'

    return outdir

def gcc_version_check():
    gcc_ver = subprocess.run(['gcc', '--version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    match   = re.match('gcc \(GCC\) (\d)\.\d\.\d', gcc_ver)

    if int(match.group(1)) < 7:
        raise Exception("GCC >=7 is required to build CPU-STREAM\n")
