#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
img2irc
Copyright (C) 2012 perplexa
"""

__author__ = "perplexa"
__version__ = "0.3"

import sys
if sys.version_info[:2] < (2, 6):
    raise RuntimeError("Python v2.6 or later required")

# requires python image library
import Image
import getopt
import StringIO
import sys
import time
import urllib2

# define our palettes
palette = {
  "mirc": {
     0: [255,255,255],
     1: [0,0,0],
     2: [0,0,127],
     3: [0,147,0],
     4: [255,0,0],
     5: [127,0,0],
     6: [156,0,156],
     7: [252,127,0],
     8: [255,255,0],
     9: [0,252,0],
    10: [0,147,147],
    11: [0,255,255],
    12: [0,0,252],
    13: [255,0,255],
    14: [127,127,127],
    15: [210,210,210]
  },
  "perplexa": {
     0: [255,255,255],
     1: [0,0,0],
     2: [58,80,120],
     3: [174,206,146],
     4: [207,97,113],
     5: [158,24,40],
     6: [150,60,89],
     7: [150,138,56],
     8: [255,247,150],
     9: [197,247,121],
    10: [65,129,121],
    11: [113,190,190],
    12: [65,134,190],
    13: [207,158,190],
    14: [102,102,102],
    15: [190,190,190]
  }
}

# define default parameter values
use_palette = "perplexa"
line_delay = None
max_width = None

#convert RGB to CIE-L*a*b* color space (takes floats between 0.0-1.0)
def rgb_to_cielab(r, g, b):
  return xyz_to_cielab(*rgb_to_xyz(r, g, b))
  
def rgb_to_xyz(r, g, b):
  r = _r1(r)
  g = _r1(g)
  b = _r1(b)

  # observer. = 2°, illuminant = D65
  x = r * 0.4124 + g * 0.3576 + b * 0.1805
  y = r * 0.2126 + g * 0.7152 + b * 0.0722
  z = r * 0.0193 + g * 0.1192 + b * 0.9505

  return x, y, z

def _r1(y):
  y = ((y + 0.055) / 1.055) ** 2.4 if y > 0.04045 else y / 12.92
  return y * 100

def _r2(y):
  return y ** (1.0 / 3.0) if y > 0.008856 else (7.787 * y) + (16.0 / 116.0)

def xyz_to_cielab(x, y, z):
  x = x / 95.047
  y = y / 100.0
  z = z / 108.883

  x = _r2(x)
  y = _r2(y)
  z = _r2(z)

  L = (116 * y) - 16
  a = 500 * (x - y)
  b = 200 * (y - z)

  return L, a, b

def euclidian_distance(v1, v2):
  return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5

def nearest_color(lab):
  distance = None
  color = None
  for col in palette[use_palette]:
    clab = rgb_to_cielab(*[x / 255.0 for x in palette[use_palette][col]])
    cdist = euclidian_distance(clab, lab)
    if distance == None or cdist < distance:
      distance = cdist
      color = col
  return color

def usage():
  return """Usage: %s [OPTIONS] IMAGE
Convert IMAGE to IRC text.

Options:
  -d, --delay      define delay per line (seconds, float)
  -p, --palette    use specific palette (%s)
  -w, --width      limit image width to X pixels
""" % (sys.argv[0], ", ".join(palette.keys()))

# ## ### ##### ######## ##### ### ## #
# ## ### ##### ######## ##### ### ## #

if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "p:d:w:", ["palette=", "delay=", "width="])
  except getopt.GetoptError, err:
    sys.stderr.write(str(err) + "\n")
    sys.exit(2)

  for opt, arg in opts:
    if opt in ("-p", "--palette"):
      if arg not in palette:
        sys.stderr.write("Invalid palette: %s\nUse one of the following: %s\n" % (arg, ", ".join(palette.keys())))
        sys.exit(2)
      use_palette = arg
    
    if opt in ("-d", "--delay"):
      line_delay = float(arg)

    if opt in ("-w", "--width"):
      max_width = int(arg)

  if not len(args):
    sys.stderr.write(usage())
    sys.exit(2)
  fn = args[0]

  try:
    if fn[0:4] == "http":
      sock = urllib2.urlopen(fn)
      data = sock.read()
      sock.close()
      fil = StringIO.StringIO(data)
    else:
      fil = fn
    img = Image.open(fil)
  except:
    sys.stderr.write("Could not open file: %s\n" % fn)
    sys.exit(2)

  img = img.convert(mode="RGBA")

  bg = Image.new("RGBA", img.size, (255, 255, 255))
  bg.paste(img, img)

  width, height = bg.size
  if max_width:
    height = int(height * (max_width / float(width)))
    width = max_width
    bg = bg.resize((width, height))

  pxl = bg.load()
  prv = None

  for y in range(height):
    for x in range(width):
      r, g, b, a = pxl[x, y]
      col = nearest_color(rgb_to_cielab(r / 255.0, g / 255.0, b / 255.0))
      if prv == None or prv != col:
        sys.stdout.write("\x03%s,%sXX" % (col, col))
        prv = col
      else:
        sys.stdout.write("XX")
    sys.stdout.write("\n")
    prv = None

    if line_delay:
      sys.stdout.flush()
      time.sleep(line_delay)
