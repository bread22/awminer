__author__ = 'wuqingyi22@gmail.com'

import time
from datetime import datetime
import json
import subprocess
import scraping
import logging

logging.basicConfig(filename='runtime.log')
pool = 'http://zpool.ca/'
pool_url_base = '.mine.zpool.ca'
config = 'algos_zpool.json'
miner_config = 'mining_machine.json'

zpool = scraping.MiningPool(pool, config)

# print zpool.getTopProfit()
with open(miner_config) as fn:
    machine = json.load(fn)
current_algo = {}

while True:
    top_algo = zpool.getTopProfit()         # get top algo
    logging.info(datetime.now().isoformat(), top_algo)
    if current_algo:
        process.kill()                      # kill current miner, it doesn't hurt
        time.sleep(10)
    current_algo = top_algo

    # start new mining process
    stratum = 'stratum+tcp://' + top_algo['algo'] + pool_url_base + ':' + top_algo['port']
    mining_cmd = [top_algo['miner'], '-a', top_algo['algo'], '-o', stratum, '-u',
                                machine['wallet'], '-p', machine['name'], 'c=BTC']
    print mining_cmd
    process = subprocess.Popen([top_algo['miner'], '-a', top_algo['algo'], '-o', stratum, '-u',
                                machine['wallet'], '-p', machine['name'], 'c=BTC'])

    time.sleep(30)
    # time.sleep(machine['interval']*60)

