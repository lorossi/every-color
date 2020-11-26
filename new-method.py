from math import sqrt
import random
from PIL import Image

class Pixel:
    def __init__(self, x=None, y=None):
        self.__x = x
        self.__y = y

    def __eq__(self, other):
        return self.__x == other.x and self.__y == other.y

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    @property
    def pos(self):
        return (self.__x, self.__y)


def generate_colors(bits):
    colors = []
    step = int(256 / (2 ** (bits / 3)))
    total_steps = int(256/step)

    for r in range(0, total_steps):
        for g in range(0, total_steps):
            for b in range(0, total_steps):
                # rgb values stored as a tuple
                new_color = (r * step, g * step, b * step)
                colors.append(new_color)

    return colors


def calculate_size(grid):
    if sqrt(grid).is_integer():
        # if the image is a square
        width = int(sqrt(grid))
        height = int(sqrt(grid))
    else:
        # in case the image is not a square
        height = int(sqrt(grid / 2))
        width = int(grid / height)
    return width, height


def generate_grid(width, height):
    grid = [[None for y in range(height)] for x in range(width)]
    return grid


def color_difference(color1, color2):
    return (color1[0] - color2[0]) ** 2 + \
           (color1[1] - color2[1]) ** 2 + \
           (color1[2] - color2[2]) ** 2

def find_free_neighbors(grid, pixel):
    free_neighbors = []

    width = len(grid)
    height = len(grid[0])

    for px in range(pixel.x - 1, pixel.x + 2):
        if px >= width or px < 0:
            continue
        for py in range(pixel.y - 1, pixel.y + 2):
            if py >= height or py < 0:
                continue
            if pixel.pos == (px, py):
                continue
            if not grid[px][py]:
                free_neighbors.append(Pixel(px, py))

    return free_neighbors

def calculate_diff(grid, pixel, color):
    diffs = []
    width = len(grid)
    height = len(grid[0])

    for px in range(pixel.x - 1, pixel.x + 2):
        if px >= width or px < 0:
            continue
        for py in range(pixel.y - 1, pixel.y + 2):
            if py >= height or py < 0:
                continue
            if pixel.pos == (px, py):
                continue
            if grid[px][py]:
                diffs.append(color_difference(grid[px][py], color))

    return min(diffs)


def place_pixels(grid, colors):
    width = len(grid)
    height = len(grid[0])
    available_pixels = []

    best_pixel = Pixel()
    random.shuffle(colors)

    for c in colors:
        if len(available_pixels) == 0:
            best_pixel = Pixel(0, 0)
            available_pixels.append(best_pixel)
        else:
            best_pixel = sorted(available_pixels, key=lambda p: calculate_diff(grid, p, c))[0]

        grid[best_pixel.x][best_pixel.y] = c

        new_available_pixels = find_free_neighbors(grid, best_pixel)
        for n in new_available_pixels:
            if n not in available_pixels:
                available_pixels.append(n)
        available_pixels.remove(best_pixel)

    return grid

# generates the image by dumping the grid into a png
def generate_image(grid, default_color=(0, 0, 0)):
    width = len(grid)
    height = len(grid[0])
    image = Image.new("RGB", (width, height))
    # loop throught grid list
    for x in range(width):
        for y in range(height):
            if not grid[x][y]:
                #print(x, y, "empty")
                grid[x][y] = default_color

            image.putpixel((x, y), grid[x][y])
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
    bits = 15
    colors = generate_colors(bits)
    width, height = calculate_size(len(colors))
    grid = generate_grid(width, height)
    colored_grid = place_pixels(grid, colors)
    image = generate_image(colored_grid)
    save_image(image)

if __name__ == "__main__":
    main()
