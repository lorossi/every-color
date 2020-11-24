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


    def distance(self, other):
        #https://stackoverflow.com/questions/5392061/algorithm-to-check-similarity-of-colors
        """ C CODE:
        double ColourDistance(RGB e1, RGB e2)
        {
          long rmean = ( (long)e1.r + (long)e2.r ) / 2;
          long r = (long)e1.r - (long)e2.r;
          long g = (long)e1.g - (long)e2.g;
          long b = (long)e1.b - (long)e2.b;
          return sqrt((((512+rmean)*r*r)>>8) + 4*g*g + (((767-rmean)*b*b)>>8));
        }
        """

        rmean = (self.r + other.r) / 2
        r = self.r - other.r
        g = self.g - other.g
        b = self.b - other.b
        return sqrt(( int((512+rmean)*r*r)>>8) + 4*g*g + ( int((767-rmean)*b*b)>>8))

    @property
    def RGB(self):
        return self.RGBtuple

    @property
    def hue(self):
        return self.h


def generateColors(bit_depth):
    colors = []
    step = int(256 / (2 ** bit_depth))
    for r in range(0, 255, step):
        for g in range(0, 255, step):
            for b in range(0, 255, step):
                new_color = Color(r, g, b)
                colors.append(new_color)

    return colors

def generateEmptyPixels(side_length):
    pixels = [[None for x in range(side_length)] for y in range(side_length)]
    return pixels

def checkFreeNeighbors(pixels, x, y, radius):
    side_length = len(pixels)
    free_neighbors = []
    for nx in range(x - radius, x + radius + 1):
        for ny in range(y - radius, y + radius + 1):
            if nx >= 0 and nx < side_length and ny >= 0 and ny < side_length and (x, y) != (nx, ny):
                if not pixels[nx][ny]:
                    free_neighbors.append((nx, ny))

    return(free_neighbors)


def checkPopulatedNeighbors(pixels, x, y, radius):
    side_length = len(pixels)
    populated_neighbors = []
    for nx in range(x - radius, x + radius + 1):
        for ny in range(y - radius, y + radius + 1):
            if nx >= 0 and nx < side_length and ny >= 0 and ny < side_length and (x, y) != (nx, ny):
                if pixels[nx][ny]:
                    populated_neighbors.append(pixels[nx][ny])

    return populated_neighbors


def populatePixels(colors, pixels):
    started = datetime.now()
    placed_pixels = 0
    percent = 0
    last_percent = 0

    max_hue_diff = 1
    side_length = len(pixels)
    image_size =  side_length ** 2
    starting_pixel = int(side_length / 2)
    x, y = starting_pixel, starting_pixel

    #candidate_pixels = []
    backtrack_pixels = []
    random.shuffle(colors)

    while len(colors) > 0:
        if not pixels[x][y]:
            populated_neighbors = checkPopulatedNeighbors(pixels, x, y, 1)

            color_index = 0
            if len(populated_neighbors) > 0:
                average = [sum(x) for x in zip(*populated_neighbors)]
                average = [a / len(populated_neighbors) for a in average]
                average_color = Color(average[0], average[1], average[2])
                average_hue = average_color.hue
                lower_dist_sq = None

                for i in range(len(colors)):
                    hues_diff = abs(colors[i].hue - average_hue)
                    if hues_diff > max_hue_diff:
                        continue

                    distance_sq = colors[i].distance(average_color)
                    if not lower_dist_sq or distance_sq < lower_dist_sq:
                        color_index = i
                        lower_dist_sq = distance_sq

            pixels[x][y] = colors.pop(color_index).RGB
            placed_pixels += 1
            backtrack_pixels.insert(0, (x, y))

        free_neighbors = checkFreeNeighbors(pixels, x, y, 1)
        if len(free_neighbors) > 0:
            next_position = free_neighbors[0]
            x = next_position[0]
            y = next_position[1]

        else:
            next_position = backtrack_pixels.pop(0)
            x = next_position[0]
            y = next_position[1]


        percent = round(placed_pixels / image_size * 100, 2)
        if percent != last_percent:
            last_percent = percent
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
    side = len(pixels)
    im = Image.new("RGB", (side, side))

    for x in range(side):
        for y in range(side):
            if not pixels[x][y]:
                pixels[x][y] = (0, 0, 0)

            im.putpixel((x, y), pixels[x][y])
    return im

def saveImage(image, path="", filename="everycolor"):
    image.save(f"{path}{filename}.png")


def main():
    bit_depth = 6

    colors = generateColors(bit_depth)
    side_length = int(sqrt(len(colors)))
    pixels = generateEmptyPixels(side_length)
    pixels = populatePixels(colors, pixels)
    im = generateImage(pixels)
    saveImage(im)




if __name__ == '__main__':
    main()
