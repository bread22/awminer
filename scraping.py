import json
import re
from selenium import webdriver


__author__ = 'wuqingyi22@gmail.com'


class MiningPool(object):
    def __init__(self, url, config):
        self.url = url
        self.config = config        # pool configuration file name in json format

    def getTopProfit(self):
        with open(self.config) as fn:
            profit_dict = json.load(fn)

        for key in profit_dict:
            algo = profit_dict[key]['algo']
            url1 = 'http://zpool.ca/site/gomining?algo=' + algo
            url2 = 'http://zpool.ca/site/graph_price_results'
            url3 = 'http://zpool.ca/site/mining_results'
            wd = webdriver.PhantomJS()
            wd.get(url1)                            # select algo
            wd.get(url2)                            # get actual profict in last 24 hours
            profit_24hr = [float(item) for item in re.findall(r'",(.+?)]', wd.page_source)]
            profit_dict[key]['normalized_profit'] = sum(profit_24hr[-10:]) / 10
            profit_dict[key]['actual_profit'] = profit_dict[key]['normalized_profit'] \
                * profit_dict[key]['hashrate']
            wd.get(url3)                            # get pool status and miner quantity
            miner_str = wd.find_element_by_class_name('main-left-title').text
            miner_qty = int(re.search(r', (\d+?) miners', miner_str).groups()[0])
            profit_dict[key]['miner_qty'] = miner_qty
            print profit_dict[key]['algo'], profit_dict[key]['actual_profit'], \
                profit_dict[key]['normalized_profit']

        top_port = ''
        top_algo = ''
        top_miner = ''
        top_profit = 0
        for key in profit_dict:
            if profit_dict[key]['actual_profit'] > top_profit and profit_dict[key]['miner_qty'] > 10:
                top_port = key
                top_algo = profit_dict[key]['algo']
                top_profit = profit_dict[key]['actual_profit']
                top_miner = profit_dict[key]['miner']

        print "Algo: ", top_algo
        print "Port: ", top_port
        print "Profit: ", top_profit

        return {'algo': top_algo, 'port': top_port, 'profit': top_profit, 'miner': top_miner}
