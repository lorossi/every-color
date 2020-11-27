# Every color

I wanted to generate an image containing every color, so here we go.

## How it works

**TODO**

## Arguments
| Command | Description | Defaults | Type |
|---|---|---|---|---|
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
**TODO**

## Outputs

**TODO**


# Additional infos

I like PEP8 but 79 characters is definitely not enough

# License
