#!/usr/bin/env python
import sys
import posix_ipc as ipc

sema_name = sys.argv[1]

sema = ipc.Semaphore(sema_name)

while sema.value < 0:    
    sema.release()

sema.unlink()
sema.close()
