# refer http://www.360doc.com/content/21/0706/12/76108447_985350099.shtml
import datetime  # 用于datetime对象操作
import backtrader as bt # 引入backtrader框架

# 创建策略
class SmaCross(bt.Strategy):
    params = dict(
        pfast=5,  # 短期均线周期
        pslow=60,   # 长期均线周期
        poneplot = False,  # 是否打印到同一张图
        pstake = 1000 # 单笔交易股票数目
    )
    def __init__(self):
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['sma1'] = bt.ind.SMA(d.close, period=self.p.pfast)  # 短期均线
            self.inds[d]['sma2'] = bt.ind.SMA(d.close, period=self.p.pslow)  # 长期均线
            self.inds[d]['cross'] = bt.ind.CrossOver(self.inds[d]['sma1'], self.inds[d]['sma2'], plot = False)  # 交叉信号
            # 跳过第一只股票data，第一只股票data作为主图数据
            # if i > 0:
            #     if self.p.poneplot:
            #         d.plotinfo.plotmaster = self.datas[0]

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            if not pos:
                if self.inds[d]['cross'] > 0:
                    self.buy(data = d, size = self.p.pstake)
            elif self.inds[d]['cross'] < 0:
                self.close(data = d)
cerebro = bt.Cerebro()  # 创建cerebro

stk_codes = ['VO', 'GLD']
stk_num = len(stk_codes)
for i in range(stk_num):
    datapath = '../data/' + stk_codes[i] + '.csv'
    # 创建数据
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2006, 1, 1),
        todate=datetime.datetime(2017, 12, 25),
    )

    # data = bt.feeds.GenericCSVData(
    #         dataname = datapath,
    #         fromdate = datetime.datetime(2018, 1, 1),
    #         todate = datetime.datetime(2020, 3, 31),
    #         nullvalue = 0.0,
    #         dtformat = ('%Y-%m-%d'),
    #         datetime = 0,
    #         open = 1,
    #         high = 2,
    #         low = 3,
    #         close = 4,
    #         volume = 5,
    #         openinterest = -1
    #         )
    # 在Cerebro中添加股票数据
    cerebro.adddata(data, name = stk_codes[i])
# 设置启动资金
cerebro.broker.setcash(100_000.0)
# 设置交易单位大小
#cerebro.addsizer(bt.sizers.FixedSize, stake = 5000)
# 设置佣金为千分之一
# cerebro.broker.setcommission(commission=0.001)
cerebro.addstrategy(SmaCross, poneplot = False)  # 添加策略
cerebro.run()  # 遍历所有数据
# 打印最后结果
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot(style = "candlestick")  # 绘图

