import os
import subprocess

libs = ['requests','pyserial','flask','flask_cors']
for lib in libs:
    try:
        import lib
    except ImportError:
        subprocess.call(['pip','install',lib])
        subprocess.check_call(['pip','install',lib])