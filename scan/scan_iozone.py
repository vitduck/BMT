#!/usr/bin/env python3

from iozone import Iozone

io = Iozone(
    prefix = '../run/IOZONE', 
    thread_per_host = 8 )

io.build()
io.make_outdir() 
io.write_hostfile() 

bw_write = {} 
bw_read  = {} 
op_write = {} 
op_read  = {} 
threads  = [1, 2, 4, 8, 12, 16]

for thread in threads: 
    io.thread = thread

    # write mode
    io.mode = 0 
    io.run() 
    bw_write[thread] = io.parse_output()/1024

    # read mode
    io.mode = 1
    io.run() 
    bw_read[thread] = io.parse_output()/1024

    #  random read/write mode 
    io.mode = 2
    io.run() 
    op_read[thread], op_write[thread] = io.parse_output() 
    
    io.clean() 

    io.thread *= 2

# summary 
print('\nBandwidth (MB/s):')
print(f'{"#thread":<12} {"write":<12} {"read":<12}')
for thread in threads: 
    print(
       f'{thread:<12d} '
       f'{bw_write[thread]:<12.1f} '
       f'{bw_read[thread]:<12.1f}' )

print('\nIO Operation (ops/sec):')
print(f'{"#thread":<12} {"write":<12} {"read":<12}')
for thread in threads: 
    print(
        f'{thread:<12d} '
        f'{op_write[thread]:<12.1f} '
        f'{op_read[thread]:<12.1f}' )
