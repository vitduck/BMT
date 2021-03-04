#!/usr/bin/env python 

import os
import argparse
import subprocess 

from shutil import copy

__version__ = '0.1'

# init
parser=argparse.ArgumentParser(
    prog='iozone.py', 
    description='IOZONE Benchmark', 
    usage='%(prog)s -a', 
    formatter_class=argparse.RawDescriptionHelpFormatter)

# version string
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

# options for stream setup
iozone = parser.add_argument_group(
    title='IOZONE Parameters',
    description='\n'.join([
        '-a       full automatic mode (record: 4KB->16MB, size: 64KB->512MB)',
        '-i       test mode:',
        '            0 = write/re-write',
        '            1 = read/re-read',
        '            2 = random-read/write',
        '            3 = read-backwards',
        '            4 = re-write-records',
        '            5 = stride-read',
        '            6 = fwrite/re-fwrite',
        '            7 = fread/re-fread',
        '            8 = random-mix',
        '            9 = pwrite/re-pwrite',
        '           10 = pread/re-pread',
        '           11 = pwritev/re-pwritev',
        '           12 = preadv/re-preadv',
        '-n       minimum file size in auto mode (KB)', 
        '-g       maximum file size in auto mode (KB)', 
        '-y       minimum record size in auto mode (KB)', 
        '-q       maximum record size in auto mode (KB)', 
        '-s       size of file to test (KB)',
        '-r       record size to test (KB)',
        '-o       synchronous write to disk',
        '-b       excel output file', 
        '--dir    local test directory']))

# check for exclusivity betwen '-a' and '-i'
group = parser.add_mutually_exclusive_group() 
group.add_argument( '-a'   , action='store_true',  help=argparse.SUPPRESS)
group.add_argument( '-i'   , type=int, metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-n'   , type=int, metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-g'   , type=int, metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-y'   , type=int, metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-q'   , type=int, metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-s'   , type=int, metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-r'   , type=int, metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-o'   , action='store_true' , help=argparse.SUPPRESS)
iozone.add_argument('-b'   , type=str, default='iozone.xls', metavar='', help=argparse.SUPPRESS)
iozone.add_argument('--dir', type=str, default='./', metavar='', help=argparse.SUPPRESS)

args = parser.parse_args()

def main():
    if args.a or args.i:
        os.chdir(args.dir)

        download()
        build()
        benchmark()

def download():
    subprocess.call(['wget', 'http://www.iozone.org/src/current/iozone3_491.tgz'])

def build():
    subprocess.call(['tar', 'xf', 'iozone3_491.tgz'])

    os.chdir('iozone3_491/src/current')

    subprocess.call(['make', 'linux'])

    os.chdir('../../../')

    copy('iozone3_491/src/current/iozone','.')

def benchmark(): 
    cmd = ['./iozone', '-R', '-b', args.b]

    if args.a: 
        cmd += ['-a']
    if args.i: 
       cmd += ['-i', str(args.i)]
    if args.n: 
       cmd += ['-n', str(args.n)]
    if args.g: 
       cmd += ['-g', str(args.g)]
    if args.y: 
       cmd += ['-y', str(args.y)] 
    if args.q: 
       cmd += ['-q', str(args.q)] 
    if args.s: 
       cmd += ['-s', str(args.s)]
    if args.r: 
       cmd += ['-r', str(args.r)]

    subprocess.call(cmd)

if __name__ == "__main__":
    main()
