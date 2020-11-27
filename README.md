# Every color

I wanted to generate an image containing every color, so here we go.

## How it works

**TODO**

## Arguments
| Command | Description | Defaults | Type |
|---|---|---|---|
| `-h --help` | show help | `none` | - | - |
| `-n --NUMBER` | number of images to generate | `1` | `int` |
| `-b --BITS` | image depth bits | `15` | `int` |
| `-p --STARTPOSITION` | location of the first pixel  | `center` | `{center, corner, random}` |
| `-c --STARTCOLOR` | color of the first pixel | `random` | `{white, black, random}` |
| `-o --OUTPUT` | output folder | `output` | `str` |
| `-l --LOG` | log destination | `file` | `{file, console}` | ✓ |
| `--progresspics` | number of progress pics to be saved | `0` | `int` |
| `--sortcolors` | sort colors before placing them | `random` | `{"hue", "saturation", "brightness", "default", "reverse", "random"}` |
| `--distselection` | select how new colors are selected according to their distance | `min` | `{min, average}` |
| `--startpoints` | number of starting points | `1` | `int` |

All arguments are optionals

# Example usage
- Basic usage (1 image, 15 bits for each color, 1 starting at the center with a random color, logging in console, no progress pics, random color sorting, pixels selected by their minimum value): `python3 every-color-py`
- Generate 1 image with a color depth of 18 bits (512 by 512 pixels): `python3 every-color.py -b 18`
- Generate 5 images and log progress to console: `python3 every-color.py -n 5 -l console`
- Generate 2 images starting with from the central pixel and save them in `generated/`: `python3 every-color.py -n 2 -p center -o generated`
- Generate 1 image starting with white and save 200 progress pics: `python3 every-color.py -c white --progress 200`
- Generate 1 image sorting all colors by hue: `python3 every-color.py --sortcolors hue`
- Generate 10 images with 5 random starting points and average distance selections: `python3 every-color.py -n 5 --startpoints 5 --distselection average`

**TODO**

## Outputs

**TODO**


# Additional infos

I like PEP8 but 79 characters is definitely not enough

# License

This project is distributed under Attribution 4.0 International (CC BY 4.0) license.
