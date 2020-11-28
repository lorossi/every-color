# Every color

I wanted to generate an image containing every color, so here we go.

This *not-so-handy* tool is ready to make any image you want! Just simple these simple (I swear, it's simple) instructions.

## How it works

This is how the script operates:

1. It starts by generating and empty grid as big as the final image and a list containing every color with the wanted bit depth
2. It put a starting point (or more, according to the parameters) with a random (or not, again, according to the parameters) in a set location in the image
3. It calculates all candidate pixels (empty pixels neighboring a colored one)
4. It iterates over all pixels until we find the one with the least minimum (or average) neighborhood color difference (the selected pixel)
5. It fills the selected pixel
6. It loops throught steps 3-5 until all colors are placed
7. It saves the final image.

## Installation

1. Clone the repository or download the relase
2. Navigate the folder containing the file named `every-color.py`
3. Install all the needed dependencies using `pip3 install -r requirements.txt`
4. Launch the script with the command `python3 every-color.py`. Check below for the availabe options or launch writing `python3 every-color.py -h`
5. There you go! The image will be generated shortly after.

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
| `--PROGRESSPICS` | number of progress pics to be saved | `0` | `int` |
| `--SORTCOLORS` | sort colors before placing them | `random` | `{"hue", "saturation", "brightness", "default", "reverse", "random"}` |
| `--DISTSELECTION` | select how new colors are selected according to their distance | `min` | `{min, average}` |
| `--STARTPOINTS` | number of starting points | `1` | `int` |
| `--SEED` | seed for random function | `epoch time` | `str` |

All arguments are optionals

# Example usage
- Basic usage (1 image, 15 bits for each color, 1 starting at the center with a random color, logging in console, no progress pics, random color sorting, pixels selected by their minimum value): `python3 every-color-py`
- Generate 1 image with a color depth of 18 bits (512 by 512 pixels): `python3 every-color.py -b 18`
- Generate 5 images and log progress to console: `python3 every-color.py -n 5 -l console`
- Generate 2 images starting with from the central pixel and save them in `generated/`: `python3 every-color.py -n 2 -p center -o generated`
- Generate 1 image starting with white and save 200 progress pics: `python3 every-color.py -c white --PROGRESSPICS 200`
- Generate 1 image sorting all colors by hue: `python3 every-color.py --SORTCOLORS hue`
- Generate 10 images with 5 random starting points and average distance selections: `python3 every-color.py -n 5 --STARTPOINTS 5 --DISTSELECTION average`

## Pause script

If, for any reason, you need to pause the script, create a file called `PAUSE` in the working folder. As long as the file is there, the script will be paused.

## Outputs

**TODO**


# Additional infos

The script takes quite a while to generate big pictures (up to about half a day for 24 bits pictures). There isn't much room for optimizations and according to my tests, parallelization won't increase much the speed. The most computationally expensive process is searching for a better pixel.

FFmpeg commands used:
- To create MP4 video: `fmpeg -i frames/%03d.png -vf fps=25,scale=512:-1 out.mp4 -y`
- To create GIFS:`ffmpeg -i frames/%03d.png -vf fps=20,scale=512:-1 out.gif -y`

I like PEP8 but 79 characters is definitely not enough.

# License

This project is distributed under Attribution 4.0 International (CC BY 4.0) license.
