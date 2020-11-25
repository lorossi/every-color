import random
import time
from datetime import datetime
from PIL import Image
from math import sqrt


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.RGBtuple = (r, g, b)
        self.RBGlist = [r, g, b]
        self.HSVtuple = self.__calculateHSV()

    def __calculateHSV(self):
        r = self.r / 255.0;
        g = self.g / 255.0;
        b = self.b / 255.0;

        cmax = max(r, max(g, b));
        cmin = min(r, min(g, b));
        diff = cmax - cmin;

        if cmax == cmin:
            self.h = 0

        elif cmax == r:
            self.h = (60 * ((g - b) / diff) + 360) % 360;

        elif cmax == g:
            self.h = (60 * ((b - r) / diff) + 120) % 360;

        elif cmax == b:
            self.h = (60 * ((r - g) / diff) + 240) % 360;


        if cmax == 0:
            self.s = 0;
        else:
            self.s = (diff / cmax) * 100;

        self.v = cmax * 100
        return (self.h, self.s, self.v)


    def distance(self, other):
        return sqrt( (self.r - other.r) ** 2 + (self.g - other.g) ** 2 + (self.b - other.b) ** 2 )


    def distanceSq(self, other):
        return (self.r - other.r) ** 2 + (self.g - other.g) ** 2 + (self.b - other.b) ** 2


    @property
    def RGB(self):
        return self.RGBtuple


    @property
    def hue(self):
        return self.h

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
                new_color = Color(r * step, g * step, b * step)
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
                        dist_sq = average_color.distanceSq(colors[i][j][k])
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
    place_radius = 0
    image_size = width * height
    x, y = int(width/2), int(height/2) # pixel position

    pixels_queue = []
    backtrack_pixels = []

    while placed_pixels < image_size:
        if not pixels[x][y]:
            average = checkNeighborsAverage(pixels, x, y, width, height)
            if average:
                average_color = Color(average[0], average[1], average[2])
                cx, cy, cz = findClosestColor(pixels, cx, cy, cz, colors, average_color, width, height)
            else:
                cx = 0
                cy = 0
                cz = 0

            pixels[x][y] = colors[cx][cy][cz].RGB
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
    elapsed_minutes = int(elapsed_seconds / 60)
    elapsed_hours = int(elapsed_minutes / 60)

    print("Completed! It took ", end="")
    if elapsed_hours > 0:
        print(f"{elapsed_hours} hours")
    elif elapsed_minutes > 0:
        print(f"{elapsed_minutes} minutes")
    else:
        print(f"{elapsed_seconds} seconds")

    return pixels

def generateImage(pixels, width, height):
    im = Image.new("RGB", (width, height))

    for x in range(width):
        for y in range(height):
            if not pixels[x][y]:
                pixels[x][y] = (0, 0, 0)
                print("pixel", x, y, "is empty")
            #else:
                #print(pixels[x][y])
            im.putpixel((x, y), pixels[x][y])
    return im

def saveImage(image, path="", filename="everycolor"):
    image.save(f"{path}{filename}.png")


def main():
    color_bits = 15
    colors, step = generateColors(color_bits)
    width, height = calculateSize(len(colors))
    pixels = generateEmptyPixels(width, height)
    pixels = populatePixels(colors, pixels, width, height, step)
    im = generateImage(pixels, width, height)
    saveImage(im)


if __name__ == '__main__':
    main()
