/* Copyright (c) 2018 Trollforge. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Trollforge's name may not be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 */

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>
#include <stdbool.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#define STB_IMAGE_RESIZE_IMPLEMENTATION
#include "stb_image_resize.h"

#define R	0
#define G	1
#define B	2
#define A	3

#define DIST(x, y)	fabs(sqrtf((x[R] - y[R]) * (x[R] - y[R]) + \
				   (x[G] - y[G]) * (x[G] - y[G]) + \
				   (x[B] - y[B]) * (x[B] - y[B])))

#define ANSI_FMT	0
#define MIRC_FMT	1
#define EMOJI_FMT	2

#define VGA_PAL		0
#define MIRC_PAL	1
#define XIRC_PAL	2

typedef struct block_s {
	int color;
} block_t;

void usage(void);
int nearestcolor(float *pixel, int palette, float tlevel);
double huetorgb(double p, double q, double t);
void tweak(float *pixel, float sat, float lum);

int
main(int argc, char *argv[])
{
	int width = 0;
	int height = 0;
	int channels = 0;
	block_t *block = NULL;

	int format = ANSI_FMT;
	int palette = VGA_PAL;

	bool cp437 = false;
	bool useice = false;
	bool resize = false;

	long resize_width = 0;
	long resize_height = 0;

	int ch = 0;
	int fg = 0;
	int bg = 0;
	int lfg = 0;
	int lbg = 0;

	float *pixel = NULL;
	float *resized = NULL;

	float brightness = 100.0f;
	float saturation = 100.0f;
	float tlevel = 0.5f;

	bool verbose = false;

	while((ch = getopt(argc, argv, "b:f:p:s:t:w:v")) != -1) {
		switch (ch) {
			case 'b':
				brightness = strtof(optarg, NULL);
				break;
			case 'f':
				switch (optarg[0]) {
					case 'a':
						format = ANSI_FMT;
						break;
					case 'd':
						format = ANSI_FMT;
						cp437 = true;
						useice = true;
						break;
					case 'm':
						format = MIRC_FMT;
						break;
					case 'e':
						format = EMOJI_FMT;
						break;
					default:
						usage();
						break;
				}
				break;
			case 'p':
				switch (optarg[0]) {
					case 'm':
						palette = MIRC_PAL;
						break;
					case 'v':
						palette = VGA_PAL;
						break;
					case 'x':
						palette = XIRC_PAL;
						break;
					default:
						usage();
						break;
				}
				break;
			case 's':
				saturation = strtof(optarg, NULL);
				break;
			case 't':
				tlevel = strtof(optarg, NULL);
				break;
			case 'w':
				resize_width = strtol(optarg, NULL, 10);
				resize = true;
				break;
			case 'v':
				verbose = true;
				break;
			default:
				usage();
		}
	}
	argc -= optind;
	argv += optind;

	if (argc < 1) {
		usage();
	}

	/* XXX handle alpha eventually */
	/* channels is the number of channels in the original file, not our buffer) */
	pixel = stbi_loadf(argv[0], &width, &height, &channels, STBI_rgb_alpha);

	if (!pixel) {
		fprintf(stderr, "Unable to read file: %s\n", argv[0]);
		usage();
	}

	if (resize) {
		resize_height = height * resize_width / width;

		resized = malloc(sizeof(float) * resize_width * resize_height * STBI_rgb_alpha);

		stbir_resize_float(pixel, width, height, 0,
				   resized, resize_width, resize_height, 0,
				   STBI_rgb_alpha);

		free(pixel);

		pixel = resized;
		width = resize_width;
		height = resize_height;
	}

	if (!pixel) {
		usage();
	}

	if (verbose) {
		fprintf(stderr, "file: %s\n", argv[0]);
		fprintf(stderr, "format: %s\n", format == ANSI_FMT ? "ANSI" :
						format == MIRC_FMT ? "mIRC" :
						"emoji");
		fprintf(stderr, "palette: %s\n", palette == VGA_PAL ? "VGA" : "mIRC");

		if (format == ANSI_FMT) {
			fprintf(stderr, "iCE: %s\n", useice ? "true" : "false");
			fprintf(stderr, "CP437: %s\n", cp437 ? "true" : "false");
		}

		fprintf(stderr, "resized: %s\n", resize ? "true" : "false");
		fprintf(stderr, "geometry: %dx%d\n", width, height);
		fprintf(stderr, "channels: %d\n", STBI_rgb);

		fprintf(stderr, "saturation: %f\n", saturation);
		fprintf(stderr, "brightness: %f\n", brightness);
	}

	if (brightness != 100.0f || saturation != 100.0f) {
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				tweak(&pixel[((width * i) + j) * STBI_rgb_alpha],
				      saturation, brightness);
			}
		}
	}

	block = malloc(sizeof(block_t) * height * width);

	if (format == EMOJI_FMT) {
		palette = VGA_PAL;
	}

	for (int i = 0; i < height; i++) {
		for (int j = 0; j < width; j++) {
			block[(width * i) + j].color =
			nearestcolor(&pixel[((width * i) + j) * STBI_rgb_alpha],
				     palette, tlevel);
		}
	}
	free(pixel);

	if (format == EMOJI_FMT) {
		for (int i = 0; i < height; i++) {
			for (int j = 0; j < width; j++) {
				switch (block[(width * i) + j].color) {
					case 0:
						printf("⬛");
						break;
					case 1:
						printf("🔴");
						break;
					case 2:
						printf("💚");
						break;
					case 3:
						printf("💩");
						break;
					case 4:
						printf("💙");
						break;
					case 5:
						printf("💜");
						break;
					case 6:
						printf("📫");
						break;
					case 7:
						printf("👽");
						break;
					case 8:
						printf("💣");
						break;
					case 9:
						printf("🧠");
						break;
					case 10:
						printf("🎾");
						break;
					case 11:
						printf("🌞");
						break;
					case 12:
						printf("♿");
						break;
					case 13:
						printf("🐷");
						break;
					case 14:
						printf("💦");
						break;
					case 15:
						printf("💭");
						break;
					/* transparent */
					case -1:
						printf(" ");
						break;
				}
			}
			printf("\n");
		}
		return 0;
	}

	for (int i = 0; i + 1 < height; i += 2) {
		for (int j = 0; j < width; j++) {
			fg = block[(width * i) + j].color;
			bg = block[(width * (i + 1)) + j].color;

			/* dont print color codes if we dont have to */
			if (j != 0 && lbg == bg && lfg == fg) {
				/* try to save bytes */
				if (bg == fg) {
					printf(" ");
				} else {
					cp437 ? printf("\xdf") : printf("▀");
				}
			} else {
				/* XXX we dont really have to print both attrs */
				/* XXX not handling alpha here either */
				if (format == ANSI_FMT) {
					if (useice) {
						printf("\x1b[%s%d;%dm%s",
							/* bold and ice */
							(fg > 7 && bg > 7) ? "1;5;" :
							/* bold only */
							(fg > 7 && bg < 8) ? "1;" :
							/* ice only */
							(fg < 8 && bg > 7) ? "5;" :
							/* neither */
							"",
							fg > 7 ? fg - 8 + 30 : fg + 30,
							bg > 7 ? bg - 8 + 40 : bg + 40,
							bg == fg ? " " : cp437 ? "\xdf" : "▀");
					} else {
					/* XXX this doesnt work for extended colors */
					printf("\x1b[%d;%dm%s",
						fg < 8 ? fg + 30 : fg - 8 + 90,
						bg < 8 ? bg + 40 : bg - 8 + 100,
						bg == fg ? " " : cp437 ? "\xdf" : "▀");
					}
				} else {
					if (bg == -1 && fg != -1) {
						printf("\x03%d%s", fg, cp437 ? "\xdf" : "▀");
					} else if (fg == -1 && bg != -1) {
						printf("\x03%d%s", bg, cp437 ? "\xdc" : "▄");
					} else if (fg == -1 && bg == -1) {
						printf("\x03 ");
					} else {
						printf("\x03%d,%d%s", fg, bg,
						       bg == fg ? " " : cp437 ? "\xdf" : "▀");
					}
				}
			}
			lbg = bg;
			lfg = fg;
		}
		/* reset to prevent line bleeding on terms */
		if (format == ANSI_FMT) {
			printf("\x1b[0m%s", cp437 && width == 80 ? "" : "\n");
		} else {
			printf("\n");
		}
	}
	return 0;
}

int
nearestcolor(float *pixel, int palette, float tlevel)
{

	if (pixel[A] < tlevel) {
		return -1;
	}
	/* vga palette, maybe add more */
	float vga_palette[16][3] = {{0.00f, 0.00f, 0.00f},
				    {0.66f, 0.00f, 0.00f},
				    {0.00f, 0.66f, 0.00f},
				    {0.66f, 0.33f, 0.00f},
				    {0.00f, 0.00f, 0.66f},
				    {0.66f, 0.00f, 0.66f},
				    {0.00f, 0.66f, 0.66f},
				    {0.66f, 0.66f, 0.66f},
				    {0.33f, 0.33f, 0.33f},
				    {1.00f, 0.85f, 0.85f},
				    {0.33f, 1.00f, 0.33f},
				    {1.00f, 1.00f, 0.33f},
				    {0.33f, 0.33f, 1.00f},
				    {1.00f, 0.33f, 1.00f},
				    {0.33f, 1.00f, 1.00f},
				    {1.00f, 1.00f, 1.00f}};

	float mirc_palette[16][3] = {{1.00f, 1.00f, 1.00f},
				     {0.00f, 0.00f, 0.00f},
				     {0.00f, 0.00f, 0.50f},
				     {0.00f, 0.57f, 0.00f},
				     {1.00f, 0.00f, 0.00f},
				     {0.50f, 0.00f, 0.00f},
				     {0.61f, 0.00f, 0.61f},
				     {0.98f, 0.50f, 0.00f},
				     {1.00f, 1.00f, 0.00f},
				     {0.00f, 0.98f, 0.00f},
				     {0.00f, 0.57f, 0.57f},
				     {0.00f, 1.00f, 1.00f},
				     {0.00f, 0.33f, 0.98f},
				     {1.00f, 0.00f, 1.00f},
				     {0.50f, 0.50f, 0.50f},
				     {0.82f, 0.82f, 0.82f}};

	float xirc_palette[99][3] = {{1.00f, 1.00f, 1.00f},
				     {0.00f, 0.00f, 0.00f},
				     {0.00f, 0.00f, 0.50f},
				     {0.00f, 0.57f, 0.00f},
				     {1.00f, 0.00f, 0.00f},
				     {0.50f, 0.00f, 0.00f},
				     {0.61f, 0.00f, 0.61f},
				     {0.98f, 0.50f, 0.00f},
				     {1.00f, 1.00f, 0.00f},
				     {0.00f, 0.98f, 0.00f},
				     {0.00f, 0.57f, 0.57f},
				     {0.00f, 1.00f, 1.00f},
				     {0.00f, 0.33f, 0.98f},
				     {1.00f, 0.00f, 1.00f},
				     {0.50f, 0.50f, 0.50f},
				     {0.82f, 0.82f, 0.82f},
				     {0.28f, 0.00f, 0.00f},
				     {0.28f, 0.13f, 0.00f},
				     {0.28f, 0.28f, 0.00f},
				     {0.20f, 0.28f, 0.00f},
				     {0.00f, 0.28f, 0.00f},
				     {0.00f, 0.28f, 0.17f},
				     {0.00f, 0.28f, 0.28f},
				     {0.00f, 0.15f, 0.28f},
				     {0.00f, 0.00f, 0.28f},
				     {0.18f, 0.00f, 0.28f},
				     {0.28f, 0.00f, 0.28f},
				     {0.28f, 0.00f, 0.16f},
				     {0.45f, 0.00f, 0.00f},
				     {0.45f, 0.23f, 0.00f},
				     {0.45f, 0.45f, 0.00f},
				     {0.32f, 0.45f, 0.00f},
				     {0.00f, 0.45f, 0.00f},
				     {0.00f, 0.45f, 0.29f},
				     {0.00f, 0.45f, 0.45f},
				     {0.00f, 0.25f, 0.45f},
				     {0.00f, 0.00f, 0.45f},
				     {0.29f, 0.00f, 0.45f},
				     {0.45f, 0.00f, 0.45f},
				     {0.45f, 0.00f, 0.27f},
				     {0.71f, 0.00f, 0.00f},
				     {0.71f, 0.39f, 0.00f},
				     {0.71f, 0.71f, 0.00f},
				     {0.49f, 0.71f, 0.00f},
				     {0.00f, 0.71f, 0.00f},
				     {0.00f, 0.71f, 0.44f},
				     {0.00f, 0.71f, 0.71f},
				     {0.00f, 0.39f, 0.71f},
				     {0.00f, 0.00f, 0.71f},
				     {0.46f, 0.00f, 0.71f},
				     {0.71f, 0.00f, 0.71f},
				     {0.71f, 0.00f, 0.42f},
				     {1.00f, 0.00f, 0.00f},
				     {1.00f, 0.55f, 0.00f},
				     {1.00f, 1.00f, 0.00f},
				     {0.70f, 1.00f, 0.00f},
				     {0.00f, 1.00f, 0.00f},
				     {0.00f, 1.00f, 0.63f},
				     {0.00f, 1.00f, 1.00f},
				     {0.00f, 0.55f, 1.00f},
				     {0.00f, 0.00f, 1.00f},
				     {0.65f, 0.00f, 1.00f},
				     {1.00f, 0.00f, 1.00f},
				     {1.00f, 0.00f, 0.60f},
				     {1.00f, 0.35f, 0.35f},
				     {1.00f, 0.71f, 0.35f},
				     {1.00f, 1.00f, 0.44f},
				     {0.81f, 1.00f, 0.38f},
				     {0.44f, 1.00f, 0.44f},
				     {0.40f, 1.00f, 0.79f},
				     {0.43f, 1.00f, 1.00f},
				     {0.35f, 0.71f, 1.00f},
				     {0.35f, 0.35f, 1.00f},
				     {0.77f, 0.35f, 1.00f},
				     {1.00f, 0.40f, 1.00f},
				     {1.00f, 0.35f, 0.74f},
				     {1.00f, 0.61f, 0.61f},
				     {1.00f, 0.83f, 0.61f},
				     {1.00f, 1.00f, 0.61f},
				     {0.89f, 1.00f, 0.61f},
				     {0.61f, 1.00f, 0.61f},
				     {0.61f, 1.00f, 0.86f},
				     {0.61f, 1.00f, 1.00f},
				     {0.61f, 0.83f, 1.00f},
				     {0.61f, 0.61f, 1.00f},
				     {0.86f, 0.61f, 1.00f},
				     {1.00f, 0.61f, 1.00f},
				     {1.00f, 0.58f, 0.83f},
				     {0.00f, 0.00f, 0.00f},
				     {0.07f, 0.07f, 0.07f},
				     {0.16f, 0.16f, 0.16f},
				     {0.21f, 0.21f, 0.21f},
				     {0.30f, 0.30f, 0.30f},
				     {0.40f, 0.40f, 0.40f},
				     {0.51f, 0.51f, 0.51f},
				     {0.62f, 0.62f, 0.62f},
				     {0.74f, 0.74f, 0.74f},
				     {0.89f, 0.89f, 0.89f},
				     {1.00f, 1.00f, 1.00f}};

	float delta = 10;
	int color = 0;

	if (palette == MIRC_PAL) {
		for (int i = 0; i < 16; i++) {
			if (DIST(pixel, mirc_palette[i]) < delta) {
				delta = DIST(pixel, mirc_palette[i]);
				color = i;
			}
		}
	} else if (palette == VGA_PAL) {
		for (int i = 0; i < 16; i++) {
			if (DIST(pixel, vga_palette[i]) < delta) {
				delta = DIST(pixel, vga_palette[i]);
				color = i;
			}
		}
	} else { /* XIRC_PAL */
		for (int i = 0; i < 99; i++) {
			if (DIST(pixel, xirc_palette[i]) < delta) {
				delta = DIST(pixel, xirc_palette[i]);
				color = i;
			}
		}
	}
	return color;
}

double
huetorgb(double p, double q, double t)
{
	if (t < 0.0f) {
		t += 1.0f;
	} else if (t > 1.0f) {
		t -= 1.0f;
	}

	if (t < 1.0f/6.0f) {
		return p + (q - p) * 6.0f * t;
	}

	if (t < 0.5f) {
		return q;
	}

	if (t < 2.0f/3.0f) {
		return p + (q - p) * ((2.0f/3.0f) - t) * 6.0f;
	}
	return p;
}

/* sat and lum are percentages */
void
tweak(float *pixel, float sat, float lum)
{
	/* convert rgb to hsl */
	float r = pixel[R];
	float g = pixel[G];
	float b = pixel[B];

	float max = r > g ? r > b ? r : b : g > b ? g : b;
	float min = r < g ? r < b ? r : b : g < b ? g : b;

	float h = (min + max) / 2.0f;
	float s = (min + max) / 2.0f;
	float l = (min + max) / 2.0f;

	float d = max - min;

	float q = 0.0f;
	float p = 0.0f;

	if (max == min) {
		s = l = 0.0f;
	} else {
		s = l > 0.5f ? d / (2.0f - max - min) : d / (max + min);
		if (max == r) {
			h = (g - b) / d + (g < b ? 6.0f : 0.0f);
		} else if (max == g) {
			h = (b - r) / d + 2.0f;
		} else { /* max == b */
			h = (r - g) / d + 4.0f;
		}
	}
	h /= 6.0f;

	/* apply tweaks */
	s *= sat * 0.01f;
	l *= lum * 0.01f;

	/* convert from hsl to rgb */
	if (s == 0.0f) {
		r = g = b = l;
	} else {
		q = l < 0.5f ? l * (1.0f + s) : l + s - l * s;
		p = 2 * l - q;
		r = huetorgb(p, q, h + 1.0f/3.0f);
		g = huetorgb(p, q, h);
		b = huetorgb(p, q, h - 1.0f/3.0f);
	}

	/* clamp values */
	pixel[R] = r < 0.0f ? 0.0f : r > 1.0f ? 1.0f : r;
	pixel[G] = g < 0.0f ? 0.0f : g > 1.0f ? 1.0f : g;
	pixel[B] = b < 0.0f ? 0.0f : b > 1.0f ? 1.0f : b;
}

void
usage(void)
{
	fprintf(stderr, "usage: p2u [options] input\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "-b percent     Adjust brightness levels, default is 100.\n");
	fprintf(stderr, "-f a|d|e|m     Specify output format ANSI, DOS (ANSI with\n");
	fprintf(stderr, "               CP437 characters), emoji or mirc.  Default is ANSI.\n");
	fprintf(stderr, "-p m|v|x       Specify palette to use, mirc, VGA, or extended mirc,\n");
	fprintf(stderr, "               default is VGA.\n");
	fprintf(stderr, "-s percent     Adjust saturation levels, default is 100.\n");
	fprintf(stderr, "-t percent     Adjust transparency threshold of alpha channel,\n");
	fprintf(stderr, "               default is 50.\n");
	fprintf(stderr, "-w width       Specify output width, default is the image width.\n");
	fprintf(stderr, "\n");
	exit(1);
}
