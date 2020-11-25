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

def checkFreeNeighbors(pixels, x, y, radius, width, height):
    free_neighbors = []
    for nx in range(x - radius, x + radius + 1):
        for ny in range(y - radius, y + radius + 1):
            if nx >= 0 and nx < width and ny >= 0 and ny < height and (x, y) != (nx, ny):
                if not pixels[nx][ny]:
                    free_neighbors.append((nx, ny))

    return(free_neighbors)


def checkPopulatedNeighbors(pixels, x, y, radius, width, height):
    populated_neighbors = []
    for nx in range(x - radius, x + radius + 1):
        for ny in range(y - radius, y + radius + 1):
            if nx >= 0 and nx < width and ny >= 0 and ny < height and (x, y) != (nx, ny):
                if pixels[nx][ny]:
                    populated_neighbors.append(pixels[nx][ny])

    return populated_neighbors


def populatePixels(colors, pixels, width, height, step):
    started = datetime.now()
    placed_pixels = 0
    percent = 0
    last_percent = None

    min_dist_sq = step ** 2

    pixel_radius = 1
    image_size = width * height
    colors_len = len(colors)
    x, y = int(width/2), int(height/2) # pixel position
    cx, cy, cz = 0, 0, 0 # color coordinates

    backtrack_pixels = []
    while placed_pixels < image_size:
        if not pixels[x][y]:
            populated_neighbors = checkPopulatedNeighbors(pixels, x, y, pixel_radius, width, height)

            if len(populated_neighbors) > 0:
                average = [0 for x in range(3)]
                for a in range(3):
                    for p in populated_neighbors:
                        average[a] += p[a]
                    average[a] /= len(populated_neighbors)

                average_color = Color(average[0], average[1], average[2])

                shortest_dist_sq = None
                nx, ny, nz = 0, 0, 0 # new color coordinates

                color_picked = False
                search_size = 1

                searched = set()
                searched.add((cx, cy, cz))

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
                cx = nx
                cy = ny
                cz = nz

            else:
                nx, ny, nz = 0, 0, 0

            pixels[x][y] = colors[cx][cy][cz].RGB
            colors[cx][cy][cz] = None
            placed_pixels += 1
            backtrack_pixels.append((x, y))

        free_neighbors = checkFreeNeighbors(pixels, x, y, pixel_radius, width, height)
        if len(free_neighbors) > 1:
            next_position = random.choice(free_neighbors)
        elif len(free_neighbors) == 1:
            next_position = free_neighbors[0]
        else:
            random_index = random.randint(0, len(backtrack_pixels) - 1)
            next_position = backtrack_pixels.pop(random_index)

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
    color_bits = 18
    colors, step = generateColors(color_bits)
    width, height = calculateSize(len(colors))
    pixels = generateEmptyPixels(width, height)
    pixels = populatePixels(colors, pixels, width, height, step)
    im = generateImage(pixels, width, height)
    saveImage(im)


if __name__ == '__main__':
    main()
