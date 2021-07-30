#!/usr/bin/env python3

from iozone import Iozone

io = Iozone(
    prefix = '../run/IOZONE' ) 

io.build()
io.make_outdir() 
io.write_hostfile() 

# write mode
io.mode = 0 
io.run() 
bw_write = io.parse_output()

# read mode
io.mode = 1
io.run() 
bw_read = io.parse_output()

# random read/write mode
io.mode = 2 
io.run() 
op_random_read, op_random_write = io.parse_output()

# clean dummy files
io.clean() 

print('\nResult:')
print(f'Write bandwidth: {bw_write/1024:.1f} MB/s')
print(f'Read bandwidth: {bw_read/1024:.1f} MB/s')
print(f'Random write: {op_random_write} ops/sec')
print(f'Random read: {op_random_read } ops/sec')
