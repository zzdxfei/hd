"""
import easyquotation
quotation = easyquotation.use('sina')
quotation.market_snapshot(prefix=True)
print(quotation.real('603160'))

{'603160': {
 'name': '汇顶科技',
 'open': 331.96,
 'close': 333.27,
 'now': 346.86,
 'high': 361.52,
 'low': 326.59,
 'buy': 346.5,
 'sell': 346.75,
 'turnover': 5919247,
 'volume': 2023648150.0,
 'bid1_volume': 100,
 'bid1': 346.5,
 'bid2_volume': 400,
 'bid2': 346.01,
 'bid3_volume': 3700,
 'bid3': 346.0,
 'bid4_volume': 100,
 'bid4': 345.8,
 'bid5_volume': 100,
 'bid5': 345.75,
 'ask1_volume': 100,
 'ask1': 346.75,
 'ask2_volume': 300,
 'ask2': 346.76,
 'ask3_volume': 700,
 'ask3': 346.86,
 'ask4_volume': 200,
 'ask4': 347.0,
 'ask5_volume': 1200,
 'ask5': 347.2,
 'date': '2020-02-19',
 'time': '14:16:06'}}
"""

import pynvim
import time
import numpy as np
import easyquotation


def ComputeRatio(v):
    MAX_VALUE = 999999999999999.0
    base_thresh = [0, 36, 144, 300, 420, 660, 960, MAX_VALUE]
    base_ratio =  [3,  10,  20,  25,  30,  35,  45]
    value = v / 1000.0
    ratio = 0.0
    bins = []
    for i in range(1, len(base_thresh)):
        dist = base_thresh[i] - base_thresh[i - 1]
        if value <= dist:
            bins.append(value)
            break
        bins.append(dist)
        value -= dist
    for i in range(len(bins)):
        ratio += bins[i] * base_ratio[i] * 0.01
    return ratio * 1000

def GetMoney(p):
    W = 10000.0
    fww = (1.9 * 6 + 2.2 * 12 - 6 - 2.4 - 0.25 * 12) * W
    total = ((96 + p) / 2.0 - 48) * 17000 * 0.24 + fww
    base_ratio  = ComputeRatio(fww)
    gupiao = ComputeRatio(total) - base_ratio
    owner = (p - 48) * 17000 * 0.24
    return (owner, gupiao, owner - gupiao)


def GetGupiaoLists(info):
    change = (info['now'] - info['close'])
    ratio =  change / info['close']
    lines = [
        "{:^9}: {}".format('公司名称', info['name']),
        "{:^10}: {:.2f}".format(' 开盘价 ', info['close']),
        "{:^10}: {:.2f}".format(' 当前价 ', info['now']),
        "{:^11}: {:.2%} {:6.2f}".format('  涨幅  ', ratio, change)]
    return lines


def GetGupiaoOwns(owns):
    lines = [
            "{:^10}: {:.2f}".format(' 总收益 ', owns[0]),
            "{:^11}: {:.2f}".format('  交税  ', owns[1]),
            "{:^11}: {:.2f}".format('  净得  ', owns[2])
        ]
    return lines


@pynvim.plugin
class Huiding(object):
    def __init__(self, vim):
        self.vim = vim
        self.quotation = easyquotation.use('sina')
        self.quotation.market_snapshot(prefix=True)

    @pynvim.command('Huiding', range='', nargs='0', sync=False)
    def command_handler(self, args, range):
        self.vim.command('hi Type ctermfg=green')
        self.vim.command('hi Number ctermfg=red')
        self.vim.command('hi Boolean ctermfg=blue')
        buf_number = self.vim.current.buffer.number
        while(True):
            info = self.quotation.real('603160')['603160']
            lines = GetGupiaoLists(info)
            owns = GetMoney(info['now'])
            lines.extend(GetGupiaoOwns(owns))
            self.vim.buffers[buf_number][:] = lines

            hi_type = "Number" if info['now'] > info['close'] else "Type"
            
            hi_lists = [[hi_type, int(i), 13, -1] for i in np.arange(len(lines))]
            hi_lists[0][0] = 'Boolean'
            hi_lists.extend([['Boolean', int(i), 0, 13] for i in np.arange(len(lines))])
            src_id = self.vim.new_highlight_source()
            self.vim.buffers[buf_number].update_highlights(
                src_id, hi_lists, clear=True, async_=False)
            time.sleep(1)
