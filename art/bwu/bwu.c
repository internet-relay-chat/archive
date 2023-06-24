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

#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#define STB_IMAGE_RESIZE_IMPLEMENTATION
#include "stb_image_resize.h"

void usage(void);

#define P(row, col)	(pixel[width * (row) + (col)] > 0x7f)
#define D(x)		printf(x)

int
main(int argc, char *argv[])
{
	uint8_t *pixel;
	int width;
	int height;
	int channels;

	int resize_width = 0;
	int resize_height;
	uint8_t *resized;

	char ch;

	int use_color = 0;
	int fg = 0;
	int bg = 0;

	while((ch = getopt(argc, argv, "w:f:b:")) != -1) {
		switch (ch) {
			case 'w':
				resize_width = strtol(optarg, NULL, 10);
				break;
			case 'f':
				use_color = 1;
				fg = strtol(optarg, NULL, 10);
				break;
			case 'b':
				use_color = 1;
				bg = strtol(optarg, NULL, 10);
				break;
			default:
				usage();
				break;
		}
	}
	argc -= optind;
	argv += optind;

	if (argc < 1) {
		usage();
	}

	pixel = stbi_load(argv[0], &width, &height, &channels, 1);

	if (resize_width) {
		resize_height = height * resize_width / width;
		resized = malloc(resize_width * resize_height);

		stbir_resize_uint8(pixel, width, height, 0,
				   resized, resize_width, resize_height, 0,
				   1);

		free(pixel);
		pixel = resized;

		height = resize_height;
		width = resize_width;
	}

	for (int r = 0; r < height - 1; r += 2) {

		if (use_color) {
			printf("\03%d,%d", fg, bg);
		}

		for (int c = 0; c < width - 1; c += 2) {

			( P(r    , c) &&  P(r    , c + 1) &&
			  P(r + 1, c) &&  P(r + 1, c + 1)) ? D("█"):

			( P(r    , c) &&  P(r    , c + 1) &&
			  P(r + 1, c) && !P(r + 1, c + 1)) ? D("▛"):

			( P(r    , c) && !P(r    , c + 1) &&
			  P(r + 1, c) &&  P(r + 1, c + 1)) ? D("▙"):

			( P(r    , c) && !P(r    , c + 1) &&
			  P(r + 1, c) && !P(r + 1, c + 1)) ? D("▌"):

			( P(r    , c) &&  P(r    , c + 1) &&
			 !P(r + 1, c) &&  P(r + 1, c + 1)) ? D("▜"):

			( P(r    , c) &&  P(r    , c + 1) &&
			 !P(r + 1, c) && !P(r + 1, c + 1)) ? D("▀"):

			( P(r    , c) && !P(r    , c + 1) &&
			 !P(r + 1, c) &&  P(r + 1, c + 1)) ? D("▚"):

			( P(r    , c) && !P(r    , c + 1) &&
			 !P(r + 1, c) && !P(r + 1, c + 1)) ? D("▘"):

			(!P(r    , c) &&  P(r    , c + 1) &&
			  P(r + 1, c) &&  P(r + 1, c + 1)) ? D("▟"):

			(!P(r    , c) &&  P(r    , c + 1) &&
			  P(r + 1, c) && !P(r + 1, c + 1)) ? D("▞"):

			(!P(r    , c) && !P(r    , c + 1) &&
			  P(r + 1, c) &&  P(r + 1, c + 1)) ? D("▄"):

			(!P(r    , c) && !P(r    , c + 1) &&
			  P(r + 1, c) && !P(r + 1, c + 1)) ? D("▖"):

			(!P(r    , c) &&  P(r    , c + 1) &&
			 !P(r + 1, c) &&  P(r + 1, c + 1)) ? D("▐"):

			(!P(r    , c) &&  P(r    , c + 1) &&
			 !P(r + 1, c) && !P(r + 1, c + 1)) ? D("▝"):

			(!P(r    , c) && !P(r    , c + 1) &&
			 !P(r + 1, c) &&  P(r + 1, c + 1)) ? D("▗"):

			D(" ");
		}
		printf("\n");
	}
	return 0;
}

void usage(void)
{
	fprintf(stderr, "usage: bwu [options] input\n");
	fprintf(stderr, "-w width       set width.\n");
	fprintf(stderr, "-f color       set foreground.\n");
	fprintf(stderr, "-b color       set background.\n");

	exit(1);
}
