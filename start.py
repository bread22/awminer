__author__ = 'wuqingyi22@gmail.com'

import os, time
import subprocess

process = subprocess.Popen('pingbat.bat')

time.sleep(20)

process.kill()
