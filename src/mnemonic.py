from typing import Tuple, Union, List
from ascii_magic import AsciiArt
from PIL import Image
from hashlib import sha3_256
import ascii_magic
import itertools
import random
import matplotlib
from perlin_noise import PerlinNoise


class RandomImageGenerator:
    def __init__(self):
        self._rnd = random.Random()
        self._noises = []
        self._noise_depth = 0
        self._size = (0, 0)
        self._pixels = []
        self._visited = 0
        self._path = []
        self._colormap = ""
        self._start_pos = 0, 0

    def prepare(self, seed: int, size: Tuple[int, int]) -> None:
        self._rnd.seed(seed)
        octaves = sorted(
            [self._rnd.randint(1, 7) for _ in range(self._rnd.randint(1, 5))]
        )
        self._noises = [PerlinNoise(seed=seed, octaves=octave) for octave in octaves]
        self._noise_depth = self._rnd.randint(1, len(self._noises))
        self._pixels = []
        self._visited = 0
        self._path = []
        width, height = size
        self._start_pos = self._rnd.randint(0, width - 1), self._rnd.randint(
            0, height - 1
        )
        colormaps = [
            "viridis",
            "plasma",
            "inferno",
            "magma",
            "cividis",
            "Greys",
            "Purples",
            "Blues",
            "Greens",
            "Oranges",
            "Reds",
            "YlOrBr",
            "YlOrRd",
            "OrRd",
            "PuRd",
            "RdPu",
            "BuPu",
            "GnBu",
            "PuBu",
            "YlGnBu",
            "PuBuGn",
            "BuGn",
            "YlGn",
            "binary",
            "gist_yarg",
            "gist_gray",
            "gray",
            "bone",
            "pink",
            "spring",
            "summer",
            "autumn",
            "winter",
            "cool",
            "Wistia",
            "hot",
            "afmhot",
            "gist_heat",
            "copper",
            "PiYG",
            "PRGn",
            "BrBG",
            "PuOr",
            "RdGy",
            "RdBu",
            "RdYlBu",
            "RdYlGn",
            "Spectral",
            "coolwarm",
            "bwr",
            "seismic",
            "twilight",
            "twilight_shifted",
            "hsv",
            "Pastel1",
            "Pastel2",
            "Paired",
            "Accent",
            "Dark2",
            "Set1",
            "Set2",
            "Set3",
            "tab10",
            "tab20",
            "tab20b",
            "tab20c",
            "flag",
            "prism",
            "ocean",
            "gist_earth",
            "terrain",
            "gist_stern",
            "gnuplot",
            "gnuplot2",
            "CMRmap",
            "cubehelix",
            "brg",
            "gist_rainbow",
            "rainbow",
            "jet",
            "turbo",
            "nipy_spectral",
            "gist_ncar",
        ]
        self._colormap = self._rnd.choice(colormaps)

    def get_noise(self, pos: List[float]) -> float:
        result = 0
        factor = 1
        for i in range(self._noise_depth):
            noise = self._noises[i]
            result += noise.noise(pos) * factor
            factor /= 2

        result = max(-1, result)
        return min(1, result)

    def pos_from_ind(self, ind: int) -> Tuple[int, int]:
        width, height = self._size
        y = ind // width
        x = ind % width
        return y, x

    def ind_from_pos(self, y: int, x: int) -> int:
        width, height = self._size
        return y * width + x

    def put_noise(self, index: int) -> int:
        y, x = self.pos_from_ind(index)
        width, height = self._size
        return round((self.get_noise([y / height, x / width]) / 2 + 0.5) * 255)

    def find_next(self, x: int, y: int) -> Tuple[int, int]:
        width, height = self._size
        index = self.ind_from_pos(y, x)

        next_point = (-1, -1)
        cur_color_dist = 1e9

        window = 3
        while next_point == (-1, -1):
            candidates = []
            for i in range(-window // 2, window // 2 + 1):
                candidates.extend(
                    (
                        (x + i, y - window // 2),
                        (x + i, y + window // 2),
                        (x - window // 2, y + i),
                        (x + window // 2, y + i),
                    )
                )

            for nx, ny in candidates:
                n_index = self.ind_from_pos(ny, nx)
                if 0 <= nx < width and 0 <= ny < height and not self._path[n_index]:
                    color_dist = abs(self._pixels[n_index] - self._pixels[index])
                    if color_dist < cur_color_dist:
                        cur_color_dist = color_dist
                        next_point = (nx, ny)

            window += 2

        return next_point

    def walk(self) -> None:
        width, height = self._size
        self._path = [0] * (width * height)
        cur_x, cur_y = self._start_pos
        self._visited = 1
        self._path[self.ind_from_pos(cur_y, cur_x)] = self._visited

        while self._visited < width * height:
            cur_x, cur_y = self.find_next(cur_x, cur_y)
            self._visited += 1
            self._path[self.ind_from_pos(cur_y, cur_x)] = self._visited

    def color_path(self) -> None:
        width, height = self._size
        cmap = matplotlib.colormaps[self._colormap]
        for x, y in itertools.product(range(width), range(height)):
            ind = self.ind_from_pos(y, x)
            r, g, b, _ = cmap(self._path[ind] / (width * height))
            self._pixels[ind] = round(r * 255), round(g * 255), round(b * 255)

    def generate(self, size: Tuple[int, int], seed: int) -> Image:
        self._size = size
        width, height = self._size
        self.prepare(seed, size)
        self._pixels = [self.put_noise(i) for i in range(width * height)]

        self.walk()
        self.color_path()

        img = Image.new("RGB", self._size)
        img.putdata(self._pixels)

        return img


class Mnemonic:
    @staticmethod
    def to_seed(s: str) -> int:
        enc = s.encode()
        return int.from_bytes(
            enc + sha3_256(enc).digest(), byteorder="big", signed=False
        )

    @staticmethod
    def image(size: Tuple[int, int], seed: Union[int, str]) -> Image:
        if isinstance(seed, str):
            seed = Mnemonic.to_seed(seed)
        gen = RandomImageGenerator()
        return gen.generate(size, seed)

    @staticmethod
    def ascii_image(size: Tuple[int, int], seed: Union[int, str]) -> AsciiArt:
        img = Mnemonic.image(size, seed)
        return ascii_magic.obj_from_image(img)

    @staticmethod
    def display_image(size: Tuple[int, int], seed: Union[int, str]) -> None:
        img = Mnemonic.image(size, seed)
        img.show()

    @staticmethod
    def display_ascii_image(
        size: Tuple[int, int], seed: Union[int, str], **kwargs
    ) -> None:
        img = Mnemonic.ascii_image(size, seed)
        img.to_terminal(columns=size[0], **kwargs)
