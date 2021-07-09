# refer http://www.360doc.com/content/21/0706/12/76108447_985350099.shtml

import datetime
import backtrader as bt


# 创建策略
class DualMomentum(bt.Strategy):
    params = dict(  # just bt's trick
        poneplot=False,  # 是否打印到同一张图
        look_back_days=90,
        printlog=True,
    )
    FREE_RATE = 0.02  # 2%

    def __init__(self):
        self.inds = dict()

    def next(self):
        if len(self.datas[0]) % 22 != 0:  # check every 30 days
            return
        if len(self.datas[0]) < self.p.look_back_days:
            return

        p0 = self.datas[5].close[0]  # spy, today close
        pn = self.datas[5].close[-self.p.look_back_days]
        rate = (p0 - pn) / pn
        if rate < self.FREE_RATE:  # poor spy, no trade, close positions and return
            for data in self.datas:
                pos = self.getposition(data).size
                if pos != 0:
                    self.close(data=data)
            return

        rate_list = []
        for i, data in enumerate(self.datas[:5]):  # 5 is spy, 6 is tlt
            # print(f"name :{data._name}, date: {self.datetime.date()}, price:{data.close[0]}") # values inside

            p0 = data.close[0]
            pn = data.close[-self.p.look_back_days]
            rate = (p0 - pn) / pn
            rate_list.append([data._name, rate])

        sorted_rate = sorted(rate_list, key=lambda x: x[1], reverse=True)

        stock_amount = 2
        long_list = [i[0] for i in sorted_rate[:stock_amount]]  # choose top 2.

        # if len(sorted_rate) < stock_amount:
        #     return

        total_value = self.broker.getvalue()
        p_value = total_value / stock_amount
        for data in self.datas:
            pos = self.getposition(data).size
            if not pos and data._name in long_list:
                size = int(p_value // 100 / data.close[0]) * 100
                self.buy(data=data, size=size)

            if pos != 0 and data._name not in long_list:
                self.close(data=data)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'buy {order.data._name}:\nprice:{order.executed.price:.2f},\
                cost:{order.executed.value:.2f}')
                # 手续费:{order.executed.comm:.2f}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'sell {order.data._name}:\nprice：{order.executed.price:.2f},\
                cost: {order.executed.value:.2f}')

            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'order failure: {order.Status[order.status]}')

        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'profit: {trade.pnl:.2f} for {trade.data._name}')


cerebro = bt.Cerebro()  # 创建cerebro

stk_codes = ['VO', 'VB', 'VTI', 'QQQ', 'GLD', 'SPY', 'TLT']
stk_num = len(stk_codes)
for i in range(stk_num):
    datapath = '../data/' + stk_codes[i] + '.csv'
    # 创建数据
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2005, 3, 1),
        todate=datetime.datetime(2010, 12, 31),
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
