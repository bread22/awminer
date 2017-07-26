import json
import re
import logging
from selenium import webdriver
from lxml import html
import requests


__author__ = 'wuqingyi22@gmail.com'

logger = logging.getLogger('runtime.log')


class MiningPool(object):
    def __init__(self, rig_config, algo_config):
        self.config = rig_config                # rig configuration file name in json format
        self.algo_config = algo_config          # pool algo configuration (hashrate) file name in json format
        # load rig config and contruct self.top_algo
        with open(self.config) as fn:
            rig_conf = json.load(fn)
        self.top_algo = {
        'profit': 0.0,
        'user': rig_conf['username'],
        'password': rig_conf['password'],
        'url_base': rig_conf['pool_url_base'],
        'switch_interval': rig_conf['switch_interval']
        }


class Zpool(MiningPool):

    def getTopProfit(self):
        with open(self.algo_config) as fn:
            profit_dict = json.load(fn)

        for key in profit_dict:
            algo = profit_dict[key]['algo']
            url1 = 'http://zpool.ca/site/gomining?algo=' + algo
            url2 = 'http://zpool.ca/site/graph_price_results'
            url3 = 'http://zpool.ca/site/mining_results'
            profit_dict[key]['actual_p'] = 0   # initialize these 2
            profit_dict[key]['miner_qty'] = 0
            if profit_dict[key]['hashrate'] == 0 or not profit_dict[key]['miner']:
                continue                            # skip algo not in use to save some time
            wd = webdriver.PhantomJS()
            try:
                wd.get(url1)                            # select algo
                wd.get(url2)                            # get normalized profit in last 24 hours
                profit_24hr = [float(item) for item in re.findall(r'",(.+?)]', wd.page_source)]
                profit_dict[key]['norm_p'] = sum(profit_24hr[-10:]) / 10
                # calculate actual profit
                profit_dict[key]['actual_p'] = profit_dict[key]['norm_p'] \
                    * profit_dict[key]['hashrate']
                wd.get(url3)                            # get pool status and miner quantity
                miner_str = wd.find_element_by_class_name('main-left-title').text
                miner_qty = int(re.search(r', (\d+?) miner', miner_str).groups()[0])
                wd.close()
            except:
                wd.close()
                # if there is any error during scraping, return False, preventing miner from stopping
                return False

            profit_dict[key]['miner_qty'] = miner_qty
            logmsg = 'ZPOOL: algo: ' + profit_dict[key]['algo'] + ',\t norm: ' + str(profit_dict[key]['norm_p']) \
                + ',\t profit: ' + str(profit_dict[key]['actual_p'])
            logger.info(logmsg)
            # print profit_dict[key]['algo'], profit_dict[key]['actual_p'], \
            #     profit_dict[key]['norm_p']

        self.top_algo['profit'] = 0                 # reset top profit
        for key in profit_dict:
            if profit_dict[key]['actual_p'] > self.top_algo['profit'] and profit_dict[key]['miner_qty'] > 10:
                self.top_algo['port'] = key
                self.top_algo['algo'] = profit_dict[key]['algo']
                self.top_algo['profit'] = profit_dict[key]['actual_p']
                self.top_algo['miner'] = profit_dict[key]['miner']
                self.top_algo['miner_qty'] = profit_dict[key]['miner_qty']
                self.top_algo['stratum'] = 'stratum+tcp://' + self.top_algo['algo'] + \
                                           self.top_algo['url_base'] + ':' + self.top_algo['port']

        return self.top_algo


class MiningPoolHub(MiningPool):
    def __init__(self, rig_config, algo_config):
        MiningPool.__init__(self, rig_config, algo_config)
        with open(self.config) as fn:
            rig_conf = json.load(fn)
        self.top_algo['fetch_interval'] = rig_conf['fetch_interval']
        with open(self.algo_config) as fn:
            self.hash_dict = json.load(fn)
        # convert profit_dict to use algo as key, easier to use in updateProfit
        self.profit_dict = {}

    def updateProfit(self):
        url = 'http://miningpoolhub.com/?page=home&normalize=none'
        try:
            page = requests.get(url)
        except:
            return
        tree = html.fromstring(page.content)
        # get hash data from 2nd <tbody>, which are no-switch ports
        xpath = '(//tbody)[position()=2]/tr/td/span/text()|(//tbody)[position()=2]/tr/td/text()'
        raw_hash = tree.xpath(xpath)
        # convert raw_hash to str list, and convert them to lower to match profit_dict
        raw_hash = map(str, raw_hash)
        raw_hash = [item.lower() for item in raw_hash]
        i = 0
        while i < len(raw_hash):
            # length 5 str starts with '20', it is a port number
            if len(raw_hash[i]) == 5 and raw_hash[i].startswith('20'):
                if raw_hash[i] in self.profit_dict:
                    # update profit data
                    profit = raw_hash[i+1]
                    if profit == '-':
                        profit = 0.0
                    else:
                        profit = float(profit.replace(',', ''))
                    self.profit_dict[raw_hash[i]]['norm_p'].append(profit)
                    self.profit_dict[raw_hash[i]]['actual_p'] = self.profit_dict[raw_hash[i]]['hashrate'] * \
                        sum(self.profit_dict[raw_hash[i]]['norm_p']) / len(self.profit_dict[raw_hash[i]]['norm_p'])
                    # logmsg = 'MPH: algo: ' + self.profit_dict[raw_hash[i]]['algo'] + ',\t norm: ' + \
                    #          str(self.profit_dict[raw_hash[i]]['norm_p']) + ',\t profit: ' + \
                    #          str(self.profit_dict[raw_hash[i]]['actual_p'])
                    # logger.info(logmsg)
                else:
                    # create new item in self.profit_dict
                    algo = raw_hash[i-1]
                    if algo == 'myriad-groestl':
                        algo = 'myr-gr'
                    if algo == 'lyra2re2':
                        algo = 'lyra2v2'
                    self.profit_dict[raw_hash[i]] = {}
                    self.profit_dict[raw_hash[i]]['algo'] = algo
                    self.profit_dict[raw_hash[i]]['miner'] = self.findMiner(algo)
                    self.profit_dict[raw_hash[i]]['norm_p'] = []
                    self.profit_dict[raw_hash[i]]['actual_p'] = 0.0
                    self.profit_dict[raw_hash[i]]['hashrate'] = self.findHashrate(algo)   
                    logger.info(self.profit_dict[raw_hash[i]])
            i += 1
        page.close()

    def findHashrate(self, algo):
        for key in self.hash_dict:
            if self.hash_dict[key]['algo'] == algo:
                if algo == 'equihash':
                    return float(self.hash_dict[key]['hashrate']) / 10**3
                elif algo == 'blake2s' or algo == 'blakecoin':
                    return float(self.hash_dict[key]['hashrate']) * 10**3
                else:
                    return float(self.hash_dict[key]['hashrate'])
        return 0.0        # if algo is not found, return 0

    def findMiner(self, algo):
        for key in self.hash_dict:
            if self.hash_dict[key]['algo'] == algo:
                return self.hash_dict[key]['miner']
        return None        # if algo is not found, return None

    def resetProfit(self):
        for key in self.profit_dict:
            self.profit_dict[key]['norm_p'] = []
            self.profit_dict[key]['actual_p'] = 0.0

    def getTopAlgo(self):
        self.top_algo['profit'] = 0                 # reset top profit
        for key in self.profit_dict:
            if self.profit_dict[key]['actual_p'] > self.top_algo['profit']:
                self.top_algo['port'] = key
                self.top_algo['algo'] = self.profit_dict[key]['algo']
                self.top_algo['profit'] = self.profit_dict[key]['actual_p']
                self.top_algo['miner'] = self.profit_dict[key]['miner']
                self.top_algo['stratum'] = 'stratum+tcp://' + self.top_algo['url_base'] + \
                                           ':' + self.top_algo['port']
        logger.info(self.profit_dict[self.top_algo['port']])
        return self.top_algo
