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

zpool = scraping.Zpool('rig_zpool.json', 'algos_zpool.json')
mph = scraping.MiningPoolHub('rig_mph.json', 'algos_zpool.json')
mph.updateProfit()

with open(zpool.config) as fn:
    machine = json.load(fn)

current_algo = {}

while True:
    logger.info('Start scraping')
    zpool_top = zpool.getTopProfit()         # get top algo
    mph_top = mph.getTopAlgo()
    while not zpool_top and not mph_top:
        logger.warning('Scraping failed, wait 10 minutes and retry')
        time.sleep(600)
        zpool_top = zpool.getTopProfit()     # if getTopProfit returns False, wait 10 minutes and retry
        mph_top = mph.getTopAlgo()
    logger.info(zpool_top)
    logger.info(mph_top)

    if current_algo:
        process.kill()                      # kill current miner, it doesn't hurt
        logger.info('Killing current miner')
        time.sleep(10)
    if zpool_top['profit'] >= mph_top['profit']:
        current_algo = zpool_top
        current_algo['url_base'] = zpool.pool_url_base
    else:
        current_algo = mph_top
        current_algo['url_base'] = mph.pool_url_base

    # start new mining process
    stratum = 'stratum+tcp://' + top_algo['algo'] + pool_url_base + ':' + top_algo['port']
    mining_cmd = [top_algo['miner'], '-a', top_algo['algo'], '-o', stratum, '-u',
                                machine['wallet'], '-p', machine['name'], 'c=BTC']
    logger.info(' '.join([str(item) for item in mining_cmd]))
    process = subprocess.Popen([top_algo['miner'], '-a', top_algo['algo'], '-o', stratum, '-u',
                                machine['wallet'], '-p', machine['name'], 'c=BTC'])

    timer = 0
    while timer < machine['switch_interval'] / 5:
        timer += 1
        if process.poll() == 0:             # if mining process dies, break wait loop and start next one
            break
        mph.updateProfit()                  # poll MPH to update current algo profits
        time.sleep(300)


