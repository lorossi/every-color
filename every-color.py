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

    # overrides == for list
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

    @property
    def RGB(self):
        return (self.__r, self.__g, self.__b)

    @property
    def r(self):
        return self.__r

    @property
    def g(self):
        return self.__g

    @property
    def b(self):
        return self.__b


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
def calculate_size(color_number):
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
def calculate_diff(grid, pixel, color):
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
    # average = sum(diffs) / len(diffs)
    # return average
    # THIS COULD ALSO WORK
    return min(diffs)


# place pixels in grid, effectively creating the image
def place_pixels(grid, colors, start_position, start_color, progress_pics,
                 path, filename):
    # started time
    started = datetime.now()

    # progess tracking
    percent = 0
    last_percent = 0

    # progress pictures tracking
    last_saved = 0

    # all available pixels (free with at least one neighbor)
    available_pixels = []
    # best pixel for the current color
    best_pixel = Pixel()

    # WELL WELL WELL

    if start_color == "white":
        # colors list is built from least to most colored, so we need to sort
        # it backwards (reverse it)
        colors.reverse()
    elif start_color == "black":
        # first color is already the darkest, so no need to do anything
        pass
    elif start_color == "random":
        # randomize the whole list
        random.shuffle(colors)

    # iterate over colors
    for x in range(len(colors)):
        c = colors[x]

        if len(available_pixels) == 0:
            # since we have no available pixels, we gotta pick a first one
            # this happens the first time ONLY

            # grid size
            width = len(grid)
            height = len(grid[0])

            # place first pixel
            if start_position == "center":
                best_pixel = Pixel(int(width/2), int(height/2))
            elif start_position == "corner":
                best_pixel = Pixel(random.randrange(width),
                                   random.randrange(height))
            elif start_position == "random":
                best_pixel = Pixel(int(width/2), int(height/2))
            # we append it to the list of available pixels
            available_pixels.append(best_pixel)
        else:
            # look throught every available pixel and find the one with the
            # least difference with the current color
            #  (that's why we call it "best pixel")
            best_pixel = sorted(available_pixels,
                                key=lambda p: calculate_diff(grid, p, c))[0]

        # put the color on the best pixel on the grid
        grid[best_pixel.x][best_pixel.y] = c

        # find all new available pixels
        new_available_pixels = find_free_neighbors(grid, best_pixel)
        # loop throught them
        for n in new_available_pixels:
            # if the new found is not already in the list, add it
            if n not in available_pixels:
                available_pixels.append(n)
        # remove the pixel that we just put
        available_pixels.remove(best_pixel)

        # update percent
        percent = x / len(colors) * 100
        # is it time to save a progress pic yet?
        if progress_pics and percent - last_saved >= 0.25:
            # yes it is
            last_saved = last_percent
            last_saved = round(percent * 4) / 4  # round to quarters
            # .5 -> .50, (add zeroes at the and)
            last_saved_str = format(last_saved, '.2f')
            progress_grid = [g[:] for g in grid]
            image = generate_image(progress_grid)
            logging.info(f"progress image at {last_saved_str}"
                         "%% generated")
            progress_filename = f"{filename}-progress-{last_saved_str}"
            full_path = save_image(image, path=path,
                                   filename=progress_filename)
            logging.info(f"progress image saved: {full_path}")

        # update logging
        if percent - last_percent >= 1:
            last_percent = percent
            # calculate elapsed time
            elapsed_seconds = int((datetime.now() - started).total_seconds())
            elapsed_minutes = int(elapsed_seconds / 60)
            elapsed_hours = int(elapsed_minutes / 60)
            # string that will be logged
            log_string = f"Progress: {int(percent)}%, elapsed: "

            # elapsed time in a correct fashion
            if elapsed_hours > 0:
                log_string += f"{elapsed_hours} hour(s)"
            elif elapsed_minutes > 0:
                log_string += f"{elapsed_minutes} minute(s)"
            else:
                log_string += f"{elapsed_seconds} second(s)"
            # it's time to log!
            logging.info(log_string)

    # elapsed time in seconds
    seconds = int((datetime.now() - started).total_seconds())
    return grid, seconds


# generates the image by dumping the grid into a png
def generate_image(grid, default_color=(0, 0, 0)):
    width = len(grid)
    height = len(grid[0])

    image = Image.new("RGB", (width, height))
    # loop throught grid list
    for x in range(width):
        for y in range(height):
            # fill with default color if empty
            if not grid[x][y].RGB:
                grid[x][y] = Color(default_color)

            image.putpixel((x, y), grid[x][y].RGB)
    return image


# save image to file
def save_image(image, path="", filename="everycolor"):
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
                        help="image depth bits (defaults to 15)", default=15)  # OK
    parser.add_argument("-n", "--number", type=int,
                        help="number of images to generate (defaults to 1)",
                        default=1)  # OK
    parser.add_argument("-p", "--startposition", action="store",
                        choices=["center", "corner", "random"],
                        default="center",
                        help="location of the first pixel "
                              "(defaults to center)")  # OK
    parser.add_argument("-c", "--startcolor", action="store",
                        choices=["white", "black", "random"], default="random",
                        help="color of the first pixel (defaults to random)")  # OK
    parser.add_argument("-o", "--output", type=str, default="output",
                        help="output folder (defaults to output)"
                        " make sure that the path exists")  # OK
    parser.add_argument("-l", "--log", action="store",
                        choices=["file", "console"], default="file",
                        help="log destination (defaults to file)")  # OK
    parser.add_argument("--progresspics", action="store_true",
                        help="saves a picture every 0.25%% of completion")  # OK
    parser.add_argument("--sortcolors", action="store",
                        choices=["no", "random", "hue"], default="no",
                        help="sort colors before placing them (defaults to no)") # NOT DONE YET
    parser.add_argument("--distselection", action="store",
                        choices=["min", "average"], default="min",
                        help="select how new colors are selected according to their distance (defaults to no)") # NOT DONE YET
    args = parser.parse_args()

    # logging setup
    if args.log == "file":
        logfile = __file__.replace(".py", ".log")
        logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                            level=logging.INFO, filename=logfile,
                            filemode="w+")
        print("Logging in every-color.log")
    else:
        logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                            level=logging.INFO)

    logging.info("script started")

    # color depth
    bits = args.bits
    if bits % 3 != 0:
        logging.error("The bit number must be dibisible by 3")
        return

    images_to_generate = args.number
    for x in range(images_to_generate):
        logging.info(f"started generating image {x+1}/{images_to_generate}")
        # random seeding
        random.seed(datetime.now())
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{now}-every-color"
        path = args.output
        logging.info("basic setup completed, generating image with "
                     f"{bits} bits")

        colors = generate_colors(bits)
        logging.info("colors generated")

        width, height = calculate_size(len(colors))
        logging.info(f"size calculated, generating a {width} "
                     f"by {height} image")

        grid = generate_grid(width, height)
        logging.info("empty image grid generated")

        start_position = args.startposition
        start_color = args.startcolor
        progress_pics = args.progresspics
        logging.info(f"start position: {start_position}, "
                     f"start color: {start_color}, "
                     f"saving progress pics: {progress_pics}. "
                     "Starting pixel placement")

        colored_grid, seconds = place_pixels(grid, colors, start_position,
                                             start_color, progress_pics, path,
                                             filename)
        logging.info(f"pixel placing completed! It took {seconds} seconds.")

        image = generate_image(colored_grid)
        logging.info("image generated")

        full_image_path = save_image(image, path=path, filename=filename)
        logging.info(f"image saved: {full_image_path}")

    logging.info("script ended")

if __name__ == "__main__":
    main()
