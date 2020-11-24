import random
import time
from PIL import Image
from math import sqrt


class Color:
    def __init__(self):

        return

    def setRGB(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.RGBstring = f"#{hex(int(r))[2:]}{hex(int(g))[2:]}{hex(int(b))[2:]}"
        self.RGBtuple = (r, g, b)
        self.__calculateHSV()

    def distance(self, other):
        return sqrt( (self.r - other.r) ** 2 + (self.g - other.g) ** 2 + (self.b - other.b) ** 2 )

    def distanceSq(self, other):
        return (self.r - other.r) ** 2 + (self.g - other.g) ** 2 + (self.b - other.b) ** 2

    def __calculateHSV(self):
        r = self.r / 255
        g = self.r / 255
        b = self.r / 255

        cmax = max(r, max(g, b))
        cmin = min(r, min(g, b))
        diff = cmax - cmin
        if cmax == cmin:
            self.h = 0
        elif cmax == r:
            self.h = (60 * ((g - b) / diff) + 360) % 360
        elif cmax == g:
            self.h = (60 * ((b - r) / diff) + 120) % 360
        elif cmax == b:
            self.h = (60 * ((r - g) / diff) + 240) % 360

        if cmax == 0:
            self.s = 0
        else:
            self.s = (diff / cmax) * 100

        self.v = cmax * 100


    @property
    def RGB(self):
        return self.RGBtuple

    def RGBstring(self):
        return self.RBGstring


def generateColors(bit_depth):
    colors = []
    step = int(256 / (2 ** bit_depth))
    for r in range(0, 255, step):
        for g in range(0, 255, step):
            for b in range(0, 255, step):
                new_color = Color()
                new_color.setRGB(r, g, b)
                colors.append(new_color)
    return colors

def generateEmptyPixels(side_length):
    pixels = [[None for x in range(side_length)] for y in range(side_length)]
    return pixels

def populatePixels(colors, pixels, max_distance_sq):
    side_length = len(pixels)
    starting_pixel = int(side_length / 2)
    x, y = starting_pixel, starting_pixel

    random.shuffle(colors)
    pixels[x][y] = colors[0].RGB
    colors.pop(0)

    while len(colors) > 0:
        pixel_neighbors = []
        available_pixels = []
        for nx in range(x-1, x+1):
            for ny in range(y-1, y+1):
                if nx >= 0 and nx < side_length and ny > 0 and ny <= side_length:
                    if pixels[nx][ny] != None:
                        pixel_neighbors.append(pixels[nx][ny])
                    else:
                        available_pixels.append([nx, ny])

        average = [0 for a in range(3)]

        if len(pixel_neighbors) > 0:
            for p in pixel_neighbors:
                for a in range(3):
                    average[a] += p[a]

            for a in range(3):
                average[a] /= len(pixel_neighbors)

        average_color = Color()
        average_color.setRGB(average[0], average[1], average[2])

        try_colors = colors.copy()
        color_chosen = False
        for c in try_colors:
            if c.distanceSq(average_color) < max_distance_sq:
                pixels[x][y] = c.RGB
                colors.remove(c)
                print(len(colors), x, y)
                color_chosen = True
                break

        position_chosen = False
        if color_chosen:
            if len(available_pixels) > 0:
                next_position = random.choice(available_pixels)
                x = next_position[0]
                y = next_position[1]
            else:
                position_chosen = False

        if not position_chosen or not color_chosen:
            picked = False
            while not picked:
                x = random.randint(0, side_length - 1)
                y = random.randint(0, side_length - 1)
                if not pixels[x][y]:
                    picked = True
                    break

    return pixels

def generateImage(pixels, image_mode):
    side = len(pixels)
    im = Image.new(image_mode, (side, side))

    for x in range(side):
        for y in range(side):
            if not pixels[x][y]:
                pixels[x][y] = (0, 0, 0)
            #print(pixels[x][y])
            im.putpixel((x, y), pixels[x][y])

    return im

def main():
    bit_depth = 4
    max_distance_sq = 50 ** 2
    image_mode = "RGB"

    colors = generateColors(bit_depth)
    side_length = int(sqrt(len(colors)))
    pixels = generateEmptyPixels(side_length)
    pixels = populatePixels(colors, pixels, max_distance_sq)
    im = generateImage(pixels, image_mode)
    im.show()


if __name__ == '__main__':
    main()
