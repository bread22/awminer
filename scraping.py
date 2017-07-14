import sys, json
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import html

__author__ = 'wuqingyi22@gmail.com'


class Render(QWebPage):
  def __init__(self, url):
    self.app = QApplication(sys.argv)
    QWebPage.__init__(self)
    self.loadFinished.connect(self._loadFinished)
    self.mainFrame().load(QUrl(url))
    self.app.exec_()

  def _loadFinished(self, result):
    self.frame = self.mainFrame()
    self.app.quit()


class MiningPool(object):
    def __init__(self, url, config):
        self.url = url
        self.config = config        # pool configuration file name in json format
        self.profit_dict = {}

    def parseZpool(self, page_txts):
        fee_pos = 0
        with open(self.config) as fn:
            pool_dict = json.load(fn)

        profit_dict = pool_dict

        for i in range(len(page_txts)):
            if page_txts[i] in pool_dict:
                for j in range(1, 5):
                    if "%" in page_txts[i+j]:
                        fee_pos = j                 # use fee as anchor position, +3 is profit, -2 is miners
                        break
                profit_dict[page_txts[i]]['normalized_profit'] = float(page_txts[i+fee_pos+3])
                profit_dict[page_txts[i]]['miner_qty'] = int(page_txts[i+fee_pos-2])
                profit_dict[page_txts[i]]['actual_profit'] = profit_dict[page_txts[i]]['normalized_profit'] \
                    * pool_dict[page_txts[i]]['hashrate']

        with open('profits_zpool.json', 'w') as fn:
            json.dump(profit_dict, fn)

        return profit_dict

    def getTopProfit(self):
        # This does the magic.Loads everything
        r = Render(self.url)
        # result is a QString.
        result = r.frame.toHtml()

        # QString should be converted to string before processed by lxml
        formatted_result = str(result.toAscii())

        # with open('zpool_output.html', 'w') as fn:
        #     fn.write(formatted_result)
        # print formatted_result

        # Next build lxml tree from formatted_result
        tree = html.fromstring(formatted_result)

        # Now using correct Xpath we are fetching URL of archives
        data = tree.xpath('///tbody/tr/td[text()]')

        txt = [item.text_content() for item in data]
        # text = str(''.join(str(txt)))
        # with open('zpool_output.txt', 'w') as fn:
        #     fn.write(text)

        profit_dict = self.parseZpool(txt)

        print profit_dict

        top_port = ''
        top_algo = ''
        top_profit = 0
        for key in profit_dict:
            print profit_dict[key]['algo'], profit_dict[key]['actual_profit']
            if profit_dict[key]['actual_profit'] > top_profit and profit_dict[key]['miner_qty'] > 10:
                top_port = key
                top_algo = profit_dict[key]['algo']
                top_profit = profit_dict[key]['actual_profit']

        print "Algo: ", top_algo
        print "Port: ", top_port
        print "Profit: ", top_profit

        return profit_dict
