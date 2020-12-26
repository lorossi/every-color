import time
import random
import logging
import argparse
from PIL import Image
from math import sqrt
from pathlib import Path
from datetime import datetime


# container for the current pixel. Easier than just using x and y variables
class Pixel:
    def __init__(self, x=None, y=None):
        self.__x = x
        self.__y = y

    # overrides == for list sorting and placing
    def __eq__(self, other):
        return self.__x == other.x and self.__y == other.y

    # getter and setter for x
    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    # getter and setter for y
    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    # getter for position as tuple
    @property
    def pos(self):
        return (self.__x, self.__y)


# color container. Easier than just using tuples
class Color:
    def __init__(self, r=None, g=None, b=None):
        self.__r = r
        self.__g = g
        self.__b = b
        self.__h, self.__s, self.__v = self.__calculateHSB()

    def __calculateHSB(self):
        # converts RGB values to HSV (hue, saturation, value)
        # value is the same as brightness (but b was alerady taken...)

        # r, g, b normalized in range [0, 1]
        r, g, b = self.__r / 255.0, self.__g / 255.0, self.__b / 255.0

        cmax = max(r, g, b)    # maximum of r, g, b
        cmin = min(r, g, b)    # minimum of r, g, b
        diff = cmax - cmin     # diff of cmax and cmin.

        # cmax == cmin => hue = 0
        if cmax == cmin:
            h = 0.0
        # cmax == r, we need to calculate h
        elif cmax == r:
            h = (60 * ((g - b) / diff) + 360) % 360

        # cmax == g, we need to calculate h
        elif cmax == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        #  cmax == b, we need to calculate h
        elif cmax == b:
            h = (60 * ((r - g) / diff) + 240) % 360

        # cmax == 0 -> s = 0
        if cmax == 0:
            s = 0.0
        else:
            s = (diff / cmax) * 100

        # v calculation
        v = cmax * 100
        return (h, s, v)

    @property
    def RGB(self):
        return (self.__r, self.__g, self.__b)

    @property
    def HSB(self):
        return (self.__h, self.__s, self.__v)

    @property
    def r(self):
        return self.__r

    @property
    def g(self):
        return self.__g

    @property
    def b(self):
        return self.__b

    @property
    def h(self):
        return self.__h

    @property
    def s(self):
        return self.__s

    @property
    def v(self):
        return self.__v


# generates all the colors needed in the script
def generate_colors(bits):
    colors = []
    # total items for each channel
    length = int(2 ** (bits / 3))
    # step of each channel
    step = int(256 / length)

    # fill colors list by iterating over each channel
    for r in range(0, length):
        for g in range(0, length):
            for b in range(0, length):
                # rgb values stored as Color item
                new_color = Color(r * step, g * step, b * step)
                colors.append(new_color)

    return colors


# calculate image size in pixels by number of colors
def calculate_size(bits):
    # total number of colors
    color_number = int(2 ** bits)
    if sqrt(color_number).is_integer():
        # if the image is a square
        width = int(sqrt(color_number))
        height = int(sqrt(color_number))
    else:
        # in case the image is not a square
        height = int(sqrt(color_number / 2))
        width = int(color_number / height)
    return width, height


# generate an empty grid
def generate_grid(width, height):
    grid = [[None for y in range(height)] for x in range(width)]
    return grid


# calculate difference between two colors
def color_difference(color1, color2):
    return (color1.r - color2.r) ** 2 + \
           (color1.g - color2.g) ** 2 + \
           (color1.b - color2.b) ** 2


# find free neighbors of a pixel by iterating over its square container
def find_free_neighbors(grid, pixel):
    # grid size
    width = len(grid)
    height = len(grid[0])

    free_neighbors = []
    # horizontal
    for px in range(pixel.x - 1, pixel.x + 2):
        if px >= width or px < 0:
            # out of boundaries
            continue
        # vertical
        for py in range(pixel.y - 1, pixel.y + 2):
            if py >= height or py < 0:
                # out of boundaries
                continue
            if pixel.pos == (px, py):
                # same as central
                continue
            if not grid[px][py]:
                # if empty
                free_neighbors.append(Pixel(px, py))

    return free_neighbors


# calculates color difference between a color and its neighbors
def calculate_diff(grid, pixel, color, dist_selection):
    diffs = []
    width = len(grid)
    height = len(grid[0])

    # same as find_free_neighbors but we want to find full neighbors (not
    # empty as in the other)
    # horizontal
    for px in range(pixel.x - 1, pixel.x + 2):
        if px >= width or px < 0:
            # out of boundaries
            continue
        # vertical
        for py in range(pixel.y - 1, pixel.y + 2):
            if py >= height or py < 0:
                # out of boundaries
                continue
            if pixel.pos == (px, py):
                # same as central
                continue
            if grid[px][py]:
                # if full
                diffs.append(color_difference(grid[px][py], color))

    if dist_selection == "average":
        # returns average according to diff
        average = sum(diffs) / len(diffs)
        return average
    elif dist_selection == "min":
        # returns least diff
        return min(diffs)


# place pixels in grid, effectively creating the image
def place_pixels(grid, colors, start_position, start_points, start_color,
                 sort_colors, dist_selection, progress_pics, path, filename):
    # started time
    started = time.time()

    # progess tracking
    percent = 0
    percent_interval = 1
    last_percent = 0
    time_lost = 0

    # progress pictures tracking
    last_saved = 0
    if progress_pics > 0:
        # percent intervals at which a progress has to be saved
        save_interval = 100 / progress_pics
    else:
        save_interval = None

    # all available pixels (free with at least one neighbor)
    available_pixels = []
    # best pixel for the current color
    selected_pixel = Pixel()

    # start color picking
    if start_color == "white":
        # colors list is built from least to most colored, so we need to put
        # the last item in front
        colors.insert(0, colors.pop(-1))
    elif start_color == "black":
        # first color is already the darkest, so no need to do anything
        pass
    elif start_color == "random":
        # pick a random element index
        color_index = random.randrange(len(colors))
        # put the random selected color in front
        colors.insert(0, colors.pop(color_index))

    # sort colors
    if sort_colors == "hue":
        # sort by hue
        colors = sorted(colors, key=lambda c: c.h)
    elif sort_colors == "saturation":
        # sort by saturation
        colors = sorted(colors, key=lambda c: c.s)
    elif sort_colors == "brightness":
        # sort by value (brightness)
        colors = sorted(colors, key=lambda c: c.v)
    elif sort_colors == "default":
        # do nothing
        pass
    elif sort_colors == "reverse":
        # reverse
        colors.reverse()
    elif sort_colors == "random":
        # suffle array
        random.shuffle(colors)

    # iterate over colors
    for i in range(len(colors)):
        c = colors[i]

        if (i < start_points):
            # pick the first starting points
            # grid size
            width = len(grid)
            height = len(grid[0])

            # place first pixel(s)
            if start_position == "center" and i == 0:
                # if center, we use only the first one
                selected_pixel = Pixel(int(width/2), int(height/2))
            elif start_position == "corner" and i < 5:
                # only the first 4 corners
                # bit masking to get corners
                x = (i >> 1) & 1
                y = (i >> 0) & 1
                selected_pixel = Pixel(x * (width - 1), y * (height - 1))

            elif start_position == "random":
                # random position
                selected_pixel = Pixel(random.randrange(width),
                                       random.randrange(height))

            # put the color on the selected pixel in the grid
            grid[selected_pixel.x][selected_pixel.y] = c

            # we append it to the list of available pixels
            available_pixels.append(selected_pixel)
        else:
            # sort pixels by color difference
            sorted_pixels = sorted(available_pixels,
                                   key=lambda p:
                                   calculate_diff(grid, p, c, dist_selection))

            # pick the closest one
            selected_pixel = sorted_pixels[0]

            # put the color on the best pixel on the grid
            grid[selected_pixel.x][selected_pixel.y] = c

        # find all new available pixels
        new_available_pixels = find_free_neighbors(grid, selected_pixel)
        # has any new pixel been added?
        new_pixels = False
        # loop throught them
        for n in new_available_pixels:
            # if the new found is not already in the list, add it
            if n not in available_pixels:
                available_pixels.append(n)
                new_pixels = True
        # if any new pixel has been added:
        if new_pixels:
            # shuffle the array
            random.shuffle(available_pixels)
        # remove the pixel that we just put
        available_pixels.remove(selected_pixel)

        # update percent
        percent = i / len(colors) * 100
        # is it time to save a progress pic yet?
        if progress_pics > 0 and percent - last_saved >= save_interval:
            # yes it is
            last_saved = last_percent
            last_saved = round(percent * 4) / 4  # round to quarters
            # .5 -> .50, (add zeroes at the and)
            last_saved_str = format(last_saved, '.2f')
            # grid deep copy
            progress_grid = [g[:] for g in grid]
            image = generate_image(progress_grid)
            logging.info(f"progress image at {last_saved_str}% generated")
            progress_filename = f"{filename}-progress-{last_saved_str}"
            full_path = save_image(image, path=path,
                                   filename=progress_filename)
            logging.info(f"progress image saved: {full_path}")

        # update logging
        if percent - last_percent >= percent_interval:
            last_percent = percent
            # calculate elapsed time
            elapsed_seconds = int((time.time() - started)) - time_lost
            elapsed_minutes = int(elapsed_seconds / 60)
            elapsed_hours = int(elapsed_minutes / 60)

            # calculate total time
            total_seconds = 100 * elapsed_seconds / percent
            # calculate remaining time
            remaining_seconds = int(total_seconds - elapsed_seconds)
            remaining_minutes = int(remaining_seconds / 60)
            remaining_hours = int(remaining_minutes / 60)

            # string that will be logged
            log_string = f"progress: {int(percent)}%, elapsed: "

            # stop showing plural a plural S when it's singular!
            suffix = ""
            # elapsed time in a correct fashion
            if elapsed_hours > 0:
                if elapsed_hours > 1:
                    suffix = "s"
                log_string += f"{elapsed_hours} hour{suffix}"
            elif elapsed_minutes > 0:
                if elapsed_minutes > 1:
                    suffix = "s"
                log_string += f"{elapsed_minutes} minute{suffix}"
            else:
                if elapsed_seconds > 1:
                    suffix = "s"
                log_string += f"{elapsed_seconds} second{suffix}"

            # reset suffix
            suffix = ""
            log_string += ", remaining: "
            # remaining time in a correct fashion
            if remaining_hours > 0:
                if remaining_hours > 1:
                    suffix = "s"
                log_string += f"{remaining_hours} hour{suffix}"
            elif remaining_minutes > 0:
                if remaining_minutes > 1:
                    suffix = "s"
                log_string += f"{remaining_minutes} minute{suffix}"
            else:
                if remaining_seconds > 1:
                    suffix = "s"
                log_string += f"{remaining_seconds} second{suffix}"

            # it's time to log!
            logging.info(log_string)

            # check if it's time to pause
            script_paused = False
            pause_started = time.time()
            while Path('PAUSE').is_file():
                # notify only the first time
                if not script_paused:
                    logging.info("script paused")
                    script_paused = True
                # lower the load on the cpu
                time.sleep(1)

            # if file does not exist but the script was script_paused,
            # it's time to start again
            if script_paused:
                time_lost += int(time.time() - pause_started)
                logging.info(f"script resumed. Total time lost: {time_lost} "
                             "seconds.")

    # elapsed time in seconds
    seconds = int((time.time() - started))
    return grid, seconds, time_lost


# generates the image by dumping the grid into a png
def generate_image(grid, default_color=Color(0, 0, 0)):
    width = len(grid)
    height = len(grid[0])

    image = Image.new("RGB", (width, height))
    # loop throught grid list
    for x in range(width):
        for y in range(height):
            # fill with default color if empty
            if not grid[x][y]:
                grid[x][y] = Color(default_color.r,
                                   default_color.g,
                                   default_color.b)

            image.putpixel((x, y), grid[x][y].RGB)
    return image


# save image to file
def save_image(image, path, filename):
    if path:
        Path(path).mkdir(parents=True, exist_ok=True)
        full_path = f"{path}/{filename}.png"
    else:
        full_path = f"{filename}.png"
    image.save(full_path)
    return full_path


def main():
    # arguments parsing
    parser = argparse.ArgumentParser(description="Generate an image with all"
                                     "the possible colors in the"
                                     " RGB colorspace")

    parser.add_argument("-b", "--bits", type=int,
                        help="image depth bits (defaults to 15)", default=15)
    parser.add_argument("-n", "--number", type=int,
                        help="number of images to generate (defaults to 1)",
                        default=1)
    parser.add_argument("-p", "--startposition", action="store",
                        choices=["center", "corner", "random"],
                        default="center",
                        help="location of the first pixel "
                        "(defaults to center)")
    parser.add_argument("-c", "--startcolor", action="store",
                        choices=["white", "black", "random"], default="random",
                        help="color of the first pixel (defaults to random)")
    parser.add_argument("-o", "--output", type=str, default="output",
                        help="output folder (defaults to output) "
                        "make sure that the path exists")
    parser.add_argument("-l", "--log", action="store",
                        choices=["file", "console"], default="file",
                        help="log destination (defaults to file)")
    parser.add_argument("--progresspics", type=int,
                        help="number of progress pics to be saved "
                        "(defaults to 0)", default=0)
    parser.add_argument("--sortcolors", action="store",
                        choices=["hue", "saturation", "brightness",
                                 "default", "reverse", "random"],
                        default="random",
                        help="sort colors before placing them "
                        "(defaults to random)")
    parser.add_argument("--distselection", action="store",
                        choices=["min", "average"], default="min",
                        help="select how new colors are selected according"
                        "to their distance (defaults to min)")
    parser.add_argument("--startpoints", type=int,
                        help="number of starting points (defaults to 1). "
                        "Doesn't work if start position is set to center",
                        default=1)
    parser.add_argument("--seed", type=str, help="random seed", default=None)

    args = parser.parse_args()

    # logging setup
    if args.log == "file":
        logfile = "every-color.log"
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                            level=logging.INFO, filename=logfile,
                            filemode="w+")
        print("Logging in every-color.log")
    else:
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                            level=logging.INFO)

    logging.info("script started")

    # color depth
    bits = args.bits
    if bits % 3 != 0:
        logging.error("the bit number must be dibisible by 3")
        return

    # random.seed
    seed = args.seed
    if not seed:
        # seed not provided, we use current time (converted to string)
        seed = str(datetime.now().timestamp())

    # get output folder
    path = args.output

    random.seed(seed)
    logging.info(f"seed used for random functions: {seed}")
    logging.info("basic setup completed, generating image with "
                 f"{bits} bits")

    width, height = calculate_size(bits)
    start_position = args.startposition
    start_points = args.startpoints
    start_color = args.startcolor
    sort_colors = args.sortcolors
    dist_selection = args.distselection
    progress_pics = args.progresspics
    logging.info(f"start position: {start_position}, "
                 f"start points: {start_points}, "
                 f"start color: {start_color}, "
                 f"sort color: {sort_colors}, "
                 f"dist selection: {dist_selection}, "
                 f"saving progress pics: {progress_pics}, "
                 f"destination image size: {width}x{height} pixels.")

    logging.info("starting pixels placement.")

    logging.info("keep in mind that the remaining time will not be "
                 "accurate at least until about half of the progress has "
                 "gone by. Don't panic, the script is most likely not "
                 "stuck but very computationally heavy and as such "
                 "quite slow. Let it run!")

    images_to_generate = args.number
    for x in range(images_to_generate):
        logging.info(f"started generating image {x+1}/{images_to_generate}")
        # random seeding
        random.seed(time.time())
        # output filename generation
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"every-color-{now}"

        colors = generate_colors(bits)
        logging.info("colors generated")

        grid = generate_grid(width, height)
        logging.info("empty image grid generated")

        colored_grid, seconds, lost = place_pixels(grid, colors,
                                                   start_position,
                                                   start_points, start_color,
                                                   sort_colors, dist_selection,
                                                   progress_pics, path,
                                                   filename)

        logging.info(f"pixel placing completed! It took {seconds} seconds. "
                     f"Total effective time: {seconds - lost} seconds. "
                     f"Total paused time: {lost} seconds.")
        logging.info(f"average speed: {round((width * height) / seconds, 2)} "
                     "pixels per second")

        image = generate_image(colored_grid)
        logging.info(f"image {x+1}/{images_to_generate} generated")

        full_image_path = save_image(image, path=path, filename=filename)
        logging.info(f"image saved: {full_image_path}")

    logging.info("script ended")


if __name__ == "__main__":
    main()
