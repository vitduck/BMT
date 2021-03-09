#!/usr/bin/env python 

import os
import argparse
import subprocess 

from shutil    import move
from modulecmd import env
from utils     import download, timestamp

__version__ = '0.2'

# init
parser=argparse.ArgumentParser(
    prog            = 'iozone.py', 
    usage           = '%(prog)s -a', 
    description     = 'IOZONE Benchmark', 
    formatter_class = argparse.RawDescriptionHelpFormatter)

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
        '-b       excel output file']))

# check for exclusivity betwen '-a' and '-i'
group = parser.add_mutually_exclusive_group() 
group.add_argument ('-a', action='store_true',                        help=argparse.SUPPRESS)
group.add_argument ('-i', type=int,                       metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-n', type=int,                       metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-g', type=int,                       metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-y', type=int,                       metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-q', type=int,                       metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-s', type=int,                       metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-r', type=int,                       metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-b', type=str, default='iozone.xls', metavar='', help=argparse.SUPPRESS)
iozone.add_argument('-o', action='store_true' ,                       help=argparse.SUPPRESS)

args = parser.parse_args()

# top directory
root = os.getcwd()

def main():
    env('iozone')

    if not os.path.exists('bin/iozone'): 
        os.makedirs('bin'  , exist_ok=True)
        os.makedirs('build', exist_ok=True)

        download(['http://www.iozone.org/src/current/iozone3_491.tgz'])
    
        build()

    benchmark()

def build():
    os.chdir('build')
    
    # extract 
    print('=> Extracting iozone')
    subprocess.call(['tar', 'xf', 'iozone3_491.tgz'])
    
    # make
    os.chdir('iozone3_491/src/current')

    with open('make.log', 'w') as log: 
        print('=> Building iozone')
        subprocess.call(['make', 'linux'], stderr=log, stdout=log)

    move('iozone',   f'{root}/bin')
    move('make.log', f'{root}'    )

    os.chdir(root)

def benchmark(): 
    # time stamp
    outdir = timestamp()
    output = os.path.join(outdir, 'iozone.out')

    os.makedirs(outdir)

    print(f'=> Output: {output}')

    cmd = ['bin/iozone', '-R', '-b', os.path.join(outdir, args.b)]

    if args.a: 
        cmd.extend(['-a'])

    if args.i: 
       cmd.extend(['-i', str(args.i)])

    if args.n: 
       cmd.extend(['-n', str(args.n)])

    if args.g: 
       cmd.extend(['-g', str(args.g)])

    if args.y: 
       cmd.extend(['-y', str(args.y)])

    if args.q: 
       cmd.extend(['-q', str(args.q)])

    if args.s: 
       cmd.extend(['-s', str(args.s)])

    if args.r: 
       cmd.extend(['-r', str(args.r)])

    with open(output, 'w') as output:
        subprocess.call(cmd, stdout=output)

    os.chdir(root)

if __name__ == "__main__":
    main()
