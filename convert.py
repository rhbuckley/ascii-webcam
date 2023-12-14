"""
Richard Buckley
12 December 2023

`convert.py` This file contains the AsciiImageConverter class. This is the
main class that converts an image to Ascii. This file uses the AsciiGradient
class to determine the best match for a given pixel. This file also uses the
ImageNormalization class to normalize an image before converting it to Ascii.
"""

import os
import cv2
import numpy as np
from colored import Fore, Style
from gradients import AsciiGradient
from normalize import ImageNormalization, image_resize

DEFAULT_OUTPUT_WIDTH = 100


class AsciiImageConverter:
    def __init__(self, gradient: AsciiGradient, color: bool = False, **kwargs):
        """
        Initialize the AsciiImageConverter class.

        :param gradient: ascii gradient to use
        :param color: <terminal only> apply color? (default: False)
        :param image_size: (height, width) of the desired output image. Input None for automatic sizing.
        :param use_terminal: <terminal only> use the smallest terminal dimensions?
        :param normalization: the normalization to use when converting an image to ascii
        """
        self.gradient = gradient
        self.color = color
        self.image_size = kwargs.get("image_size", (None, DEFAULT_OUTPUT_WIDTH))

        if kwargs.get("use_terminal", False):
            term_size = os.get_terminal_size()
            if term_size.lines < term_size.columns:
                self.image_size = (term_size.lines, None)
            else:
                self.image_size = (None, term_size.columns)

        self.normalization_method = kwargs.get("normalization", "luminance")

    def normalize_image(self, input_image: np.ndarray) -> np.ndarray:
        """ normalize an image - can change mode here, but once we find the best mode... """
        conv = ImageNormalization(self.normalization_method, self.image_size)
        return conv.normalize(input_image)

    """
    Now, we will define our main function that will
    convert an image to ascii.
    """

    def convert_image(self, image: np.ndarray) -> np.ndarray:
        """
        This is the main function that converts an image to ascii.

        if AsciiImageConverter was passed color, it will return (char, r, g, b).
        otherwise, it will return (char,)

        :param image: the image to convert to ascii
        :return: the converted image (height, width, 1), or (height, width, 4)
        :return:
        """
        clean_image = self.normalize_image(image)
        resized_image = image_resize(image, *self.image_size)
        return_shape = (*clean_image.shape, 4 if self.color else 1)
        new_image = np.empty(return_shape, dtype=object)

        for idx in np.ndindex(clean_image.shape[:2]):
            pixel = clean_image[idx]
            intensity = float(pixel)

            # get the closest character match in first index, then
            # return rgb values in the next three indices
            new_image[idx] = [
                self.gradient.closest_match(intensity),
                *(resized_image[idx] if self.color else []),
            ]

        # flip around axis=0 to fix mirroring effect
        new_image = np.flip(new_image, axis=1)
        return new_image

    def convert_image_to_terminal(self, image: np.ndarray) -> str:
        """ convert an image to ascii for the terminal """
        converted_image = self.convert_image(image)

        if self.color:
            return "\n".join([
                "".join([
                    Fore.RGB(*pixel) + char + Style.RESET
                    for char, *pixel in row
                ])
                for row in converted_image
            ])

        return "\n".join([
                "".join([char for (char, *_) in row])
                for row in converted_image
            ])

    def convert_image_from_path(self, path: str):
        """ convert an image from a path to ascii """
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        if image is None:
            raise IOError(f"Could not read image from path: {path}")
        return self.convert_image(image)
