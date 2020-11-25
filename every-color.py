import random
import time
from datetime import datetime
from PIL import Image
from math import sqrt


def calculateSize(colors):
    if sqrt(colors ** 3).is_integer():
        width = int(sqrt(colors ** 3))
        height = int(sqrt(colors ** 3))

    else:
        width = 256
        height = 128
    return width, height

def generateColors(bits):
    step = int(256 / ( 2 ** (bits / 3)))
    total_steps = int(256/step)
    colors = [[ [None for b in range(total_steps)] for h in range(total_steps)] for r in range(total_steps)]

    for r in range(0, total_steps):
        for g in range(0, total_steps):
            for b in range(0, total_steps):
                new_color = (r * step, g * step, b * step)
                colors[r][g][b] = new_color
    return colors, step

def generateEmptyPixels(width, height):
    pixels = [[None for y in range(height)] for x in range(width)]
    return pixels

def checkFreeNeighbors(pixels, x, y, width, height):
    free_neighbors = []
    for i in [x-1, x+1]:
        if i < 0: i = 0
        elif i >= width: i = width - 1
        free_neighbors.append((i, y))

    for j in [y-1, y+1]:
        if j < 0: j = 0
        elif j >= height: j = height - 1
        free_neighbors.append((x, j))

    return free_neighbors


def checkNeighborsAverage(pixels, x, y, width, height):
    average = [0, 0, 0]
    total_dist = 0
    radius = 5
    found = 0
    searched = []
    searched.append((x, y))

    for i in range(x - radius, x + radius + 1):
        if i < 0 or i >= width:
            continue

        for j in range(y - radius, y + radius + 1):
            if j < 0 or j >= height:
                continue

            if (i, j) not in searched:
                if pixels[i][j]:
                    for p in range(3):
                        average[p] += pixels[i][j][p]
                        found += 1
                searched.append((x, y))

    if found > 0:
        average = [a / found for a in average]
    else:
        average = None

    return average


def findNextPixels(pixels, x, y, width, height):
    next = []
    radius = 1

    for i in [x - radius, x + radius]:
        if i < 0 or i >= width:
            continue

        if not pixels[i][y]:
            next.append((i, y))

    for j in [y - radius, y + radius]:
        if j < 0 or j >= height:
            continue

        if not pixels[x][j]:
            next.append((x, j))

    return next


def distanceSq(color1, color2):
    return (color1[0] - color2[0]) ** 2 +  (color1[1] - color2[1]) ** 2 +  (color1[2] - color2[2]) ** 2


def findClosestColor(pixels, cx, cy, cz, colors, average_color, width, height):
    colors_len = len(colors)
    searched = set()
    searched.add((cx, cy, cz))

    color_picked = False
    search_size = 1
    shortest_dist_sq = None
    nx, ny, nz = 0, 0, 0 # new color coordinates
    while not color_picked:
        for i in range(cx - search_size, cx + search_size + 1):
            if i < 0: i = 0
            elif i >= colors_len: i = colors_len - 1
            for j in range(cy - search_size, cy + search_size + 1):
                if j < 0: j = 0
                elif j >= colors_len: j = colors_len - 1
                for k in range(cz - search_size, cz + search_size + 1):
                    if k < 0: k = 0
                    elif k >= colors_len: k = colors_len - 1
                    if (i, j, k) not in searched and colors[i][j][k]:
                        searched.add((i, j, k))
                        dist_sq = distanceSq(average_color, colors[i][j][k])
                        if not shortest_dist_sq or dist_sq <= shortest_dist_sq:
                            shortest_dist_sq = dist_sq
                            nx = i
                            ny = j
                            nz = k
                            color_picked = True

            search_size += 1
    return nx, ny, nz


def populatePixels(colors, pixels, width, height, step):
    started = datetime.now()

    placed_pixels = 0
    percent = 0
    last_percent = None
    image_size = width * height
    x, y = random.randint(0, width - 1),  random.randint(0, height - 1) # pixel position

    pixels_queue = []
    backtrack_pixels = []

    while placed_pixels < image_size:
        if not pixels[x][y]:
            average_color = checkNeighborsAverage(pixels, x, y, width, height)
            if average_color:
                cx, cy, cz = findClosestColor(pixels, cx, cy, cz, colors, average_color, width, height)
            else:
                # this happens only when the program is first ran
                cx = random.randint(0, len(colors) - 1)
                cy = random.randint(0, len(colors) - 1)
                cz = random.randint(0, len(colors) - 1)

            pixels[x][y] = colors[cx][cy][cz]
            colors[cx][cy][cz] = None
            backtrack_pixels.append((x, y))
            placed_pixels += 1

        if placed_pixels == image_size: # THIS IS SO FUCKING UGLY I CAN'T EVEN
            break

        if len(pixels_queue) == 0:
            pixels_queue = findNextPixels(pixels, x, y, width, height)
            random.shuffle(pixels_queue)

        if not pixels_queue:
            next_position = backtrack_pixels.pop(0)
        else:
            next_position = pixels_queue.pop(0)

        x = next_position[0]
        y = next_position[1]

        percent = int(placed_pixels / image_size * 100)
        if percent != last_percent:
            last_percent = percent

            if percent == 0:
                print(f"Started selecting pixels")
            else:
                elapsed_seconds = int((datetime.now() - started).total_seconds())
                elapsed_minutes = int(elapsed_seconds / 60)
                elapsed_hours = int(elapsed_minutes / 60)

                total = 100 / percent * elapsed_seconds
                remaining_seconds = int(total - elapsed_seconds)
                remaining_minutes = int(remaining_seconds / 60)
                remaining_hours = int(remaining_minutes / 60)

                print(f"Progress: {percent}%, elapsed: ", end="")
                if elapsed_hours > 0:
                    print(f"{elapsed_hours} hours", end="")
                elif elapsed_minutes > 0:
                    print(f"{elapsed_minutes} minutes", end="")
                else:
                    print(f"{elapsed_seconds} seconds", end="")

                print(", remaining: ", end="")
                if remaining_hours > 0:
                    print(f"{remaining_hours} hours")
                elif remaining_minutes > 0:
                    print(f"{remaining_minutes} minutes")
                else:
                    print(f"{remaining_seconds} seconds")

    elapsed_seconds = int((datetime.now() - started).total_seconds())

    print(f"Completed! It took {elapsed_seconds} seconds")

    return pixels

def generateImage(pixels, width, height):
    im = Image.new("RGB", (width, height))

    for x in range(width):
        for y in range(height):
            im.putpixel((x, y), pixels[x][y])
    return im

def saveImage(image, path="", filename="everycolor"):
    image.save(f"{path}{filename}.png")


def main():
    color_bits = 18
    colors, step = generateColors(color_bits)
    width, height = calculateSize(len(colors))
    pixels = generateEmptyPixels(width, height)
    pixels = populatePixels(colors, pixels, width, height, step)
    im = generateImage(pixels, width, height)
    saveImage(im)


if __name__ == '__main__':
    main()
