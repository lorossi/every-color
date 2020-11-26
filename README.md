# Every color

I wanted to generate an image containing every color, so here we go.

## How it works

**TODO**

## Arguments
| Command | Description | Defaults | Type | Optional |
|---|---|---|---|---|
| `-h --help` | show help | `none` | - | - |
| `-n --NUMBER` | number of images to generate | `1` | `int` | ✓ |
| `-b --BITS` | image depth bits | `15` | `int` | ✓ |
| `-p --STARTPOSITION` | location of the first pixel  | `center` | `{center, corner, random}` | ✓ |
| `-c --STARTCOLOR` | color of the first pixel | `random` | `{white, black, random}` | ✓ |
| `-o --OUTPUT` | output folder | `output` | `str` | ✓ |
| `-l --LOG` | log destination | `file` | `{file, console}` | ✓ |
| `--progresspics` | saves a picture every 0.25% of completion (total of 400 pictures) | `False` | `flag` | ✓ |
| `--sortcolors` | sort colors before placing them | `no` | `{no, random, hue}` | *NOT IMPLEMENTED YET* |
| `--distselection` | select how new colors are selected according to their distance | `min` | `{min, average}` | *NOT IMPLEMENTED YET* | 

## Outputs

**TODO**
