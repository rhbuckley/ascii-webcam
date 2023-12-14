"""
Richard Buckley
12 December 2023

`gradients.py` This file contains the AsciiGradient class. This class is
responsible for not only ordering an ascii palette in terms of intensity,
but also finding the closest match for a given pixel intensity.

We also export a PresetGradients class that contains some pre-defined
gradients for the user to use within their own projects.
"""

import numpy as np
from typing import Union
from PIL import ImageFont
from itertools import chain

FONT_SIZE = 100


class AsciiGradient:
    scaler: callable

    def __init__(self, palette: str, **kwargs):
        """
        Initialize the AsciiGradient class.

        :param palette: the palette to use
        :param use_dict: find the closest match when
            calculating the intensity of each pixel
        :param ordered: the ascii is already ordered
        :param font: the font to use when calculating
            pixel intensities
        :param scaler: the scaler to use when calculating
            pixel intensities
        - None
        - minmax scaler
        """
        # find the font that the user wants to use
        font = kwargs.get('font', None)
        if font:
            self.font = ImageFont.truetype(font, size=100)
        else:
            self.font = ImageFont.load_default(size=100)  # type: ignore

        # should we scale the pixel intensities?
        scaler = kwargs.get('scaler', None)
        self.handle_scaler(scaler)

        # if we were already passed in a ordered palette...
        if kwargs.get('ordered', False):
            self.gradient = palette
            return

        # use a dictionary to find the closest match intensity-wise
        # or just use the ordered palette
        use_dict = kwargs.get('use_dict', False)

        # now we can compute the gradient that the user wants
        self.gradient = self.find_gradient(palette, use_dict)

    def closest_match(self, intensity: float):
        # given a pixel's intensity... find closest match
        if isinstance(self.gradient, dict):
            return min(self.gradient, key=lambda x: abs(x - intensity))
        return self.gradient[int((intensity / 255) * (len(self.gradient) - 1))]

    def handle_scaler(self, scaler: str) -> None:
        match scaler:
            case 'minmax':
                self.scaler = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))
            case None:
                self.scaler = lambda x: x

    def get_intensity_from_char(self, char: str) -> float:
        bmp = self.font.getmask(char, mode='L')

        # just to address ... I have made an implementation of
        # normalize_bmp_shape. I will not be using it here, but
        # it is here in case we ever want to change the method
        # we use to get the intensity of a character... instead
        # arr = self.normalize_bmp_shape(bmp)
        # return np.mean(arr)

        # for performance...
        normalize_to_size = 2 * FONT_SIZE
        arr = np.array(bmp, dtype=np.uint8).reshape(bmp.size[::-1])  # col-major to row-major

        # padding = CEIL( (SIZE - arr.shape) / 2 )
        padding = np.ceil(np.divide(np.subtract(normalize_to_size, arr.shape), 2))

        # cell_count = (padding + arr.shape)... area = cell_count[0] * cell_count[1]
        area = np.multiply(np.add(padding, arr.shape))
        return arr.sum() / area

    def find_gradient(self, palette: str, return_dict: bool) -> Union[str, dict]:
        intensity_map = {self.get_intensity_from_char(char): char for char in set(palette)}

        intensity_keys = list(intensity_map.keys())
        intensity_vals = list(self.scaler(intensity_map.values()))

        intensity_map = self.sorted_dict_from_kv(intensity_keys, intensity_vals)
        if return_dict:
            return intensity_map

        return ''.join(chain.from_iterable(intensity_map.values()))

    @staticmethod
    def normalize_bmp_shape(buff: any, s: int = 2 * FONT_SIZE, dims: str = "xy") -> np.ndarray:
        # buff is column-major we want row-major
        arr = np.array(buff, dtype=np.uint8).reshape(buff.size[::-1])

        x, xo = divmod(s - arr.shape[1], 2) if 'x' in dims else (0, 0)
        y, yo = divmod(s - arr.shape[0], 2) if 'y' in dims else (0, 0)
        return np.pad(arr, ((y, yo), (x, xo)))  # type: ignore

    @staticmethod
    def sorted_dict_from_kv(keys: list, values: list) -> dict:
        return dict(sorted(zip(keys, values)))


class PresetGradients:
    UNI = AsciiGradient(" ˙·.,:;<*≠am#W@Ŵ₩", ordered=True)
    ASCII = AsciiGradient(" .:-=+*#%@", ordered=True)
    ASCII_EXTENDED = AsciiGradient("`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu["
                                   "neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@", ordered=True)

    ALPHABETIC = AsciiGradient(" ABCDEFGHIJKLMNOPQRSTUVWXYZ", ordered=True)
    ALPHANUMERIC = AsciiGradient(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", ordered=True)

    BLOCKS = AsciiGradient(" ░▒▓█", ordered=True)
    ARROWS = AsciiGradient(" ←↑→↓↖↗↘↙", ordered=True)
    MUSICAL = AsciiGradient(" ♫♪♩♬♭♮♯°ø", ordered=True)
    GEOMETRIC = AsciiGradient(" ○◔◐◕◕◑●", ordered=True)
    ROMAN = AsciiGradient(" ♔♕♖♗♘♙♚♛♜♝♞♟", ordered=True)
    MATHEMATICAL = AsciiGradient(" ≠≤≥±≈√∞∫∑∆π", ordered=True)
