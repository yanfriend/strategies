# refer http://www.360doc.com/content/21/0706/12/76108447_985350099.shtml

import datetime
import backtrader as bt


# 创建策略
class DualMomentum(bt.Strategy):
    params = dict(  # just bt's trick
        poneplot=False,  # 是否打印到同一张图
        look_back_days=90,
    )
    FREE_RATE = 0.02  # 2%

    def __init__(self):
        self.inds = dict()

    def next(self):
        if len(self.datas[0]) % 30 != 0:  # check every 30 days
            return

        rate_list = []
        for i, data in enumerate(self.datas):
            dt, dn = self.datetime.date(), data._name

            # 90 day price change %
            if len(data) < self.p.look_back_days:
                continue

            p0 = data.close[0]
            pn = data.close[-self.p.look_back_days]
            rate = (p0 - pn) / pn
            rate_list.append([data._name, rate])

        sorted_rate = sorted(rate_list, key=lambda x: x[1], reverse=True)
        long_list = [i[0] for i in sorted_rate[:2]]  # choose top 2.

        if len(sorted_rate) < 2:
            return
        if sorted_rate[1][1] < self.FREE_RATE:
            # sell everything
            for data in self.datas:
                pos = self.getposition(data).size
                if pos != 0:
                    self.close(data=data)
            return

        total_value = self.broker.getvalue()
        p_value = total_value / 2
        for data in self.datas:
            pos = self.getposition(data).size
            if not pos and data._name in long_list:
                size = int(p_value / 100 / data.close[0]) * 100
                self.buy(data=data, size=size)

            if pos != 0 and data._name not in long_list:
                self.close(data=data)


cerebro = bt.Cerebro()  # 创建cerebro

stk_codes = ['VO', 'VB', 'VTI', 'SPY', 'QQQ']
stk_num = len(stk_codes)
for i in range(stk_num):
    datapath = '../data/' + stk_codes[i] + '.csv'
    # 创建数据
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2004, 1, 30),
        todate=datetime.datetime(2014, 1, 1),
    )

    cerebro.adddata(data, name=stk_codes[i])

cerebro.broker.setcash(100_000.0)

# 设置交易单位大小
# cerebro.addsizer(bt.sizers.FixedSize, stake = 5000)
# 设置佣金为千分之一
# cerebro.broker.setcommission(commission=0.001)

cerebro.addstrategy(DualMomentum, poneplot=False)
cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot(style="candlestick")  # 绘图
