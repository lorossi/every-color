# made by Lorenzo Rossi
# www.lorenzoros.si
# october 2020 - quarantine sucks! Milano zona rossa

import random
import logging
import argparse

from math import sqrt
from datetime import datetime
from PIL import Image


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
    colors = [[[None for blue in range(total_steps)]
              for green in range(total_steps)]
              for red in range(total_steps)]

    for red in range(0, total_steps):
        for green in range(0, total_steps):
            for blue in range(0, total_steps):
                # rgb values stored as a tuple
                new_color = (red * step, green * step, blue * step)
                colors[red][green][blue] = new_color
    return colors, step


# generates the empty 2d list that will contain the final image
def generate_empty_pixels(width, height):
    pixels = [[None for y in range(height)] for x in range(width)]
    return pixels


# check the average color of the neighbors
def check_neighbors_average(pixels, px, py, radius, width, height):
    average = [0, 0, 0]
    total_dist = 0

    # maximum distance of a pixel from the interesing pixel
    max_dist = radius * 2

    for i in range(px - radius, px + radius + 1):
        if i < 0 or i >= width:
            # out of boundaries
            continue

        for j in range(py - radius, py + radius + 1):
            if j < 0 or j >= height:
                # out of boundaries
                continue

            # we want to know the average of the pixels around the current
            # pixel so we skip it
            if (i, j) != (px, py):
                # if the pixel is colored...
                if pixels[i][j]:
                    # distance between (i, j) and (px, py)
                    dist = max_dist - (abs(i - px) + abs(j - py))
                    total_dist += dist
                    for value in range(3):
                        # weighted average
                        average[value] += pixels[i][j][value] * dist

    # if at least one has been found, we average
    if total_dist > 0:
        average = [a / total_dist for a in average]
    else:
        average = None

    return average


# find next suitable pixels
def find_next_pixels(pixels, px, py, width, height):
    next_pixels = []
    radius = 1

    for i in [px - radius, px + radius]:
        if i < 0 or i >= width:
            # out of boundaries
            continue

        if not pixels[i][py]:
            # this is a valid empty pixel
            next_pixels.append((i, py))

    for j in [py - radius, py + radius]:
        if j < 0 or j >= height:
            # out of boundaries
            continue

        if not pixels[px][j]:
            # this is a valid empty pixel
            next_pixels.append((px, j))

    return next_pixels


# squared distance of colors
def distance_sq(color1, color2):
    return (color1[0] - color2[0]) ** 2 + \
            (color1[1] - color2[1]) ** 2 + \
            (color1[2] - color2[2]) ** 2


# find the closest rgb color still available according to an average
def find_closest_color(c_x, c_y, c_z, colors, average_color, step):
    # the colors are provided in a cube
    # we proceed by gradually incrasing the cube radius to find the coordinates
    # of the most similar color. This saves A LOT of time (from ~10 hours to
    # ~5 minutes
    colors_len = len(colors)
    # initialize distances
    distances = [
                    abs(c_x - colors_len),
                    abs(c_y - colors_len),
                    abs(c_z - colors_len)
                 ]

    max_dist = max(distances)
    min_dist_sq = step ** 2

    color_picked = False
    search_size = 0
    shortest_dist_sq = None
    n_x, n_y, n_z = 0, 0, 0  # new color coordinates
    while not color_picked:
        for i in range(c_x - search_size, c_x + search_size + 1):
            # limit the index to the max size of the cube
            if i < 0:
                i = 0
            elif i >= colors_len:
                i = colors_len - 1
            for j in range(c_y - search_size, c_y + search_size + 1):
                # limit the index to the max size of the cube
                if j < 0:
                    j = 0
                elif j >= colors_len:
                    j = colors_len - 1
                for k in range(c_z - search_size, c_z + search_size + 1):
                    # limit the index to the max size of the cube
                    if k < 0:
                        k = 0
                    elif k >= colors_len:
                        k = colors_len - 1
                    # skip the current color
                    if (i, j, k) == (c_x, c_y, c_z):
                        continue
                    # skip if container is empty
                    if not colors[i][j][k]:
                        continue
                    # evaluate the squared distance
                    dist_sq = distance_sq(average_color, colors[i][j][k])
                    # if the distance is tles than the previous distance...
                    if not shortest_dist_sq or dist_sq <= shortest_dist_sq:
                        # new shortest distance
                        shortest_dist_sq = dist_sq
                        # if the distance is the least possible (1 step
                        # squared) orif the search radius is bigger than the
                        # color cube, it's time to return the closest color
                        # that has been found
                        if dist_sq <= min_dist_sq or search_size >= max_dist:
                            color_picked = True
                            n_x = i
                            n_y = j
                            n_z = k

        # increase search size
        search_size += 1
    return n_x, n_y, n_z


# populate the pixels container
def populate_pixels(start_position, start_color, colors, pixels, width, height,
                    step):

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

    logging.info("pixel placing started. "
                 "Warning: this script is fast at the beginning but very slow "
                 "as it goes on. Don't worry, just let it run.")

    # while not all the pixels have been placed
    while placed_pixels < image_size:
        # if this pixel has not been placed (only happens the first iteration)
        # color coordinates initalization
        c_x, c_y, c_z = 0, 0, 0
        if not pixels[x][y]:
            average_color = check_neighbors_average(pixels, x, y,
                                                    search_radius, width,
                                                    height)

            if average_color:
                c_x, c_y, c_z = find_closest_color(c_x, c_y, c_z, colors,
                                                   average_color, step)
            else:
                # this happens only when the program is first ran
                # starting color value
                if start_color == "white":
                    c_x = len(colors) - 1
                    c_y = len(colors) - 1
                    c_z = len(colors) - 1
                elif start_color == "black":
                    c_x = 0
                    c_y = 0
                    c_z = 0
                elif start_color == "random":
                    c_x = random.randint(0, len(colors) - 1)
                    c_y = random.randint(0, len(colors) - 1)
                    c_z = random.randint(0, len(colors) - 1)

            # set the current pixel with the new color
            pixels[x][y] = colors[c_x][c_y][c_z]
            # delete color from colors cube
            colors[c_x][c_y][c_z] = None
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
                next_position = backtrack_pixels.pop(0)
            else:
                # otherwise, pick a pixel from the queue (randomly, as it is
                # shuffled when generated)
                next_position = pixels_queue.pop(0)

            # update coords to next position
            x = next_position[0]
            y = next_position[1]

        # update percent
        percent = int(placed_pixels / image_size * 100)
        if percent != last_percent:
            # update last percent value
            last_percent = percent
            # calculate elapsed time
            elapsed_seconds = int((datetime.now() - started).total_seconds())
            elapsed_minutes = int(elapsed_seconds / 60)
            elapsed_hours = int(elapsed_minutes / 60)
            # string that will be logged
            log_string = f"Progress: {percent}%, elapsed: "
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
def generate_image(pixels, width, height):
    im = Image.new("RGB", (width, height))
    # loop throught pixels list
    for x in range(width):
        for y in range(height):
            im.putpixel((x, y), pixels[x][y])
    return im


# save image to file
def saveImage(image, path="", filename="everycolor"):
    full_path = f"{path}{filename}.png"
    image.save(full_path)
    return full_path


def main():
    # arguments parsing
    parser = argparse.ArgumentParser(description="Generate an image with all"
                                     " the possible colors in the RGB"
                                     " colorspace")

    parser.add_argument("-b", "--bits", type=int, help="image depth bits"
                        " (defaults to 15)", default=15)
    parser.add_argument("-n", "--number", type=int, help="number of images to"
                        " generate (defaults to 1)", default=1)
    parser.add_argument("-p", "--startposition", action="store",
                        choices=["center", "corner", "random"],
                        default="random",
                        help="location of the first bit (defaults to random)")
    parser.add_argument("-c", "--startcolor", action="store",
                        choices=["white", "black", "random"], default="random",
                        help="color of the first bit (defaults to center)")
    parser.add_argument("-o", "--output", type=str, default="output/",
                        help="output path (defaults to output/) make sure that"
                        " the path exists")
    parser.add_argument("-l", "--log", action="store",
                        choices=["file", "console"], default="file",
                        help="log destination (defaults to file)")
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
        logging.info("started generating image %s/%s", x+1, images_to_generate)
        # random seeding
        random.seed(datetime.now())
        # filename generation
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{now}-every-color"
        path = args.output
        logging.info("basic setup completed, generating image with %s bits",
                     color_bits)

        colors, step = generate_colors(color_bits)
        logging.info("colors generated")

        width, height = calculate_size(len(colors))
        logging.info("size calculated, generating a %s by %s image",
                     width, height)

        pixels = generate_empty_pixels(width, height)
        logging.info("empty pixels container generated")

        start_position = args.startposition
        start_color = args.startcolor
        pixels, seconds = populate_pixels(start_position, start_color, colors,
                                          pixels, width, height, step)
        logging.info("pixel placing completed! It took %s seconds", seconds)

        im = generate_image(pixels, width, height)
        logging.info("image generated")

        full_path = saveImage(im, path=path, filename=filename)
        logging.info("image saved: %s", full_path)

        logging.info("script ended")


if __name__ == '__main__':
    main()
