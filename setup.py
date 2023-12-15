from setuptools import setup, find_packages

setup(
    name='AsciiWebcam',
    version='0.1.0',
    author='Richard Buckley',
    description='Real time webcam to ascii conversion',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/yourpackagename',
    packages=find_packages(),
    install_requires=[
        'colored >= 2.2.3',
        'numpy >= 1.26.2',
        'opencv-python >= 4.8.1.78',
        'Pillow >= 10.1.0',
        'python-i18n >= 0.3.9',
        'colored >= 2.2.3',
        'numpy >= 1.26.2',
        'opencv-python >= 4.8.1.78',
        'Pillow >= 10.1.0',
    ],
)
