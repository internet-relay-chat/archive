#!/usr/bin/env python
# Scroll IRC Art Bot - Developed by acidvegas in Python (https://git.acid.vegas/scroll)

'''
Props:
	- forked idea from malcom's img2irc (https://github.com/waveplate/img2irc)
	- big props to wrk (wr34k) for forking this one

pull request: https://github.com/ircart/scroll/pull/3

'''

import io

try:
	from PIL import Image
except ImportError:
	raise SystemExit('missing required \'pillow\' library (https://pypi.org/project/pillow/)')

async def convert(data, img_width=80):
	image = Image.open(io.BytesIO(data))
	del data
	(width, height) = image.size
	img_height = img_width / width * height
	del height, width
	image.thumbnail((img_width, img_height), Image.Resampling.LANCZOS)
	del img_height, img_width
	ansi_image = AnsiImage(image)
	del image
	CHAR = '\u2580'
	buf = ''
	for (y, row) in enumerate(ansi_image.halfblocks):
		last_fg = -1
		last_bg = -1
		for (x, pixel_pair) in enumerate(row):
			fg = pixel_pair.top.irc
			bg = pixel_pair.bottom.irc
			if x != 0:
				if fg == last_fg and bg == last_bg:
					buf += CHAR
				elif bg == last_bg:
					buf += f'\x03{fg}{CHAR}'
				else:
					buf += f'\x03{fg},{bg}{CHAR}'
			else:
				buf += f'\x03{fg},{bg}{CHAR}'
			last_fg = fg
			last_bg = bg
		if y != len(ansi_image.halfblocks) - 1:
			buf += '\n'
		else:
			buf += '\x0f'
	return buf.splitlines()

def hex_to_rgb(color):
	r = color >> 16
	g = (color >> 8) % 256
	b = color % 256
	return (r,g,b)

def rgb_to_hex(rgb):
	(r,g,b) = rgb
	return (r << 16) + (g << 8) + b

def color_distance_squared(c1, c2):
	dr = c1[0] - c2[0]
	dg = c1[1] - c2[1]
	db = c1[2] - c2[2]
	return dr * dr + dg * dg + db * db

class AnsiPixel:
	def __init__(self, pixel_u32):
		self.RGB99 = [
			0xffffff, 0x000000, 0x00007f, 0x009300, 0xff0000, 0x7f0000, 0x9c009c, 0xfc7f00,
			0xffff00, 0x00fc00, 0x009393, 0x00ffff, 0x0000fc, 0xff00ff, 0x7f7f7f, 0xd2d2d2,
			0x470000, 0x472100, 0x474700, 0x324700, 0x004700, 0x00472c, 0x004747, 0x002747,
			0x000047, 0x2e0047, 0x470047, 0x47002a, 0x740000, 0x743a00, 0x747400, 0x517400,
			0x007400, 0x007449, 0x007474, 0x004074, 0x000074, 0x4b0074, 0x740074, 0x740045,
			0xb50000, 0xb56300, 0xb5b500, 0x7db500, 0x00b500, 0x00b571, 0x00b5b5, 0x0063b5,
			0x0000b5, 0x7500b5, 0xb500b5, 0xb5006b, 0xff0000, 0xff8c00, 0xffff00, 0xb2ff00,
			0x00ff00, 0x00ffa0, 0x00ffff, 0x008cff, 0x0000ff, 0xa500ff, 0xff00ff, 0xff0098,
			0xff5959, 0xffb459, 0xffff71, 0xcfff60, 0x6fff6f, 0x65ffc9, 0x6dffff, 0x59b4ff,
			0x5959ff, 0xc459ff, 0xff66ff, 0xff59bc, 0xff9c9c, 0xffd39c, 0xffff9c, 0xe2ff9c,
			0x9cff9c, 0x9cffdb, 0x9cffff, 0x9cd3ff, 0x9c9cff, 0xdc9cff, 0xff9cff, 0xff94d3,
			0x000000, 0x131313, 0x282828, 0x363636, 0x4d4d4d, 0x656565, 0x818181, 0x9f9f9f,
			0xbcbcbc, 0xe2e2e2, 0xffffff
		]
		self.irc  = self.nearest_hex_color(pixel_u32, self.RGB99)

	def nearest_hex_color(self, pixel_u32, hex_colors):
		rgb_colors = [hex_to_rgb(color) for color in hex_colors]
		rgb_colors.sort(key=lambda rgb: color_distance_squared(hex_to_rgb(pixel_u32), rgb))
		hex_color = rgb_to_hex(rgb_colors[0])
		return hex_colors.index(hex_color)

class AnsiPixelPair:
	def __init__(self, top, bottom):
		self.top = top
		self.bottom = bottom

class AnsiImage:
	def __init__(self, image):
		self.bitmap = [[rgb_to_hex(image.getpixel((x, y))) for x in range(image.size[0])] for y in range(image.size[1])]
		if len(self.bitmap) % 2 != 0:
			self.bitmap.append([0 for x in range(image.size[0])])
		ansi_bitmap = [[AnsiPixel(y) for y in x] for x in self.bitmap]
		ansi_canvas = list()
		for two_rows in range(0, len(ansi_bitmap), 2):
			top_row = ansi_bitmap[two_rows]
			bottom_row = ansi_bitmap[two_rows+1]
			ansi_row = list()
			for i in range(len(self.bitmap[0])):
				top_pixel = top_row[i]
				bottom_pixel = bottom_row[i]
				pixel_pair = AnsiPixelPair(top_pixel, bottom_pixel)
				ansi_row.append(pixel_pair)
			ansi_canvas.append(ansi_row)
		self.image = image
		self.halfblocks = ansi_canvas