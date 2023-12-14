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
```

### Caveats

- If you would like to use the Ascii Webcam feature, the program automatically selects your default webcam. Want to use another webcam? You can change this in `gui.py:270`

### Inspiration

Check out [this article](https://robertheaton.com/2018/06/12/programming-projects-for-advanced-beginners-ascii-art/), that goes over some of the methods implemented within this project. 
