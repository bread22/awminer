__author__ = 'wuqingyi22@gmail.com'

import os, time
import subprocess

process = subprocess.Popen(['ping', '-t', '127.0.0.1'])

time.sleep(10)

process.kill()
