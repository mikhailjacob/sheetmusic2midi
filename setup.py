from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sheetmusic2midi",
    version="0.1.0",
    author="SheetMusic2MIDI Contributors",
    description="Convert sheet music images to MIDI files using Optical Music Recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mikhailjacob/sheetmusic2midi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "mido>=1.3.0",
        "music21>=9.1.0",
        "Pillow>=10.0.0",
        "scipy>=1.11.0",
        "scikit-image>=0.21.0",
    ],
    entry_points={
        "console_scripts": [
            "sheetmusic2midi=sheetmusic2midi.cli:main",
        ],
    },
)
