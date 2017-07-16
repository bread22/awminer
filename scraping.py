import json
import re
import logging
from selenium import webdriver


__author__ = 'wuqingyi22@gmail.com'

logger = logging.getLogger('runtime.log')


class MiningPool(object):
    def __init__(self, url, config):
        self.url = url
        self.config = config        # pool configuration file name in json format

    def getTopProfit(self):
        with open(self.config) as fn:
            profit_dict = json.load(fn)

        for key in profit_dict:
            profit_dict[key]['actual_profit'] = 0   # initialize these 2
            profit_dict[key]['miner_qty'] = 0
            if profit_dict[key]['hashrate'] == 0 or not profit_dict[key]['miner']:
                continue                            # skip algo not in use to save some time
            algo = profit_dict[key]['algo']
            url1 = 'http://zpool.ca/site/gomining?algo=' + algo
            url2 = 'http://zpool.ca/site/graph_price_results'
            url3 = 'http://zpool.ca/site/mining_results'
            wd = webdriver.PhantomJS()
            try:
                wd.get(url1)                            # select algo
            except:
                return False
            try:
                wd.get(url2)                            # get actual profict in last 24 hours
                profit_24hr = [float(item) for item in re.findall(r'",(.+?)]', wd.page_source)]
                profit_dict[key]['normalized_profit'] = sum(profit_24hr[-10:]) / 10
                profit_dict[key]['actual_profit'] = profit_dict[key]['normalized_profit'] \
                    * profit_dict[key]['hashrate']
            except:
                return False
            try:
                wd.get(url3)                            # get pool status and miner quantity
                miner_str = wd.find_element_by_class_name('main-left-title').text
                miner_qty = int(re.search(r', (\d+?) miners', miner_str).groups()[0])
            except:
                return False

            profit_dict[key]['miner_qty'] = miner_qty
            logmsg = 'algo: ' + profit_dict[key]['algo'] + ',\t norm: ' + str(profit_dict[key]['normalized_profit']) \
                + ',\t profit: ' + str(profit_dict[key]['actual_profit'])
            logger.info(logmsg)
            # print profit_dict[key]['algo'], profit_dict[key]['actual_profit'], \
            #     profit_dict[key]['normalized_profit']

        top_algo = {'profit': 0}
        for key in profit_dict:
            if profit_dict[key]['actual_profit'] > top_algo['profit'] and profit_dict[key]['miner_qty'] > 10:
                top_algo['port'] = key
                top_algo['algo'] = profit_dict[key]['algo']
                top_algo['profit'] = profit_dict[key]['actual_profit']
                top_algo['miner'] = profit_dict[key]['miner']
                top_algo['miner_qty'] = profit_dict[key]['miner_qty']

        return top_algo
