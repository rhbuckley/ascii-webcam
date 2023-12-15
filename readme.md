# Ascii Webcam

A very common project in Computer Science is converting images to their Ascii equivalent. We did just that in this project but delved into significantly more depth. 

### Features

- Normalization Methods: What method should we use to determine which ASCII char belongs to each pixel.
- Gradient Generation: How can we order characters in order of density/weight/intensity?
- Webcam: Live ASCII image conversion through your webcam. 
- Colors: ASCII Art output through the GUI / terminal can be colored

### Installation

```shell
gh repo clone rhbuckley/ascii-webcam
pip install -r requirements.txt

python ascii_webcam/gui.py
```

The GUI looks for fonts in the `./assets` folder, so if you decide to run from inside of the ascii_webcam folder, you may need to change the path to the fonts. 

#### Package

I have converted this into a package for local use. If you wish to use this code elsewhere, you may run

```shell
source path/to/venv/bin/activate

cd path/to/ascii_webcam

pip install .
```

What you are doing here is using your project specific venv-interperter, and then installing the ascii_webcam package. This project is not useful enough for me to list this package on PyPi, so for now, it will be local only.

### Caveats

- If you would like to use the Ascii Webcam feature, the program automatically selects your default webcam. Want to use another webcam? You can change this in `gui.py:270`

### Inspiration

Check out [this article](https://robertheaton.com/2018/06/12/programming-projects-for-advanced-beginners-ascii-art/), that goes over some of the methods implemented within this project. 
