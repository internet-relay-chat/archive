#!/usr/bin/env python
# IRC2ANSI - Developed by acidvegas in Python (https://git.acid.vegas/archive)

import re

def IRC2ANSI(text):
	''' Convert IRC art to ANSI art. '''

	_formats = {
		'\x02': '\033[1m', # Bold
		'\x1D': '\033[3m', # Italic
		'\x1F': '\033[4m', # Underline
		'\x16': '\033[7m', # Reverse
		'\x0f': '\033[0m', # Reset
	}

	_colors = {
		'00': ('37',  '47'), # White
		'01': ('30',  '40'), # Black
		'02': ('34',  '44'), # Blue
		'03': ('32',  '42'), # Green
		'04': ('91', '101'), # Red
		'05': ('31',  '41'), # Brown
		'06': ('35',  '45'), # Purple
		'07': ('33',  '43'), # Orange
		'08': ('93', '103'), # Yellow
		'09': ('92', '102'), # Light Green
		'10': ('36',  '46'), # Teal
		'11': ('96', '106'), # Cyan
		'12': ('94', '104'), # Light Blue
		'13': ('95', '105'), # Magenta
		'14': ('90', '100'), # Gray
		'15': ('37',  '47')  # Light Gray
	}

	for i in range(16,100): # Add support for 99 colors
		_colors[str(i)] = (str(i), str(i))

	irc_color_regex = re.compile(r'\x03((?:\d{1,2})?(?:,\d{1,2})?)?')

	def replace_irc_color(match):
		''' Replace IRC color codes with ANSI color codes. '''
		if (irc_code := match.group(1)):
			codes = irc_code.split(',')
			foreground = '0'+codes[0] if len(codes[0]) == 1 else codes[0]
			background = ('0'+codes[1] if len(codes[1]) == 1 else codes[1]) if len(codes) == 2 else None
			ansi_foreground = _colors.get(foreground, '37')[0]
			ansi_background = _colors.get(background, '47')[1]
			return f'\033[{ansi_foreground};{ansi_background}m' if background else  f'\033[{ansi_foreground}m'
		return '\033[0m' # Reset colors on no match

	for item in _formats:
		if item in text:
			text = text.replace(item, _formats[item])
	text = text.replace('\n', '\033[0m\n') # Make sure we end with a reset code

	return irc_color_regex.sub(replace_irc_color, text) + '\033[0m'


if __name__ == '__main__':

	'''A simple script to test the IRC2ANSI function. (can you tell m using vscode yet...)
	Usage: ./irc2ansi.py <path>, where <path> is a file or directory containing IRC art.
	When using a directory, the script will loop through all files in the directory and play them randomly, acting as a screensaver.'''

	import os      #
	import sys     # We import these libraries here so they are only loaded when running the script directly
	import time    # This way, the script can still be imported as module for other scripts, without loading these libraries
	import pathlib # This is useful for testing the script directly and shows and example of how to use it in other scripts
	import random  #

	PRINT_TITLES = True # Set to False to disable printing titles when looping dircetories

	if len(sys.argv) == 2:
		try:
			import chardet
		except ImportError:
			raise SystemExit('missing chardet module (pip install chardet)')

		if os.path.exists(sys.argv[1]):
			option = sys.argv[1]

			def play(path):
				with open(path, 'rb') as art_file:
					data = art_file.read()
					enc  = chardet.detect(data)['encoding']
					for line in IRC2ANSI(data.decode(enc)).split('\n'):
						print(line)
						time.sleep(0.05)

			if os.path.isdir(option):
				if (results := list(pathlib.Path(option).rglob('*.[tT][xX][tT]'))):
					while True:
						random.shuffle(results)
						for result in results:
							play(result)
							if PRINT_TITLES:
								print(result)
							time.sleep(3)

			elif os.path.isfile(option):
				play(option)

			else:
				raise SystemExit('invalid path')

		else:
			raise SystemExit('invalid path')

	else:
		raise SystemExit('missing or invalid arguments (usage: ./irc2ansi.py <path>)')
