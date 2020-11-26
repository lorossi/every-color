# Made by Lorenzo Rossi - 2020
# www.lorenzoros.si
# quarantine sucks

import random
import logging
import argparse

from pathlib import Path
from math import sqrt
from PIL import Image
from datetime import datetime


# calculates the size of the finale image according to the number of colors
def calculate_size(colors):
    # as long as the number of color makes sense, this will work
    full_size = int(colors ** 3)
    if sqrt(full_size).is_integer():
        width = int(sqrt(colors ** 3))
        height = int(sqrt(colors ** 3))
    else:
        # in case the image is not a square
        width = int(sqrt(full_size / 2))
        height = int(full_size / width)
    return width, height


# generates the colors that will be used in the image. The number are stored
#   in a cubic array in order to increase the speed of the lookups
def generate_colors(bits):
    # length of the for step
    step = int(256 / (2 ** (bits / 3)))
    # total number of for steps
    total_steps = int(256/step)
    # generate an empty 3d list
    colors = [[[None for b in range(total_steps)]
              for h in range(total_steps)] for r in range(total_steps)]

    for r in range(0, total_steps):
        for g in range(0, total_steps):
            for b in range(0, total_steps):
                # rgb values stored as a tuple
                new_color = (r * step, g * step, b * step)
                colors[r][g][b] = new_color
    return colors, step


# generates the empty 2d list that will contain the final image
def generate_empty_pixels(width, height):
    pixels = [[None for y in range(height)] for x in range(width)]
    return pixels


# check the average color of the neighbors
def check_neighbors_average(pixels, x, y, radius, width, height):
    average = [0, 0, 0]
    total_dist = 0

    # maximum distance of a pixel from the interesing pixel
    max_dist = radius * 2

    for i in range(x - radius, x + radius + 1):
        if i < 0 or i >= width:
            # out of boundaries
            continue

        for j in range(y - radius, y + radius + 1):
            if j < 0 or j >= height:
                # out of boundaries
                continue

            # we want to know the average of the pixels around the current
            # pixel so we skip it
            if (i, j) != (x, y):
                # if the pixel is colored...
                if pixels[i][j]:
                    # distance between (i, j) and (x, y)
                    dist = max_dist - (abs(i - x) + abs(j - y))
                    total_dist += dist
                    for p in range(3):
                        # weighted average
                        average[p] += pixels[i][j][p] * dist

    # if at least one has been found, we average
    if total_dist > 0:
        average = [a / total_dist for a in average]
    else:
        average = None

    return average


# find next suitable pixels
def find_next_pixels(pixels, x, y, width, height):
    next = []
    radius = 1

    for i in [x - radius, x + radius]:
        if i < 0 or i >= width:
            # out of boundaries
            continue

        if not pixels[i][y]:
            # this is a valid empty pixel
            next.append((i, y))

    for j in [y - radius, y + radius]:
        if j < 0 or j >= height:
            # out of boundaries
            continue

        if not pixels[x][j]:
            # this is a valid empty pixel
            next.append((x, j))

    return next


# squared distance of colors
def distance_sq(color1, color2):
    return (color1[0] - color2[0]) ** 2 + (color1[1] - color2[1]) ** 2 + \
            + (color1[2] - color2[2]) ** 2


# find the closest rgb color still available according to an average
def find_closest_color(cx, cy, cz, average_color, colors, step):
    # the colors are provided in a cube
    # we proceed by gradually incrasing the cube radius to find the coordinates
    # of the most similar color. This saves A LOT of time (from ~10 hours to
    # ~5 minutes
    colors_len = len(colors)
    distances = [
                    abs(cx - colors_len),
                    abs(cy - colors_len),
                    abs(cz - colors_len)
                ]

    max_dist = max(distances)
    min_sq_dist = step ** 2

    color_picked = False
    search_size = 0
    shortest_dist_sq = None
    nx, ny, nz = 0, 0, 0  # new color coordinates
    while not color_picked:
        for i in range(cx - search_size, cx + search_size + 1):
            # limit the index to the max size of the cube
            if i < 0:
                i = 0
            elif i >= colors_len:
                i = colors_len - 1
            for j in range(cy - search_size, cy + search_size + 1):
                # limit the index to the max size of the cube
                if j < 0:
                    j = 0
                elif j >= colors_len:
                    j = colors_len - 1
                for k in range(cz - search_size, cz + search_size + 1):
                    # limit the index to the max size of the cube
                    if k < 0:
                        k = 0
                    elif k >= colors_len:
                        k = colors_len - 1
                    # skip the current color if it has already been removed
                    if not colors[i][j][k]:
                        continue
                    # evaluate the squared distance
                    dist_sq = distance_sq(average_color, colors[i][j][k])
                    # if the distance is tles than the previous distance...
                    if not shortest_dist_sq or dist_sq <= shortest_dist_sq:
                        # new shortest distance
                        shortest_dist_sq = dist_sq
                        # if the distance is the least possible (1 step) or
                        # if the search radius is bigger than the color cube,
                        # it's time to return the closest color found
                        if dist_sq <= min_sq_dist or search_size >= max_dist:
                            color_picked = True
                            nx = i
                            ny = j
                            nz = k

        # increase search size
        search_size += 1
    return nx, ny, nz


# populate the pixels container
def populate_pixels(start_position, start_color, colors, pixels, width,
                    height, step, progresspics, path, filename):

    # keep track of how much it takes
    started = datetime.now()
    # search radius for average pixel color
    search_radius = 5

    # total number of placed pixels and image size
    placed_pixels = 0
    image_size = width * height
    # progress calculation
    percent = 0
    last_percent = None
    last_progress = 0

    # starting pixel position
    if start_position == "center":
        x, y = int(width / 2), int(height / 2)
    elif start_position == "corner":
        x, y = 0, 0
    elif start_position == "random":
        x, y = random.randint(0, width - 1),  random.randint(0, height - 1)

    # pixels to be filled
    pixels_queue = []
    # past filled pixels
    backtrack_pixels = []

    logging.info("pixel placing started. Warning: this script is fast at the "
                 "beginning but very slow at the end."
                 " Don't worry, just let it run.")
    # color coordinates declaration
    cx, cy, cz = 0, 0, 0
    # while not all the pixels have been placed
    while placed_pixels < image_size:
        # if this pixel has not been placed (only happens the first iteration)
        if not pixels[x][y]:
            average_color = check_neighbors_average(pixels, x, y,
                                                    search_radius, width,
                                                    height)
            if average_color:
                cx, cy, cz = find_closest_color(cx, cy, cz, average_color,
                                                colors, step)
            else:
                # this happens only when the program is first ran
                # starting color value
                if start_color == "white":
                    cx = len(colors) - 1
                    cy = len(colors) - 1
                    cz = len(colors) - 1
                elif start_color == "black":
                    cx = 0
                    cy = 0
                    cz = 0
                elif start_color == "random":
                    cx = random.randint(0, len(colors) - 1)
                    cy = random.randint(0, len(colors) - 1)
                    cz = random.randint(0, len(colors) - 1)

            # set the current pixel with the new color
            pixels[x][y] = colors[cx][cy][cz]
            # delete color from colors cube
            colors[cx][cy][cz] = None
            # add this pixel to the list of placed pixels
            backtrack_pixels.append((x, y))
            # update the number of placed pixels
            placed_pixels += 1

        # this is ugly... but i don't know how to make it prettier
        if placed_pixels <= image_size:
            # check if we have pixels still inside the queue
            if len(pixels_queue) == 0:
                # if we don't, find the possible pixels
                pixels_queue = find_next_pixels(pixels, x, y, width, height)
                # and shuffle them to add some randomness
                random.shuffle(pixels_queue)

            # check the queue
            if not pixels_queue:
                # if no pixels are available, we go back to the most recent
                # placed pixel
                next_position = backtrack_pixels.pop(-1)
            else:
                # otherwise, pick a pixel from the queue (randomly, as it is
                # shuffled when generated)
                next_position = pixels_queue.pop(0)

            # update coords to next position
            x = next_position[0]
            y = next_position[1]

        # update percent
        percent = round(placed_pixels / image_size * 100, 2)
        # is it time to save a progress pic yet?
        if progresspics and percent - last_progress >= 0.25:
            last_progress = round(percent * 4) / 4  # round to quarters
            last_progress = format(last_progress, '.2f')  # .5 -> .50, etc
            # yes it is
            print(last_progress)
            progress_pixels = [p[:] for p in pixels]
            im = generate_image(progress_pixels, width, height)
            logging.info(f"progress image at {last_progress}%% generated")
            progress_filename = f"{filename}-progress-{last_progress}"
            full_path = save_image(im, path=path, filename=progress_filename)
            logging.info(f"progress image saved: {full_path}")

        # update logging
        if percent % 1 == 0 and percent != last_percent:
            last_percent = int(percent)
            # calculate elapsed time
            elapsed_seconds = int((datetime.now() - started).total_seconds())
            elapsed_minutes = int(elapsed_seconds / 60)
            elapsed_hours = int(elapsed_minutes / 60)
            # string that will be logged
            log_string = f"Progress: {int(percent)}%, elapsed: "

            # elapsed time in a correct fashion
            if elapsed_hours > 0:
                log_string += f"{elapsed_hours} hours"
            elif elapsed_minutes > 0:
                log_string += f"{elapsed_minutes} minutes"
            else:
                log_string += f"{elapsed_seconds} seconds"
            # it's time to log!
            logging.info(log_string)

    # total elapsed time
    elapsed_seconds = int((datetime.now() - started).total_seconds())

    return pixels, elapsed_seconds


# generates the image by dumping the pixels into a png
def generate_image(pixels, width, height, default_color=(0, 0, 0)):
    image = Image.new("RGB", (width, height))
    # loop throught pixels list
    for x in range(width):
        for y in range(height):
            if not pixels[x][y]:
                pixels[x][y] = default_color
            image.putpixel((x, y), pixels[x][y])
    return image


# save image to file
def save_image(image, path="", filename="everycolor"):
    Path(path).mkdir(parents=True, exist_ok=True)
    full_path = f"{path}/{filename}.png"
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
                        help="location of the first bit (defaults to center)")
    parser.add_argument("-c", "--startcolor", action="store",
                        choices=["white", "black", "random"], default="white",
                        help="color of the first bit (defaults to white)")
    parser.add_argument("-o", "--output", type=str, default="output",
                        help="output folder (defaults to output)"
                        " make sure that the path exists")
    parser.add_argument("-l", "--log", action="store",
                        choices=["file", "console"], default="file",
                        help="log destination (defaults to file)")
    parser.add_argument("--progresspics", action="store_true",
                        help="saves a picture every 0.25%% of completion")
    args = parser.parse_args()

    # logging setup
    if args.log == "file":
        logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                            level=logging.INFO, filename="every-color.log",
                            filemode="w+")
        print("Logging in every-color.log")
    else:
        logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                            level=logging.INFO)

    logging.info("script started")
    # color depth
    color_bits = args.bits
    if color_bits % 3 != 0:
        logging.error("The bit number must be dibisible by 3")
        return

    images_to_generate = args.number
    for x in range(images_to_generate):
        logging.info(f"started generating image {x+1}/{images_to_generate}")
        # random seeding
        random.seed(datetime.now())
        # filename generation
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{now}-every-color"
        path = args.output
        logging.info("basic setup completed, generating image with "
                     f"{color_bits} bits")

        colors, step = generate_colors(color_bits)
        logging.info("colors generated")

        width, height = calculate_size(len(colors))
        logging.info(f"size calculated, generating a {width} "
                     "by {height} image")

        pixels = generate_empty_pixels(width, height)
        logging.info("empty pixels container generated")

        start_position = args.startposition
        start_color = args.startcolor
        pixels, seconds = populate_pixels(start_position, start_color, colors,
                                          pixels, width, height, step,
                                          args.progresspics, path, filename)
        logging.info(f"pixel placing completed! It took {seconds} seconds")

        im = generate_image(pixels, width, height)
        logging.info("image generated")

        full_path = save_image(im, path=path, filename=filename)
        logging.info(f"image saved: {full_path}")

        logging.info("script ended")


if __name__ == '__main__':
    main()
