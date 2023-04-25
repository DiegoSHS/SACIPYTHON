import os
import subprocess

libs = ['requests','pyserial','json','flask','flask_cors','threading',]
for lib in libs:
    try:
        import lib
    except ImportError:
        subprocess.call(['pip','install',lib])
        subprocess.check_call(['pip','install',lib])