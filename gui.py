"""
13 December 2023

`gui.py` This file contains the pygame gui
used for visualizing the results of this
project, This file does use threading to keep
the GUI responsive while the image is being
converted to ascii.

Tip: The GUI is buggy when initially focusing the
app. Click out of the pygame window as to focus
a different app, and then click back. I do not know
why this is a problem, but I am using an Apple Silicon
Mac. Maybe a different machine will have better results.
"""

import sys
import threading
import numpy as np

import pygame
import pygame_gui
import pygame.camera
import pygame.freetype
import pygame.surfarray

from itertools import count
from ascii_webcam.gradients import PresetGradients
from ascii_webcam.convert import AsciiImageConverter
from ascii_webcam.normalize import NormalizationModes


class GUIOptions:
    FLAGS: int = 0

    ICON_PATH: str = "./assets/funny.png"
    WINDOW_NAME: str = "Ascii Cam"

    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600

    FONT_SIZE: int = 12
    FONT_PATH: str = "./assets/freefont/FreeMono.ttf"

    x_spacing: float = 0.9
    y_spacing: float = 0.9

    @property
    def window_size(self):
        return self.WINDOW_WIDTH, self.WINDOW_HEIGHT

    @property
    def ascii_width(self):
        return self.WINDOW_WIDTH // (self.FONT_SIZE * self.x_spacing)

    @property
    def ascii_height(self):
        return self.WINDOW_HEIGHT // (self.FONT_SIZE * self.y_spacing)

    @property
    def ascii_output_size(self):
        return self.ascii_height, self.ascii_width

    def __init__(self, parent):
        # circular reference
        self.parent = parent

        # create the pygame_gui manager
        self.manager = pygame_gui.UIManager(self.window_size)

        # a generator to manage the spacing of each element
        def get_pos(offset: int = 60):
            padding = 10
            widget_size = (120, 50)  # length, width
            start_x, start_y = self.WINDOW_WIDTH - \
                widget_size[0] - padding, padding
            for i in count(start=0):
                yield pygame.Rect((start_x, start_y + offset * i), widget_size)

        pos = get_pos()

        # switch mode button
        self.m_mode = 'ASCII'
        self.btn_switch_mode = pygame_gui.elements.UIButton(
            relative_rect=next(pos),
            text='Switch View',
            manager=self.manager
        )

        # gradient selector
        self.m_gradient = PresetGradients.UNI
        self.selector_gradient = pygame_gui.elements.UIDropDownMenu(
            relative_rect=next(pos),
            options_list=[
                opt for opt in PresetGradients.__dict__.keys() if not opt.startswith("__")],
            starting_option="UNI",
            manager=self.manager
        )

        # normalization
        self.m_normalization = "luminance"
        self.selector_normalization = pygame_gui.elements.UIDropDownMenu(
            relative_rect=next(pos),
            options_list=NormalizationModes,
            starting_option=self.m_normalization,
            manager=self.manager
        )

        # invert colors button
        self.m_invert_colors = False
        self.btn_invert_colors = pygame_gui.elements.UIButton(
            relative_rect=next(pos),
            text='Invert',
            manager=self.manager
        )

        # use colors button
        self.m_use_color = True
        self.btn_use_color = pygame_gui.elements.UIButton(
            relative_rect=next(pos),
            text='Color',
            manager=self.manager
        )

        # equal spacing button
        self.m_equidistant = True
        self.btn_switch_spacing = pygame_gui.elements.UIButton(
            relative_rect=next(pos),
            text='Equidistant',
            manager=self.manager
        )

        # x spacing of characters
        self.slider_x_spacing = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=next(pos),
            start_value=self.x_spacing,
            value_range=(0.1, 1.0),
            manager=self.manager
        )

        # y spacing of characters
        self.slider_y_spacing = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=next(pos),
            start_value=self.y_spacing,
            value_range=(0.1, 1.0),
            manager=self.manager
        )

    def handle_ui_event(self, event: pygame.Event):
        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                # it's a button!
                match event.ui_element:
                    case self.btn_switch_mode:
                        states = {"ASCII": "IMAGE", "IMAGE": "ASCII"}
                        self.m_mode = states[self.m_mode]

                        # stop the threading, reset conversion state
                        self.parent.engine_thread.join()
                        self.parent.conversion_ready = True

                    case self.btn_invert_colors:
                        self.m_invert_colors = not self.m_invert_colors

                    case self.btn_use_color:
                        # update state & text
                        self.m_use_color = not self.m_use_color
                        self.btn_use_color.set_text(
                            'Color' if self.m_use_color
                            else 'Grayscale'
                        )

                        # we can't have color without equal spacing
                        if self.m_use_color:
                            self.m_equidistant = True
                            self.btn_switch_spacing.set_text('Equidistant')

                    case self.btn_switch_spacing:
                        # update state
                        self.m_equidistant = not self.m_equidistant
                        self.btn_switch_spacing.set_text(
                            'Equidistant' if self.m_equidistant
                            else 'No Spacing'
                        )

                        # update sizing
                        self.x_spacing = 1.0 if self.m_equidistant else 0.583
                        self.y_spacing = 1.0 if self.m_equidistant else 0.583
                        self.slider_x_spacing.current_value = self.x_spacing
                        self.slider_y_spacing.current_value = self.y_spacing
                        self.parent.converter.image_size = self.ascii_output_size

                        # no equal spacing -> no color
                        if not self.m_equidistant:
                            self.m_use_color = False
                            self.btn_use_color.set_text('Grayscale')

            case pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                match event.ui_element:
                    case self.selector_gradient:
                        # get the gradient
                        self.m_gradient = PresetGradients.__dict__[event.text]

                        # update the converter
                        self.parent.converter = AsciiImageConverter(
                            gradient=self.m_gradient,
                            color=True,
                            image_size=self.ascii_output_size,
                            normalization=self.m_normalization
                        )
                    case self.selector_normalization:
                        # update the normalization
                        self.m_normalization = event.text

                        # update the converter
                        self.parent.converter = AsciiImageConverter(
                            gradient=self.m_gradient,
                            color=True,
                            image_size=self.ascii_output_size,
                            normalization=self.m_normalization
                        )

            case pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                match event.ui_element:
                    case self.slider_x_spacing:
                        self.x_spacing = event.value
                        self.parent.converter.image_size = self.ascii_output_size
                    case self.slider_y_spacing:
                        self.y_spacing = event.value
                        self.parent.converter.image_size = self.ascii_output_size

        # update the manager (UI events)
        self.manager.process_events(event)


class AsciiMain:
    options: GUIOptions

    # this is just to manage view
    clock = pygame.time.Clock()

    # manage the game loops
    engine_thread: threading.Thread

    # Okay to render next frame?
    conversion_ready = True

    def __init__(self):
        pygame.init()

        # initialize options
        self.options = GUIOptions(self)

        # set the window
        self.display = pygame.display.set_mode(
            size=self.options.window_size,
            flags=self.options.FLAGS,
        )

        # load the icon
        icon = pygame.image.load(self.options.ICON_PATH)
        pygame.display.set_icon(icon)

        # add a caption
        pygame.display.set_caption(self.options.WINDOW_NAME)

        # background
        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))

        # load font
        self.font = pygame.freetype.Font(
            self.options.FONT_PATH,
            self.options.FONT_SIZE
        )

        # create & initialize camera
        pygame.camera.init()
        self.camera = pygame.camera.Camera(
            pygame.camera.list_cameras()[0]
        )
        self.camera.start()

        # init & get first frame
        self.frame = self.camera.get_image()

        # screen for the camera
        self.screen = pygame.surface.Surface(
            self.options.window_size, 0, self.display)

        # screen for ascii text display
        self.text_display = pygame.surface.Surface(
            self.options.window_size, 0, self.display)

        # --- Ascii Conversion ---
        self.converter = AsciiImageConverter(
            gradient=PresetGradients.UNI,
            image_size=self.options.ascii_output_size,
            color=True,
        )

        # start the loop
        self.main_loop()

    def convert_next_frame(self, arr: np.ndarray):
        """
        This function prepares the next frame to be rendered.
        Since this function will be called through a thread,
        it does not actually update the display.
        :param arr: the image to convert
        :return: None -> updates self.text_display
        """
        # lock up the thread / engine rendering
        self.conversion_ready = False

        # clear the canvas
        self.text_display.fill(pygame.Color('#000000'))

        # convert the image to ascii text
        text_to_render = self.converter.convert_image(arr)
        text_to_render = np.flip(text_to_render, axis=(0, 1))

        # if we want a grid-like output
        if self.options.m_equidistant:
            for i, row in enumerate(text_to_render):
                for j, (char, *rgb) in enumerate(row):
                    # it is possible to create a master set of text_surfaces, but I think that
                    # the time complexity would be ~ the same, as we would still need to change
                    # the color of the text_surface

                    """
                    DEBUGGING A PROBLEM
                    ----------------------------
                    Problem: When using the ascii rendering with equidistant spacing,
                    the image appears in black / white mirrored above output

                    self.font.render << antialias. Tried with true / false, no difference
                    self.font.color << only upside down image appears...

                    self.text_display << location: I added in a if j > 30 break, to ensure that
                    the text wasn't wrapping the Surface, but that was not the issue. 

                    self.converter.convert_image: We saw good results in the no interpolation mode,
                    however, that did not have color.

                        -> Solved: I flipped the image too early in the normalize function. This resulted
                                    in one image being flipped (ascii) and one not being flipped (colored)

                        -> Solution: moved the flip function

                    """
                    self.font.render_to(
                        text=char,
                        surf=self.text_display,
                        dest=(
                            i * self.options.FONT_SIZE * self.options.x_spacing,
                            j * self.options.FONT_SIZE * self.options.y_spacing
                        ),
                        fgcolor=pygame.Color(*rgb),
                    )

        else:
            # we need to flip (transpose) text_to_render
            # because we want to render it in the correct orientation
            # the output is row, col, (char, rgb)... when we print
            text_to_render = np.transpose(text_to_render, axes=(1, 0, 2))

            for i, row in enumerate(text_to_render):
                # Join the characters to a row
                text_to_render = "".join([char for char, *_ in row])
                self.font.render_to(
                    text=text_to_render,
                    surf=self.text_display,
                    dest=(0, i * self.options.FONT_SIZE *
                          self.options.x_spacing),
                    fgcolor=pygame.Color("#FFFFFF")
                )

        # unlock the thread / engine loop
        self.conversion_ready = True

    def engine_loop(self):
        # transform image
        np_img = pygame.surfarray.array3d(self.frame)

        # invert image if option says...
        if self.options.m_invert_colors:
            np_img = 255 - np_img

        if not self.options.m_use_color:
            # convert to grayscale -> use np.dot for performance
            np_img = np_img.dot([0.298, 0.587, 0.114])[
                :, :, None].repeat(3, axis=2)

        # render
        if self.options.m_mode == "ASCII":
            # clear the canvas
            self.display.blit(self.background, (0, 0))

            # update the text display
            self.display.blit(self.text_display, (0, 0))

            # create & run the next thread
            self.engine_thread = threading.Thread(
                target=self.convert_next_frame,
                args=(np_img,)
            )
            if not self.engine_thread.is_alive():
                self.engine_thread.start()

        else:
            # clear the canvas
            self.display.blit(self.background, (0, 0))

            # check if we are filtering the image
            if not self.options.m_use_color or self.options.m_invert_colors:
                image = pygame.surfarray.make_surface(np_img)
            else:
                image = self.frame

            scaled_image = pygame.transform.scale(
                surface=image,
                size=self.options.window_size,
                dest_surface=self.screen
            )

            mirrored_image = pygame.transform.flip(
                surface=scaled_image,
                flip_x=True,
                flip_y=False
            )

            # add the scaled image to the canvas
            self.display.blit(mirrored_image, (0, 0))

        # update the next camera frame
        self.frame = self.camera.get_image()

    def main_loop(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.quit()

                # pass the event to options
                self.options.handle_ui_event(event)

            # update the tick
            self.options.manager.update(dt)

            # check if we have a frame to convert
            if self.conversion_ready:
                self.engine_loop()

            # draw the UI
            self.options.manager.draw_ui(self.display)
            pygame.display.flip()

    def quit(self):
        self.camera.stop()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    AsciiMain()
