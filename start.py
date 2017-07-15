__author__ = 'wuqingyi22@gmail.com'

import time
import json
import subprocess
import scraping
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    filename='runtime.log'
)
logger = logging.getLogger()

pool = 'http://zpool.ca/'
pool_url_base = '.mine.zpool.ca'
config = 'algos_zpool.json'
miner_config = 'mining_machine.json'

zpool = scraping.MiningPool(pool, config)

with open(miner_config) as fn:
    machine = json.load(fn)
current_algo = {}

while True:
    logger.info('Start scraping')
    top_algo = zpool.getTopProfit()         # get top algo
    while not top_algo:
        logger.warning('Scraping failed, wait 10 minutes and retry')
        time.sleep(600)
        top_algo = zpool.getTopProfit()     # if getTopProfit returns False, wait 10 minutes and retry
    logger.info(top_algo)
    if current_algo:
        process.kill()                      # kill current miner, it doesn't hurt
        logger.info('Killing current miner')
        time.sleep(10)
    current_algo = top_algo

    # start new mining process
    stratum = 'stratum+tcp://' + top_algo['algo'] + pool_url_base + ':' + top_algo['port']
    mining_cmd = [top_algo['miner'], '-a', top_algo['algo'], '-o', stratum, '-u',
                                machine['wallet'], '-p', machine['name'], 'c=BTC']
    logger.info(' '.join([str(item) for item in mining_cmd]))
    process = subprocess.Popen([top_algo['miner'], '-a', top_algo['algo'], '-o', stratum, '-u',
                                machine['wallet'], '-p', machine['name'], 'c=BTC'])

    # time.sleep(60)
    time.sleep(machine['interval']*60)

