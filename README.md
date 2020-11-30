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

All the following steps require you to have Python installed. If you haven't, download it [here](https://www.python.org/downloads/).

1. Clone the repository (`git https://github.com/lorossi/every-color` if you have git installed ) or download the release [here](https://github.com/lorossi/every-color/releases/).
2. Navigate the folder containing the file named `every-color.py`
3. Install all the needed dependencies using `pip3 install -r requirements.txt`
4. Launch the script with the command `python3 every-color.py`. Check below for the available options or launch writing `python3 every-color.py -h`
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

# Minimum selection, random color sorting
![centered start](https://github.com/lorossi/every-color/blob/master/output/18bits-center.png?raw=true)

*Started with a random pixel in center*

![centered start](https://github.com/lorossi/every-color/blob/master/output/18bits-center-2.png?raw=true)

*Started with a random pixel in center*

![2 points random](https://github.com/lorossi/every-color/blob/master/output/18bits-2points-random.png?raw=true)

*Started with 2 pixels in random positions*

![4 points random](https://github.com/lorossi/every-color/blob/master/output/18bits-4points-random.png?raw=true)

*Started with 4 pixels in random positions*

![5 points random](https://github.com/lorossi/every-color/blob/master/output/18bits-5points-random.png?raw=true)

*Started with 5 pixels in random positions*

![4 points corners](https://github.com/lorossi/every-color/blob/master/output/18bits-4points-corners.png?raw=true)

*Started with 1 pixel in each corner*

# Minimum selection, hue color sorting
![centered start](https://github.com/lorossi/every-color/blob/master/output/18bits-4points-corners-hue.png?raw=true)

*Started with a random pixel in center*

![corners start](https://github.com/lorossi/every-color/blob/master/output/18bits-center-hue.png?raw=true)

*Started with 1 pixel in each corner*

# Average selection, random color sorting
![centered start](https://github.com/lorossi/every-color/blob/master/output/frames_2/200.png?raw=true)

*Started with a random pixel in center*

![corners start](https://github.com/lorossi/every-color/blob/master/output/18bits-corners-average.png?raw=true)

*Started with 1 pixel in each corner*

# Composition
![composition](https://github.com/lorossi/every-color/blob/master/output/64_small_12bits.png?raw=true)

*Composition of 64 small images*

# Progess Gifs
![minimum gif](https://github.com/lorossi/every-color/blob/master/output/video_1.gif?raw=true)

*Minimum selection*

![minimum gif final](https://github.com/lorossi/every-color/blob/master/output/frames_1/200.png?raw=true)

*Final image*

![average gif](https://github.com/lorossi/every-color/blob/master/output/video_2.gif?raw=true)

*Average selection*

![average gif final](https://github.com/lorossi/every-color/blob/master/output/frames_2/200.png?raw=true)

*Final image*

# Additional infos

The script takes quite a while to generate big pictures (up to ~1.5 hours for 18 bits pictures with minimum selection, up to ~48 hours with average selection). There isn't much room for optimizations and, according to my tests, parallelization won't increase much the speed. The most computationally expensive process is searching for a better pixel.

Maybe Cython could help me with this task?

FFmpeg commands used:
- To create MP4 video: `ffmpeg -i frames/%03d.png -vf fps=25,scale=512:-1 out.mp4 -y`
- To create GIFS:`ffmpeg -i frames/%03d.png -vf fps=20,scale=512:-1 out.gif -y`

I like PEP8 but 79 characters is definitely not enough.

# License

This project is distributed under Attribution 4.0 International (CC BY 4.0) license.
