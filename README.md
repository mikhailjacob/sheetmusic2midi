# SheetMusic2MIDI

Convert sheet music images to MIDI files using Optical Music Recognition (OMR).

## Overview

SheetMusic2MIDI is a Python library and command-line tool that automatically converts images of sheet music into playable MIDI files. It uses computer vision and image processing techniques to detect staff lines, recognize musical symbols, and generate corresponding MIDI output.

## Features

- **Image Preprocessing**: Automatic image enhancement, binarization, and deskewing
- **Staff Detection**: Robust detection of musical staff lines
- **Symbol Recognition**: Detection and classification of musical notation (notes, rests, etc.)
- **MIDI Generation**: Conversion to standard MIDI format with customizable tempo
- **Batch Processing**: Convert multiple sheet music images at once
- **CLI and Python API**: Use as a command-line tool or integrate into your Python projects
- **Debug Mode**: Save intermediate processing steps for analysis

## Installation

### From Source

```bash
git clone https://github.com/mikhailjacob/sheetmusic2midi.git
cd sheetmusic2midi
pip install -e .
```

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- opencv-python >= 4.8.0
- numpy >= 1.24.0
- mido >= 1.3.0
- music21 >= 9.1.0
- Pillow >= 10.0.0
- scipy >= 1.11.0
- scikit-image >= 0.21.0

## Quick Start

### Command Line

Convert a single image:
```bash
sheetmusic2midi input.png output.mid
```

Convert with custom tempo:
```bash
sheetmusic2midi input.png output.mid --tempo 140
```

Convert bass clef music:
```bash
sheetmusic2midi input.png output.mid --clef bass
```

Batch convert all images in a directory:
```bash
sheetmusic2midi --batch input_dir/ output_dir/
```

Save intermediate processing images:
```bash
sheetmusic2midi input.png output.mid --save-intermediate
```

### Python API

```python
from sheetmusic2midi import SheetMusicConverter

# Create converter
converter = SheetMusicConverter(tempo=120, clef='treble')

# Convert image to MIDI
converter.convert('input.png', 'output.mid')

# Batch convert
converter.batch_convert('input_dir/', 'output_dir/')

# Get processing information
info = converter.get_processing_info()
print(f"Detected {info['num_staves']} staves and {info['num_symbols']} symbols")
```

## How It Works

The conversion process consists of four main stages:

### 1. Image Preprocessing
- Load and convert image to grayscale
- Apply Gaussian blur for noise reduction
- Binarize using adaptive thresholding
- Detect and correct image skew
- Remove small noise artifacts

### 2. Staff Line Detection
- Calculate horizontal projection profiles
- Identify peaks corresponding to staff lines
- Group lines into staves (sets of 5 lines)
- Measure staff line spacing and thickness
- Remove staff lines to isolate symbols

### 3. Symbol Detection and Recognition
- Detect note heads using contour analysis
- Identify note stems (vertical lines)
- Associate stems with note heads
- Determine note durations (whole, half, quarter, eighth, etc.)
- Calculate pitch based on staff position
- Recognize other symbols (clefs, rests, accidentals)

### 4. MIDI Generation
- Convert recognized symbols to MIDI events
- Apply temporal ordering based on x-position
- Support polyphonic music (multiple simultaneous notes)
- Generate standard MIDI file with proper timing

## Supported Features

### Currently Supported
- Treble and bass clefs
- Note heads (filled and hollow)
- Note stems
- Basic note durations (whole, half, quarter, eighth)
- Staff line detection
- Simple monophonic and polyphonic music

### Planned Features
- Time signatures and key signatures
- Sharps, flats, and naturals
- Rests and articulation marks
- Beamed notes
- Chords and complex rhythms
- Multiple voices per staff
- Improved symbol recognition using machine learning

## Examples

### Generate Test Images

The repository includes a script to generate synthetic sheet music for testing:

```bash
cd examples
python generate_test_image.py
```

This creates sample sheet music images with staff lines and notes.

### Example Usage Script

See `examples/example_usage.py` for comprehensive usage examples:

```bash
python examples/example_usage.py
```

## API Reference

### SheetMusicConverter

Main class for converting sheet music to MIDI.

#### Constructor

```python
SheetMusicConverter(tempo=120, clef='treble')
```

**Parameters:**
- `tempo` (int): Tempo in BPM (beats per minute). Default: 120
- `clef` (str): Musical clef type - 'treble' or 'bass'. Default: 'treble'

#### Methods

##### convert()

```python
convert(input_image_path, output_midi_path, save_intermediate=False)
```

Convert a single sheet music image to MIDI.

**Parameters:**
- `input_image_path` (str): Path to input image
- `output_midi_path` (str): Path for output MIDI file
- `save_intermediate` (bool): Save intermediate processing images. Default: False

**Returns:** Path to generated MIDI file

##### batch_convert()

```python
batch_convert(input_dir, output_dir, file_extensions=None)
```

Convert multiple sheet music images.

**Parameters:**
- `input_dir` (str): Directory containing input images
- `output_dir` (str): Directory for output MIDI files
- `file_extensions` (list): Image file extensions to process. Default: ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

**Returns:** List of paths to generated MIDI files

##### get_processing_info()

```python
get_processing_info()
```

Get information about the last conversion.

**Returns:** Dictionary with processing details (number of staves, symbols, etc.)

## Architecture

```
sheetmusic2midi/
├── core/
│   ├── image_processor.py    # Image preprocessing
│   ├── staff_detector.py     # Staff line detection
│   ├── symbol_detector.py    # Symbol recognition
│   └── midi_generator.py     # MIDI file generation
├── utils/                     # Utility functions
├── converter.py               # Main converter class
└── cli.py                     # Command-line interface
```

## Limitations

- Works best with clean, high-resolution images
- Limited support for complex musical notation
- May struggle with handwritten sheet music
- Requires clear staff lines
- Currently supports single-staff or simple multi-staff music

## Contributing

Contributions are welcome! Areas for improvement include:

- Enhanced symbol recognition algorithms
- Machine learning-based note detection
- Support for more musical symbols
- Improved handling of complex rhythms
- Better error handling and validation

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Run specific tests:

```bash
python -m pytest tests/test_converter.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project uses:
- OpenCV for image processing
- mido for MIDI file handling
- music21 for music theory support

## Troubleshooting

### No staff lines detected

- Ensure the image has good contrast
- Try preprocessing the image externally
- Check that staff lines are horizontal
- Increase image resolution

### Poor symbol recognition

- Use high-resolution images (at least 300 DPI)
- Ensure clean, printed sheet music
- Avoid images with watermarks or backgrounds
- Try adjusting the clef parameter

### MIDI file sounds wrong

- Verify the correct clef is specified
- Check the tempo setting
- Review intermediate images (use --save-intermediate)
- Ensure the input image is properly oriented

## Citation

If you use this software in your research, please cite:

```
@software{sheetmusic2midi,
  title = {SheetMusic2MIDI: Optical Music Recognition for Sheet Music to MIDI Conversion},
  author = {SheetMusic2MIDI Contributors},
  year = {2026},
  url = {https://github.com/mikhailjacob/sheetmusic2midi}
}
```

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
