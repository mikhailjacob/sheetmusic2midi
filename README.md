# SheetMusic2MIDI

Convert sheet music images to MIDI files using Optical Music Recognition (OMR).

## Overview

SheetMusic2MIDI is a Python library and command-line tool that automatically converts images of sheet music into playable MIDI files. It uses computer vision and image processing techniques to detect staff lines, recognize musical symbols, and generate corresponding MIDI output.

## Features

- **Image Preprocessing**: Automatic image enhancement, binarization, and deskewing
- **Staff Detection**: Robust detection of musical staff lines
- **Symbol Recognition**: Detection and classification of musical notation
  - Notes (whole, half, quarter, eighth, sixteenth)
  - Rests (whole, half, quarter, eighth)
  - Accidentals (sharps, flats, naturals)
  - Beamed notes (eighth note groups)
- **Music Theory Support**:
  - Time signature detection (4/4, 3/4, etc.)
  - Key signature detection (sharps and flats)
  - Accidental application to pitches
- **MIDI Generation**: Conversion to standard MIDI format
  - Customizable tempo
  - Time signature metadata
  - Polyphonic support (multiple simultaneous notes)
  - Rest handling (silent periods)
- **Batch Processing**: Convert multiple sheet music images at once
- **Multi-Page Support**: Combine multiple pages into a single continuous MIDI file
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

Combine multiple pages into a single MIDI file:
```bash
sheetmusic2midi --multipage page1.png page2.png page3.png output.mid
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

# Convert single image to MIDI
converter.convert('input.png', 'output.mid')

# Convert multiple pages to single MIDI file
pages = ['page1.png', 'page2.png', 'page3.png']
converter.convert_multipage(pages, 'output.mid')

# Batch convert (separate MIDI for each image)
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
- Detect time signatures (4/4, 3/4, etc.)
- Detect key signatures (count sharps/flats)
- Detect note heads using contour analysis
- Identify note stems (vertical lines)
- Detect and associate beam lines for eighth notes
- Associate stems with note heads and beams
- Determine note durations (whole, half, quarter, eighth, etc.)
- Detect accidentals (sharps, flats, naturals)
- Apply accidentals to nearby notes
- Detect rests (whole, half, quarter, eighth)
- Calculate pitch based on staff position and accidentals

### 4. MIDI Generation
- Convert recognized symbols to MIDI events
- Apply temporal ordering based on x-position
- Support polyphonic music (multiple simultaneous notes)
- Generate standard MIDI file with proper timing

## Supported Features

### Currently Supported
- **Clefs**: Treble and bass clefs
- **Notes**: Note heads (filled and hollow), note stems
- **Durations**: Whole, half, quarter, eighth, sixteenth notes
- **Rests**: Whole rest, half rest, quarter rest, eighth rest
- **Accidentals**: Sharps (#), flats (b), naturals
- **Time Signatures**: 4/4, 3/4, and other common time signatures
- **Key Signatures**: Detection of sharps and flats in key signature
- **Beamed Notes**: Eighth note groups connected by beams
- **Staff Detection**: Robust 5-line staff detection
- **Polyphonic Music**: Multiple simultaneous notes (chords)

### Planned Features
- Articulation marks (staccato, accent, etc.)
- Dynamics (forte, piano, etc.)
- Ties and slurs
- Dotted notes
- Triplets and other tuplets
- Multiple voices per staff
- Improved symbol recognition using machine learning
- Support for grand staff (piano music)

## Examples

### Generate Test Images

The repository includes scripts to generate synthetic sheet music for testing:

**Basic test images:**
```bash
python examples/generate_test_image.py
```

**Advanced test images (with accidentals, rests, beams):**
```bash
python examples/generate_advanced_test_images.py
```

These create sample sheet music images including:
- Simple scales with staff lines and notes
- Notes with sharps, flats, and naturals
- Various rest symbols
- Beamed eighth note groups
- Comprehensive tests with all features

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

##### convert_multipage()

```python
convert_multipage(image_paths, output_midi_path, save_intermediate=False)
```

Convert multiple pages of sheet music into a single continuous MIDI file.

**Parameters:**
- `image_paths` (list): List of image paths in order (page 1, page 2, etc.)
- `output_midi_path` (str): Path for output MIDI file
- `save_intermediate` (bool): Save intermediate processing images. Default: False

**Returns:** Path to generated MIDI file

**Note:** This method combines multiple pages into one continuous piece of music, as opposed to `batch_convert()` which creates separate MIDI files for each input.

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
│   ├── image_processor.py    # Image preprocessing & binarization
│   ├── staff_detector.py     # Staff line detection & removal
│   ├── symbol_detector.py    # Symbol recognition (notes, rests, accidentals, beams)
│   └── midi_generator.py     # MIDI file generation with time signatures
├── utils/                     # Utility functions
├── converter.py               # Main converter orchestrating the pipeline
├── cli.py                     # Command-line interface
├── examples/                  # Example scripts and test image generators
└── tests/                     # Unit tests
```

### Key Classes and Enums

- **SymbolType**: Enum for all musical symbols (notes, rests, accidentals, etc.)
- **NoteDuration**: Enum for note durations (whole, half, quarter, eighth, sixteenth)
- **Accidental**: Enum for accidentals (sharp, flat, natural, double sharp/flat)
- **TimeSignature**: Class representing time signatures (e.g., 4/4, 3/4)
- **KeySignature**: Class representing key signatures (sharps and flats)
- **MusicalSymbol**: Dataclass representing a detected musical symbol with all attributes

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

This project is licensed under the Apache 2 License. See the [LICENSE](LICENSE) file for details.

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
  author = {Mikhail Jacob},
  year = {2026},
  url = {https://github.com/mikhailjacob/sheetmusic2midi}
}
```

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
