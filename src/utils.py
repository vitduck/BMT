#!/usr/bin/env python3 

def scan_thread(max_thread, step_thread): 
    thread = list(range(0, max_thread+1, step_thread))
    thread[0] = 1 

    return thread
