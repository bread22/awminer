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

current_algo = {}

while True:
    logger.info('Start scraping')
    mph.updateProfit()
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
        time.sleep(5)
    if zpool_top['profit'] >= mph_top['profit']:
        current_algo = zpool_top
    else:
        current_algo = mph_top

    mph.resetProfit()
    # start new mining process
    mining_cmd = [current_algo['miner'], '-a', current_algo['algo'], '-o',
                  current_algo['stratum'], '-u', current_algo['user'],
                  '-p', current_algo['password']]
    logger.info(' '.join([str(item) for item in mining_cmd]))
    process = subprocess.Popen([current_algo['miner'], '-a', current_algo['algo'], '-o', current_algo['stratum'],
                                '-u', current_algo['user'], '-p', current_algo['password']])

    timer = 0
    while timer < mph.top_algo['switch_interval'] / mph.top_algo['fetch_interval']:
        timer += 1
        if process.poll() == 0:             # if mining process dies, break wait loop and start next one
            break
        mph.updateProfit()                  # poll MPH to update current algo profits
        time.sleep(mph.top_algo['fetch_interval']*60)


