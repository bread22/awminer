__author__ = 'wuqingyi22@gmail.com'

import os, time
import subprocess
import scraping

pool = 'http://zpool.ca/'
config = 'algos_zpool.json'

zpool = scraping.MiningPool(pool, config)

print zpool.getTopProfit()

# process = subprocess.Popen(['ping', '-t', '127.0.0.1'])
#
# time.sleep(10)
#
# process.kill()
