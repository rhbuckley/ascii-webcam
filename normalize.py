"""
Richard Buckley
12 December 2023

`normalize.py` This file contains the ImageNormalization class. This is the
class that will be called within the AsciiImageConverter class to normalize
an image before converting it to Ascii. This file contains multiple normalization
methods that can be used to convert an image to Ascii, including luminance,
lightness, average, and normalization (experimental).

"""

import cv2
import numpy as np
from typing import Union, Literal

DEFAULT_OUTPUT_WIDTH = 100

ImageSizeType = tuple[Union[int, None], Union[int, None]]

ModesType = Literal["luminance", "lightness", "average"]
NormalizationModes = ["luminance", "lightness", "average"]


class ImageNormalization:
    normalizer: callable
    image_size: ImageSizeType

    def __init__(self, mode: ModesType = "average", img_size: ImageSizeType = None):
        """
        Initialize the ImageNormalization class.

        :param mode: the mode to use for normalization
            -- Mode must be one of the following --
            luminance: use luminance to convert an image to ascii
            lightness: use lightness to convert an image to ascii
            average: use average to convert an image to ascii
            norm: use normalization to convert an image to ascii
        :param img_size: the size of the output image (width, height)
            - use None for automatic sizing
        """
        self.normalizer = self._map_mode(mode)
        if img_size is None:
            self.image_size = (DEFAULT_OUTPUT_WIDTH, None)
        else:
            self.image_size = img_size

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """ use normalization to convert an image to ascii """
        image_resized = image_resize(image, *self.image_size)
        image_norm = self.normalizer(image_resized)
        return image_norm

    @staticmethod
    def _map_mode(mode: ModesType) -> callable:
        match mode:
            case "luminance": return ImageNormalization.calculate_luminance
            case "lightness": return ImageNormalization.calculate_lightness
            case "average": return ImageNormalization.calculate_average
            case "norm": return ImageNormalization.calculate_norm
            case _: raise ValueError(f"Invalid mode: {mode}")

    @staticmethod
    def calculate_luminance(image: np.ndarray) -> np.ndarray:
        """ use luminance to convert an image to ascii """
        weights = [0.2989, 0.5870, 0.1140]  # or [0.2126, 0.7152, 0.0722]
        return np.dot(image[..., :3], weights)  # matrix * scalar = dot product

    @staticmethod
    def calculate_lightness(image: np.ndarray) -> np.ndarray:
        """ use lightness to convert an image to ascii """
        return (np.max(image, axis=2) + np.min(image, axis=2)) / 2

    @staticmethod
    def calculate_average(image: np.ndarray) -> np.ndarray:
        """ use average to convert an image to ascii """
        return np.mean(image, axis=2)

    @staticmethod
    def calculate_norm(image: np.ndarray) -> np.ndarray:
        """ use normalization to convert an image to ascii """
        return image[..., :3] / np.linalg.norm(image[..., :3], axis=2, keepdims=True)


def image_resize(image: np.ndarray, width=None, height=None, inter=cv2.INTER_AREA):
    """ Resize an image """
    h, w = image.shape[:2]

    if height is None and width is None:
        return image

    if width is None:
        # get ratio of height to width
        r = height / float(w)
        dim = (height, int(h * r))

    elif height is None:
        r = width / float(h)
        dim = (int(h * r), width)

    else:
        dim = (int(width / float(h) * h), int(height / float(w) * w))

    return cv2.resize(image, dim, interpolation=inter)
