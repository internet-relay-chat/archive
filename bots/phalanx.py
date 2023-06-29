#!/usr/bin/env python
# phalanx localhost bot - developed by acidvegas in python (https://git.acid.vegas/archive)

import asyncio
import random
import re
import sys
import time

class settings:
	admin     = 'acidvegas!~stillfree@most.dangerous.motherfuck' # Can use wildcards (Must be in nick!user@host format)
	access    = [admin,]
	oper_user = 'phalanx'
	oper_pass = 'simps0nsfAn420'

# Formatting Control Characters / Color Codes
bold        = '\x02'
reset       = '\x0f'
green       = '03'
red         = '04'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'

def color(msg, foreground, background=None):
	return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

def is_access(ident):
	result = False
	for item in settings.access:
		if re.compile(item.replace('*','.*')).search(ident):
			result = True
	return result

def is_admin(ident):
	return re.compile(settings.admin.replace('*','.*')).search(ident)

def rndip():
	host = ''
	for i in range(3):
		host = host + ''.join([random.choice('0123456789ABCDEF') for n in range(8)]) + '.'
	return host + 'IP'

def rndnick():
	prefix = random.choice(['st','sn','cr','pl','pr','fr','fl','qu','br','gr','sh','sk','tr','kl','wr','bl']+list('bcdfgklmnprstvwz'))
	midfix = random.choice(('aeiou'))+random.choice(('aeiou'))+random.choice(('bcdfgklmnprstvwz'))
	suffix = random.choice(['ed','est','er','le','ly','y','ies','iest','ian','ion','est','ing','led','inger']+list('abcdfgklmnprstvwz'))
	return prefix+midfix+suffix

class clone:
	def __init__(self, identity={'chan':'#phalanx','nick':'phalanx','user':'W','host':'R','real':'\x0304ROMAN WAR PHALANX\x03'}):
		self.identity  = identity
		self.clones    = dict()
		self.destroy   = False
		self.reader    = None
		self.write     = None

	async def sendmsg(self, target, msg):
		await self.raw(f'PRIVMSG {target} :{msg}')

	async def error(self, chan, data, reason=None):
		await self.sendmsg(chan, '[{0}] {1}'.format(color('error', red), data, color(f'({reason})', grey))) if reason else await self.sendmsg(chan, '[{0}] {1}'.format(color('error', red), data))

	async def run(self):
		await self.connect()

	async def raw(self, data):
		self.writer.write(data[:510].encode('utf-8') + b'\r\n')
		await self.writer.drain()

	async def connect(self):
		while not self.destroy:
			try:
				options = {'host':'127.0.0.1', 'port':6667, 'limit':1024, 'ssl':None, 'family':2}
				self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(**options), 5)
				del options
				await self.raw('USER {0} 0 * :{1}'.format(self.identity['user'], self.identity['real']))
				await self.raw('NICK ' + self.identity['nick'])
				await self.listen()
			except Exception as ex:
				if self.identity['nick'] == 'phalanx':
					for item in self.clones:
						if self.clones[item]:
							self.clones[item].cancel()
					self.clones = dict()
				print('[!] - error occured (' + str(ex) + ')')
				await asyncio.sleep(random.randint(60,300))

	async def listen(self):
		while True:
			try:
				data = await asyncio.wait_for(self.reader.readuntil(b'\r\n'), 600)
				line = data.decode('utf-8').strip()
				if self.identity['nick'] == 'phalanx':
					print('[~] - ' + line)
				args = line.split()
				if args[0] == 'PING':
					await self.raw('PONG ' + args[1][1:])
				elif args[1] == '001':
					await self.raw('MODE ' + self.identity['nick'] + ' +dD')
					await self.raw(f'OPER {settings.oper_user} {settings.oper_pass}')
					await asyncio.sleep(1)
					await self.raw('SETHOST ' + self.identity['host'])
					await self.raw('JOIN #phalanx')
					if self.identity['chan'] != '#phalanx':
						await self.raw('JOIN ' + self.identity['chan'])
				elif args[1] == '433':
					self.identity['nick'] = rndnick()
					await self.raw('NICK ' + self.identity['nick'])
				elif args[1] == 'KICK' and len(args) >= 4:
					chan = args[2]
					nick = args[3]
					if nick == self.identity['nick']:
						await asyncio.sleep(3)
						await self.raw('JOIN ' + chan)
				elif args[1] == 'NICK' and len(args) == 3:
					nick = args[0][1:]
					new  = ' '.join(args[2:])[1:]
					if nick == self.identity['nick']:
						self.identity['nick'] = new
				elif args[1] == 'PRIVMSG' and len(args) >= 4:
					ident  = args[0][1:]
					nick   = args[0].split('!')[0][1:]
					target = args[2]
					msg    = ' '.join(args[3:])[1:]
					args   = msg.split()
					if is_admin(ident):
						if args[0] == '.access' and self.identity['nick'] == 'phalanx' and len(args) == 2:
							action = args[1][:1]
							host   = args[1][1:]
							if action == '+':
								if host not in settings.access:
									settings.access.append(host)
									await self.sendmsg(target, color('added', green))
							elif action == '-':
								if host in settings.access:
									settings.access.remove(host)
									await self.sendmsg(target, color('removed', red))
							elif action == '?':
								for item in settings.access:
									await self.sendmsg(target, color(item, yellow))
							else:
								await self.error('invalid command', 'usage: .access <+/-><host>')
					if is_access(ident):
						if args[0] == '.create' and self.identity['nick'] == 'phalanx' and len(args) >= 2:
							if len(self.clones) < 500:
								chan = args[1]
								if len(args) >= 6:
									nick = rndnick() if args[2] == '%r' else args[2]
									user = rndnick() if args[3] == '%r' else args[3]
									host = rndip()   if args[4] == '%r' else args[4]
									real = rndnick() if args[5] == '%r' else ' '.join(args[5:])
								elif len(args) == 2:
									ident = random.choice(idents).split()
									nick = ident[0]
									user = ident[1]
									host = ident[2]
									real = ' '.join(ident[3:])
								if nick != 'phalanx':
									options = {'chan':chan,'nick':nick,'user':user,'host':host,'real':real}
									self.clones[random.randint(1000,9999)] = asyncio.create_task(clone(identity=options).run())
							else:
								self.error(target, 'max clones', 'for now...')
						elif args[0] == '.destroy' and self.identity['nick'] != 'phalanx' and len(args) == 2:
							target = args[1]
							if target == self.identity['nick'] or (target == '*' and is_admin(ident)):
								self.destroy = True
								await self.raw('QUIT :' + random.choice(('*.net *.split', f'Ping timeout: {random.randint(180,300)} seconds', 'Connection closed', 'G-line: User has been permanently banned from this network.')))
						elif args[0] == '.raw' and len(args) >= 3:
							target = args[1]
							if target == 'phalanx' and not is_admin(ident):
								self.error('yeah right...')
							data   = ' '.join(args[2:])
							if '#5000' not in data:
								if target == self.identity['nick'] or (target == '*' and is_admin(ident)):
									if args[1] == '*':
										await asyncio.sleep(float('0.0'+str(random.randint(1111,9999))))
									await self.raw(data)
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass

# Main
idents = open('idents.txt').readlines()
asyncio.run(clone().run())
