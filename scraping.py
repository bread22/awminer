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


def parseZpool(texts):
    profit_dict = {}
    fee_pos = 0
    with open('algos_zpool.json') as fn:
        pool_dict = json.load(fn)

    profit_dict = pool_dict

    for i in range(len(texts)):
        if texts[i] in pool_dict:
            for j in range(1, 5):
                if "%" in texts[i+j]:
                    fee_pos = j                 # fee postion, +3 is profit, -2 is miners
                    break
            profit_dict[texts[i]]['normalized_profit'] = float(texts[i+fee_pos+3])
            profit_dict[texts[i]]['miner_qty'] = texts[i+fee_pos-2]
            profit_dict[texts[i]]['actual_profit'] = profit_dict[texts[i]]['normalized_profit'] \
                * pool_dict[texts[i]]['hashrate']

    # with open('profits_zpool.json', 'w') as fn:
    #     json.dump(pool_dict, fn)

    return profit_dict


url = 'http://zpool.ca/'
# This does the magic.Loads everything
r = Render(url)
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
# for item in data:
#     print item.text_content()
#     pass

txt = [item.text_content() for item in data]
text = str(''.join(str(txt)))
with open('zpool_output.txt', 'w') as fn:
    fn.write(text)

parseZpool(txt)