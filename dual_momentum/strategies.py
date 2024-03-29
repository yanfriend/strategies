import backtrader as bt


class PrintClose(bt.Strategy):

	def __init__(self):
		#Keep a reference to the "close" line in the data[0] dataseries
		self.dataclose = self.datas[0].close

	# def log(self, txt, dt=None):
	# 	# import ipdb; ipdb.set_trace()
	#
	# 	dt = dt or self.datas[0].datetime.date(0)
	# 	print(f'{dt.isoformat()} {txt}') #Print date and close

	def next(self):
		# import ipdb; ipdb.set_trace()
		print(self.datas[0]._name, self.datas[0].close[0])  # Print close prices
		print(self.datas[1]._name, self.datas[0].close[0])

		# self.log('Close: ', self.dataclose[0])
		# print('haha')


class DualMomentum(bt.Strategy):
	RISK_FREE_RATE = 0.015  # 10 yr bond rate 1.5%

	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

	def __init__(self):
		self.dataclose = self.datas[0].close
		
		# Order variable will contain ongoing order details/status
		self.order = None

		# Instantiate moving averages
		self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pfast)
		self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pslow)
		
		''' Using the built-in crossover indicator
		self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)'''


	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# An active Buy/Sell order has been submitted/accepted - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
			elif order.issell():
				self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		# Reset orders
		self.order = None

	def next(self):
		''' Logic for using the built-in crossover indicator
		
		if self.crossover > 0: # Fast ma crosses above slow ma
			pass # Signal for buy order
		elif self.crossover < 0: # Fast ma crosses below slow ma
			pass # Signal for sell order
		'''
		# if not  # have 30 day data

		# Check for open orders
		if self.order:
			return

		# Check if we are in the market
		if not self.position:
			# We are not in the market, look for a signal to OPEN trades
				
			#If the 20 SMA is above the 50 SMA
			if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
				self.log(f'BUY CREATE {self.dataclose[0]:2f}')
				# Keep track of the created order to avoid a 2nd order
				self.order = self.buy()
			#Otherwise if the 20 SMA is below the 50 SMA   
			elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
				self.log(f'SELL CREATE {self.dataclose[0]:2f}')
				# Keep track of the created order to avoid a 2nd order
				self.order = self.sell()
		else:
			# We are already in the market, look for a signal to CLOSE trades
			if len(self) >= (self.bar_executed + 5):
				self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
				self.order = self.close()
