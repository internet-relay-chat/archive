#!/usr/bin/env python
# Tail Bot for syn (cause fuck gh0st and his skid scripts) - Developed by acidvegas in Python (https://git.acid.vegas/archive)

import asyncio
import aiofiles
import pathlib
import ssl
import time
import urllib.request
import os

class connection:
	server  = 'irc.supernets.org'
	port    = 6697
	ipv6    = False
	ssl     = True
	vhost   = None
	channel = '#dev'
	key     = None
	modes   = None

class identity:
	nickname = 'TailBot'
	username = 'tail'
	realname = 'gh0st is a skid LOL'
	nickserv = None

FIFO_PATH = pathlib.Path('HPOT_FIFO')

def color(msg, foreground, background=None):
	return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

def debug(data):
	print('{0} | [~] - {1}'.format(time.strftime('%I:%M:%S'), data))

def error(data, reason=None):
	print('{0} | [!] - {1} ({2})'.format(time.strftime('%I:%M:%S'), data, str(reason))) if reason else print('{0} | [!] - {1}'.format(time.strftime('%I:%M:%S'), data))

def ssl_ctx():
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	return ctx

class Bot():
	def __init__(self):
		self.last            = 0
		self.loops           = dict()
		self.slow            = False
		self.reader          = None
		self.writer          = None

	async def raw(self, data):
		self.writer.write(data[:510].encode('utf-8') + b'\r\n')
		await self.writer.drain()

	async def sendmsg(self, target, msg):
		await self.raw(f'PRIVMSG {target} :{msg}')

	async def irc_error(self, chan, msg, reason=None):
		await self.sendmsg(chan, '[{0}] {1} {2}'.format(color('ERROR', red), msg, color(f'({reason})', grey))) if reason else await self.sendmsg(chan, '[{0}] {1}'.format(color('ERROR', red), msg))

	async def loop_tail(self):
		if not os.path.exists(FIFO_PATH):
			os.mkfifo(FIFO_PATH)
		while True:
			async with aiofiles.open(FIFO_PATH, mode='r') as fifo:
				while True:
					try:
						content = await fifo.readlines()
						for line in content:
							await self.sendmsg(connection.channel, line)
							await asyncio.sleep(0.1)
					except Exception as ex:
						try:
							await self.irc_error(connection.channel, 'Error occured in the loop_tail function!', ex)
							break
						except:
							error('Fatal error occured in the loop_tail functions!', ex)
							break

	async def connect(self):
		while True:
			try:
				options = {
					'host'       : connection.server,
					'port'       : connection.port,
					'limit'      : 1024,
					'ssl'        : ssl_ctx() if connection.ssl else None,
					'family'     : 10 if connection.ipv6 else 2,
					'local_addr' : connection.vhost
				}
				self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(**options), 300)
				await self.raw(f'USER {identity.username} 0 * :{identity.realname}')
				await self.raw('NICK ' + identity.nickname)
			except Exception as ex:
				error('failed to connect to ' + connection.server, ex)
			else:
				await self.listen()
			finally:
				self.loops   = dict()
				await asyncio.sleep(30)

	async def listen(self):
		while True:
			try:
				if self.reader.at_eof():
					break
				data = await asyncio.wait_for(self.reader.readuntil(b'\r\n'), 60)
				line = data.decode('utf-8').strip()
				args = line.split()
				debug(line)
				if line.startswith('ERROR :Closing Link:'):
					raise Exception('Connection has closed.')
				elif args[0] == 'PING':
					await self.raw('PONG '+args[1][1:])
				elif args[1] == '001':
					await asyncio.sleep(5)
					if connection.modes:
						await self.raw(f'MODE {identity.nickname} +{connection.modes}')
					if identity.nickserv:
						await self.sendmsg('NickServ', f'IDENTIFY {identity.nickname} {identity.nickserv}')
					await self.raw(f'JOIN {connection.channel} {connection.key}') if connection.key else await self.raw('JOIN ' + connection.channel)
					self.loops['tail'] = asyncio.create_task(self.loop_tail())
				elif args[1] == '433':
					error('The bot is already running or nick is in use.')
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass
			except Exception as ex:
				error('fatal error occured', ex)
				break
			finally:
				self.last = time.time()

# Main
print('#'*56)
print('#{:^54}#'.format(''))
print('#{:^54}#'.format('Tail IRC Bot (for syn)'))
print('#{:^54}#'.format('Developed by acidvegas in Python (without 3rd party libraries cause im not a skid like gh0st)'))
print('#{:^54}#'.format('https://git.acid.vegas/archive (fuck twistednet supernets wanna-be)'))
print('#{:^54}#'.format(''))
print('#'*56)
asyncio.run(Bot().connect())
