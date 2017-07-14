__author__ = 'wuqingyi22@gmail.com'

import os, time, json
import subprocess
import scraping

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
    if current_algo:
        process.kill()                      # kill current miner, it doesn't hurt
        current_algo = top_algo
    # start new mining process
    stratum = 'stratum+tcp://' + top_algo['algo'] + pool_url_base + ':' + top_algo['port']
    process = subprocess.Popen([top_algo['miner'], '-a', top_algo['algo'], '-o', stratum, '-u',
                                machine['wallet'], '-p', machine['name'], 'c=BTC'])

    time.sleep(machine['interval'])
    # process = subprocess.Popen(['ping', '-t', '127.0.0.1'])
    # time.sleep(10)
    # process.kill()
    # time.sleep(3)
