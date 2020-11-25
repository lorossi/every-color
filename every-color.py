import random
import time
from datetime import datetime
from PIL import Image
from math import sqrt


# calculates the size of the finale image according to the number of colors
def calculateSize(colors):
    # as long as the number of color makes sense, this will work
    if sqrt(colors ** 3).is_integer():
        width = int(sqrt(colors ** 3))
        height = int(sqrt(colors ** 3))
    else:
        # this is cheaty but it works
        width = 256
        height = 128
    return width, height


# generates the colors that will be used in the image. The number are stored
#   in a cubic array in order to increase the speed of the lookups
def generateColors(bits):
    # length of the for step
    step = int(256 / ( 2 ** (bits / 3)))
    # total number of for steps
    total_steps = int(256/step)
    # generate an empty 3d list
    colors = [[ [None for b in range(total_steps)] for h in range(total_steps)] for r in range(total_steps)]

    for r in range(0, total_steps):
        for g in range(0, total_steps):
            for b in range(0, total_steps):
                # rgb values stored as a tuple
                new_color = (r * step, g * step, b * step)
                colors[r][g][b] = new_color
    return colors, step


# generates the empty 2d list that will contain the final image
def generateEmptyPixels(width, height):
    pixels = [[None for y in range(height)] for x in range(width)]
    return pixels


# check the average color of the neighbors
def checkNeighborsAverage(pixels, x, y, radius, width, height):
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
def findNextPixels(pixels, x, y, width, height):
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
def distanceSq(color1, color2):
    return (color1[0] - color2[0]) ** 2 +  (color1[1] - color2[1]) ** 2 +  (color1[2] - color2[2]) ** 2


# find the closest rgb color still available according to an average
def findClosestColor(pixels, cx, cy, cz, colors, average_color, width, height, step):
    # the colors are provided in a cube
    # we proceed by gradually incrasing the cube radius to find the coordinates
    # of the most similar color. This saves A LOT of time (from ~10 hours to
    # ~5 minutes


    colors_len = len(colors)
    distances = [abs(cx - colors_len), abs(cy - colors_len), abs(cz - colors_len)]
    max_dist = max(distances)
    least_possible_sq_distance = step ** 2

    color_picked = False
    search_size = 0
    shortest_dist_sq = None
    nx, ny, nz = 0, 0, 0 # new color coordinates
    while not color_picked:
        for i in range(cx - search_size, cx + search_size + 1):
            # limit the index to the max size of the cube
            if i < 0: i = 0
            elif i >= colors_len: i = colors_len - 1
            for j in range(cy - search_size, cy + search_size + 1):
                # limit the index to the max size of the cube
                if j < 0: j = 0
                elif j >= colors_len: j = colors_len - 1
                for k in range(cz - search_size, cz + search_size + 1):
                    # limit the index to the max size of the cube
                    if k < 0: k = 0
                    elif k >= colors_len: k = colors_len - 1
                    # skip the current color
                    if (i, j, k) != (cx, cy, cz) and colors[i][j][k]:
                        # evaluate the squared distance
                        dist_sq = distanceSq(average_color, colors[i][j][k])
                        # if the distance is tles than the previous distance...
                        if not shortest_dist_sq or dist_sq <= shortest_dist_sq:
                            # new shortest distance
                            shortest_dist_sq = dist_sq
                            # if the distance is the least possible (1 step) or
                            # if the search radius is bigger than the color cuube,
                            # it's time to return the closest color found
                            if dist_sq <= least_possible_sq_distance or search_size >= max_dist:
                                color_picked = True
                                nx = i
                                ny = j
                                nz = k

        # increase search size
        search_size += 1
    return nx, ny, nz


# populate the pixels container
def populatePixels(colors, pixels, width, height, step):
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
    x, y = random.randint(0, width - 1),  random.randint(0, height - 1)

    # pixels to be filled
    pixels_queue = []
    # past filled pixels
    backtrack_pixels = []

    print("Pixel placing started. Warning: this script is fast at the beginning but very slow at the end. Don't worry, let it run")
    # while not all the pixels have been placed
    while placed_pixels < image_size:
        # if this pixel has not been placed (only happens the first iteration)
        if not pixels[x][y]:
            average_color = checkNeighborsAverage(pixels, x, y, search_radius, width, height)
            if average_color:
                cx, cy, cz = findClosestColor(pixels, cx, cy, cz, colors, average_color, step, width, height)
            else:
                # this happens only when the program is first ran
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

        # this is ugly...
        if placed_pixels <= image_size:
            # check if we have pixels still inside the queue
            if len(pixels_queue) == 0:
                # if we don't, find the possible pixels
                pixels_queue = findNextPixels(pixels, x, y, width, height)
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
            percent = int(placed_pixels / image_size * 100)
            if percent != last_percent:
                # update last percent value
                last_percent = percent
                # calculate elapsed time
                elapsed_seconds = int((datetime.now() - started).total_seconds())
                elapsed_minutes = int(elapsed_seconds / 60)
                elapsed_hours = int(elapsed_minutes / 60)

                print(f"Progress: {percent}%, elapsed: ", end="")

                if elapsed_hours > 0:
                    print(f"{elapsed_hours} hours")
                elif elapsed_minutes > 0:
                    print(f"{elapsed_minutes} minutes")
                else:
                    print(f"{elapsed_seconds} seconds")

    # total elapsed time
    elapsed_seconds = int((datetime.now() - started).total_seconds())
    # yay we finished!
    print(f"Completed! It took {elapsed_seconds} seconds")

    return pixels


# generates the image by dumping the pixels into a png
def generateImage(pixels, width, height):
    im = Image.new("RGB", (width, height))
    # loop throught pixels list
    for x in range(width):
        for y in range(height):
            im.putpixel((x, y), pixels[x][y])
    return im


# save image to file
def saveImage(image, path="", filename="everycolor"):
    image.save(f"{path}{filename}.png")


def main():
    # color depth
    color_bits = 15
    colors, step = generateColors(color_bits)
    width, height = calculateSize(len(colors))
    pixels = generateEmptyPixels(width, height)
    pixels = populatePixels(colors, pixels, width, height, step)
    im = generateImage(pixels, width, height)
    saveImage(im)


if __name__ == '__main__':
    main()
