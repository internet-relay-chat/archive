#!/usr/bin/env python
# IExTrading IRC Bot - Developed by acidvegas in Python (https://acid.vegas/iex)

import http.client
import json
import random
import ssl
import socket
import time

# Connection
server  = 'irc.supernets.org'
channel = '#dev'

# Identity
nickname = 'StockMarket'
username = 'iex'
realname = 'acid.vegas/iex'

# Login
nickserv_password = None
network_password  = None

# Settings
throttle_cmd = 3
throttle_msg = 0.5
user_modes   = None

# Formatting Control Characters / Color Codes
bold        = '\x02'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

def condense_value(value):
	value = float(value)
	if value < 0.01:
		return '${0:,.8f}'.format(value)
	elif value < 24.99:
		return '${0:,.2f}'.format(value)
	else:
		return '${:,}'.format(int(value))

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
	if reason:
		print(f'{get_time()} | [!] - {msg} ({reason})')
	else:
		print(f'{get_time()} | [!] - {msg}')

def error_exit(msg):
	raise SystemExit(f'{get_time()} | [!] - {msg}')

def get_float(data):
	try:
		float(data)
		return True
	except ValueError:
		return False

def get_time():
	return time.strftime('%I:%M:%S')

def percent_color(percent):
	percent = float(percent)
	if percent == 0.0:
		return grey
	elif percent < 0.0:
		if percent > -10.0:
			return brown
		else:
			return red
	else:
		if percent < 10.0:
			return green
		else:
			return light_green

def random_int(min, max):
	return random.randint(min, max)

class IEX:
	def api(api_data):
		conn = http.client.HTTPSConnection('api.iextrading.com', timeout=15)
		conn.request('GET', '/1.0/' + api_data)
		response = conn.getresponse().read().decode('utf-8')
		data = json.loads(response)
		conn.close()
		return data

	def company(symbol):
		return IEX.api(f'stock/{symbol}/company')

	def lists(list_type):
		return IEX.api('stock/market/list/' + list_type)

	def news(symbol):
		return IEX.api(f'stock/{symbol}/news')

	def quote(symbols):
		data = IEX.api(f'stock/market/batch?symbols={symbols}&types=quote')
		if len(data) == 1:
			return data[next(iter(data))]['quote']
		else:
			return [data[item]['quote'] for item in data]

	def stats(symbol):
		return IEX.api(f'stock/{symbol}/stats')

	def symbols():
		return IEX.api('ref-data/symbols')

class IRC(object):
	def __init__(self):
		self.last = 0
		self.slow = False
		self.sock = None

	def stock_info(self, data):
		sep      = self.color('|', grey)
		sep2     = self.color('/', grey)
		name     = '{0} ({1})'.format(self.color(data['companyName'], white), data['symbol'])
		value    = condense_value(data['latestPrice'])
		percent  = self.color('{:,.2f}%'.format(float(data['change'])), percent_color(data['change']))
		volume   = '{0} {1}'.format(self.color('Volume:', white), '${:,}'.format(data['avgTotalVolume']))
		cap      = '{0} {1}'.format(self.color('Market Cap:', white), '${:,}'.format(data['marketCap']))
		return f'{name} {sep} {value} ({percent}) {sep} {volume} {sep} {cap}'

	def stock_matrix(self, data): # very retarded way of calculating the longest strings per-column
		results = {'symbol':list(),'value':list(),'percent':list(),'volume':list(),'cap':list()}
		for item in data:
			results['symbol'].append(item['symbol'])
			results['value'].append(condense_value(item['latestPrice']))
			results['percent'].append('{:,.2f}%'.format(float(item['change'])))
			results['volume'].append('${:,}'.format(item['avgTotalVolume']))
			results['cap'].append('${:,}'.format(item['marketCap']))
		for item in results:
			results[item] = len(max(results[item], key=len))
		if results['symbol'] < len('Symbol'):
			results['symbol'] = len('Symbol')
		if results['value'] < len('Value'):
			results['value'] = len('Value')
		if results['percent'] < len('Change'):
			results['percent'] = len('Change')
		if results['volume'] < len('Volume'):
			results['volume'] = len('Volume')
		if results['cap'] < len('Market Cap'):
			results['cap'] = len('Market Cap')
		return results

	def stock_table(self, data):
		matrix = self.stock_matrix(data)
		header = self.color(' {0}   {1}   {2}   {3}   {4}'.format('Symbol'.center(matrix['symbol']), 'Value'.center(matrix['value']), 'Percent'.center(matrix['percent']),  'Volume'.center(matrix['volume']), 'Market Cap'.center(matrix['cap'])), black, light_grey)
		lines  = [header,]
		for item in data:
			symbol   = item['symbol'].ljust(matrix['symbol'])
			value    = condense_value(item['latestPrice']).rjust(matrix['value'])
			percent  = self.color('{:,.2f}%'.format(float(item['change'])).rjust(matrix['percent']), percent_color(item['change']))
			volume   = '${:,}'.format(item['avgTotalVolume']).rjust(matrix['volume'])
			cap      = '${:,}'.format(item['marketCap']).rjust(matrix['cap'])
			lines.append(' {0} | {1} | {2} | {3} | {4} '.format(symbol,value,percent,volume,cap))
		return lines

	def color(self, msg, foreground, background=None):
		if background:
			return f'\x03{foreground},{background}{msg}{reset}'
		else:
			return f'\x03{foreground}{msg}{reset}'

	def connect(self):
		try:
			self.sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
			self.sock.connect((server, 6697))
			self.raw(f'USER {username} 0 * :{realname}')
			self.nick(nickname)
		except socket.error as ex:
			error('Failed to connect to IRC server.', ex)
			self.event_disconnect()
		else:
			self.listen()

	def error(self, chan, msg, reason=None):
		if reason:
			self.sendmsg(chan, '[{0}] {1} {2}'.format(self.color('!', red), msg, self.color('({0})'.format(reason), grey)))
		else:
			self.sendmsg(chan, '[{0}] {1}'.format(self.color('!', red), msg))

	def event_connect(self):
		if user_modes:
			self.mode(nickname, '+' + user_modes)
		if nickserv_password:
			self.identify(nickname, nickserv_password)
		self.join_channel(channel)

	def event_disconnect(self):
		self.sock.close()
		time.sleep(10)
		self.connect()

	def event_kick(self, chan, kicked):
		if chan == channel and kicked == nickname:
			time.sleep(3)
			self.join_channel(channel, key)

	def event_message(self, nick, chan, msg):
		#try:
			if msg[:1] in '@!':
				if time.time() - self.last < throttle_cmd:
					if not self.slow:
						self.error(chan, 'Slow down nerd!')
						self.slow = True
				else:
					args = msg.split()
					if msg == '@iex':
						self.sendmsg(chan, bold + 'IExTrading IRC Bot - Developed by acidvegas in Python - https://acid.vegas/iex')
					elif args[0] == '!stock':
						if len(args) == 2:
							symbols = args[1].upper()
							if ',' in symbols:
								symbols = ','.join(list(symbols.split(','))[:10])
								data    = IEX.quote(symbols)
								if type(data) == dict:
									self.sendmsg(chan, self.stock_info(data))
								elif type(data) == list:
									for line in self.stock_table(data):
										self.sendmsg(chan, line)
										time.sleep(throttle_msg)
								else:
									self.error(chan, 'Invalid stock names!')
							else:
								symbol = args[1]
								data = IEX.quote(symbol)
								if data:
									self.sendmsg(chan, self.stock_info(data))
								else:
									self.error(chan, 'Invalid stock name!')
						elif len(args) == 3:
							if args[1] == 'company':
								symbol = args[2]
								data = IEX.company(symbol)
								if data:
									self.sendmsg(chan, '{0} {1} ({2}) {3} {4} {5} {6} {7} {8}'.format(self.color('Company:', white), data['companyName'], data['symbol'], self.color('|', grey), data['website'], self.color('|', grey), data['industry'], self.color('|', grey), data['CEO']))
									self.sendmsg(chan, '{0} {1}'.format(self.color('Description:', white), data['description']))
								else:
									self.error('Invalid stock name!')
							elif args[1] == 'search':
								query = args[2].lower()
								data = [{'symbol':item['symbol'],'name':item['name']} for item in IEX.symbols() if query in item['name'].lower()]
								if data:
									count = 1
									max_length = len(max([item['name'] for item in data], key=len))
									for item in data[:10]:
										self.sendmsg(chan, '[{0}] {1} {2} {3}'.format(self.color(str(count), pink), item['name'].ljust(max_length), self.color('|', grey), item['symbol']))
										count += 1
										time.sleep(throttle_msg)
								else:
									self.error(chan, 'No results found.')
							elif args[1] == 'list':
								options = {'active':'mostactive','gainers':'gainers','losers':'losers','volume':'iexvolume','percent':'iexpercent'}
								option = args[2]
								try:
									option = options[option]
								except KeyError:
									self.error(chan, 'Invalid option!', 'Valid options are active, gainers, losers, volume, & percent')
								else:
									data = IEX.lists(option)
									for line in self.stock_table(data):
										self.sendmsg(chan, line)
										time.sleep(throttle_msg)
							elif args[1] == 'news':
								symbol = args[2]
								data   = IEX.news(symbol)
								if data:
									count  = 1
									for item in data:
										self.sendmsg(chan, '[{0}] {1}'.format(self.color(str(count), pink), item['headline']))
										self.sendmsg(chan, ' - ' + self.color(item['url'], grey))
										count += 1
										time.sleep(throttle_msg)
								else:
									self.error(chan, 'Invalid stock name!')
				self.last = time.time()
		#except Exception as ex:
		#	self.error(chan, 'Unknown error occured!', ex)

	def event_nick_in_use(self):
		self.nick('IEX_' + str(random_int(10,99)))

	def handle_events(self, data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			self.event_connect()
		elif args[1] == '433':
			self.event_nick_in_use()
		elif args[1] == 'KICK':
			chan   = args[2]
			kicked = args[3]
			self.event_kick(nick, chan, kicked)
		elif args[1] == 'PRIVMSG':
			nick = args[0].split('!')[0][1:]
			chan = args[2]
			msg  = ' '.join(args[3:])[1:]
			if chan == channel:
				self.event_message(nick, chan, msg)

	def identify(self, nick, passwd):
		self.sendmsg('nickserv', f'identify {nick} {passwd}')

	def join_channel(self, chan, key=None):
		self.raw(f'JOIN {chan} {key}') if key else self.raw('JOIN ' + chan)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if line):
					debug(line)
					if len(line.split()) >= 2:
						self.handle_events(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			#except Exception as ex:
			#	error('Unexpected error occured.', ex)
			#	break
		self.event_disconnect()

	def mode(self, target, mode):
		self.raw(f'MODE {target} {mode}')

	def nick(self, nick):
		self.raw('NICK ' + nick)

	def raw(self, msg):
		self.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

IRC().connect()
