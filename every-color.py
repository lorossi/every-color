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
    if sqrt(colors).is_integer():
        width = int(sqrt(colors))
        height = int(sqrt(colors))

    else:
        width = 256
        height = 128
    return width, height

def generateColors(bit_depth):
    colors = []
    step = int(256 / ( 2 ** (bit_depth / 3)))

    for r in range(0, 256, step):
        for g in range(0, 256, step):
            for b in range(0, 256, step):
                new_color = Color(r, g, b)
                colors.append(new_color)
    print(len(colors))
    return colors

def generateEmptyPixels(width, height):
    pixels = [[None for y in range(height)] for x in range(width)]
    return pixels

def checkFreeNeighbors(pixels, x, y, radius):
    width = len(pixels)
    height = len(pixels[0])

    free_neighbors = []
    for nx in range(x - radius, x + radius + 1):
        for ny in range(y - radius, y + radius + 1):
            if nx >= 0 and nx < width and ny >= 0 and ny < height and (x, y) != (nx, ny):
                if not pixels[nx][ny]:
                    free_neighbors.append((nx, ny))

    return(free_neighbors)


def checkPopulatedNeighbors(pixels, x, y, radius):
    width = len(pixels)
    height = len(pixels[0])

    populated_neighbors = []
    for nx in range(x - radius, x + radius + 1):
        for ny in range(y - radius, y + radius + 1):
            if nx >= 0 and nx < width and ny >= 0 and ny < height and (x, y) != (nx, ny):
                if pixels[nx][ny]:
                    populated_neighbors.append(pixels[nx][ny])

    return populated_neighbors


def populatePixels(colors, pixels):
    started = datetime.now()
    placed_pixels = 0
    percent = 0
    last_percent = None

    pixel_radius = 1
    max_diff = 180

    width = len(pixels)
    height = len(pixels[0])
    image_size = width * height

    x, y = int(width/2), int(height/2)

    backtrack_pixels = []
    #free_pixels = [(x, y) for x in range(width) for y in range(height)]

    random.shuffle(colors)
    while len(colors) > 0:
        if not pixels[x][y]:
            populated_neighbors = checkPopulatedNeighbors(pixels, x, y, pixel_radius)

            if len(populated_neighbors) > 0:
                average = [0 for x in range(3)]
                for a in range(3):
                    for p in populated_neighbors:
                        average[a] += p[a]
                    average[a] /= len(populated_neighbors)

                average_color = Color(average[0], average[1], average[2])
                average_hue = average_color.hue
                lower_dist_sq = None
                color_index = 0

                for i in range(len(colors)):
                    current_color = colors[i]
                    """diff = average_hue - current_color.hue
                    if diff > max_diff or diff < -max_diff:
                        continue"""

                    distance_sq = average_color.distanceSq(current_color)
                    if not lower_dist_sq or distance_sq < lower_dist_sq:
                        color_index = i
                        lower_dist_sq = distance_sq

                if (lower_dist_sq == None): print("WTF", len(colors))

            else:
                color_index = 0

            pixels[x][y] = colors.pop(color_index).RGB
            placed_pixels += 1
            backtrack_pixels.append((x, y))
            #free_pixels.remove((x, y))

        free_neighbors = checkFreeNeighbors(pixels, x, y, pixel_radius)
        if len(free_neighbors) > 0:
            next_position = random.choice(free_neighbors)
            x = next_position[0]
            y = next_position[1]

        else:
            #backtrack_index = random.randint(0, len(backtrack_pixels) - 1)
            #next_position = backtrack_pixels.pop(backtrack_index)

            next_position = backtrack_pixels.pop(-1)
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

def generateImage(pixels):
    width = len(pixels)
    height = len(pixels[0])
    im = Image.new("RGB", (width, height))

    for x in range(width):
        for y in range(height):
            if not pixels[x][y]:
                pixels[x][y] = (0, 0, 0)
                print("pixel", x, y, "is empty")
            im.putpixel((x, y), pixels[x][y])
    return im

def saveImage(image, path="", filename="everycolor"):
    image.save(f"{path}{filename}.png")


def main():
    color_bits = 15
    colors = generateColors(color_bits)
    width, height = calculateSize(len(colors))
    pixels = generateEmptyPixels(width, height)
    pixels = populatePixels(colors, pixels)
    im = generateImage(pixels)
    saveImage(im)




if __name__ == '__main__':
    main()
