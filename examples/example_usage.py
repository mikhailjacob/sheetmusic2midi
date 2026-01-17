"""
Example usage of sheetmusic2midi library

This script demonstrates how to use the SheetMusicConverter class
to convert sheet music images to MIDI files.
"""

import os
from sheetmusic2midi import SheetMusicConverter


def simple_conversion_example():
    """Example: Convert a single sheet music image to MIDI"""
    print("Example 1: Simple Conversion")
    print("-" * 50)

    # Create converter with default settings
    converter = SheetMusicConverter(tempo=120, clef='treble')

    # Convert image to MIDI
    input_image = "examples/sample_sheet_music.png"
    output_midi = "output/sample_output.mid"

    if os.path.exists(input_image):
        try:
            converter.convert(input_image, output_midi)
            print(f"Success! MIDI file saved to: {output_midi}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Image not found: {input_image}")
        print("Please place a sheet music image at this path first.")

    print()


def custom_tempo_example():
    """Example: Convert with custom tempo"""
    print("Example 2: Custom Tempo")
    print("-" * 50)

    # Create converter with custom tempo (faster)
    converter = SheetMusicConverter(tempo=140, clef='treble')

    input_image = "examples/sample_sheet_music.png"
    output_midi = "output/sample_fast.mid"

    if os.path.exists(input_image):
        try:
            converter.convert(input_image, output_midi)
            print(f"Success! Fast tempo MIDI saved to: {output_midi}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Image not found: {input_image}")

    print()


def bass_clef_example():
    """Example: Convert bass clef sheet music"""
    print("Example 3: Bass Clef Conversion")
    print("-" * 50)

    # Create converter for bass clef
    converter = SheetMusicConverter(tempo=100, clef='bass')

    input_image = "examples/bass_clef_sample.png"
    output_midi = "output/bass_output.mid"

    if os.path.exists(input_image):
        try:
            converter.convert(input_image, output_midi)
            print(f"Success! Bass clef MIDI saved to: {output_midi}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Image not found: {input_image}")
        print("This example requires a bass clef sheet music image.")

    print()


def batch_conversion_example():
    """Example: Batch convert multiple images"""
    print("Example 4: Batch Conversion")
    print("-" * 50)

    # Create converter
    converter = SheetMusicConverter(tempo=120, clef='treble')

    input_dir = "examples/"
    output_dir = "output/batch/"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        output_files = converter.batch_convert(input_dir, output_dir)
        print(f"Converted {len(output_files)} file(s)")
        for file in output_files:
            print(f"  - {file}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def debug_mode_example():
    """Example: Save intermediate processing images"""
    print("Example 5: Debug Mode (Save Intermediate Images)")
    print("-" * 50)

    converter = SheetMusicConverter(tempo=120, clef='treble')

    input_image = "examples/sample_sheet_music.png"
    output_midi = "output/debug_output.mid"

    if os.path.exists(input_image):
        try:
            # This will save intermediate processing steps
            converter.convert(input_image, output_midi, save_intermediate=True)
            print(f"Success! Check output directory for intermediate images:")
            print(f"  - {output_midi[:-4]}_1_preprocessed.png")
            print(f"  - {output_midi[:-4]}_2_no_staff.png")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Image not found: {input_image}")

    print()


def get_processing_info_example():
    """Example: Get information about the conversion process"""
    print("Example 6: Get Processing Information")
    print("-" * 50)

    converter = SheetMusicConverter(tempo=120, clef='treble')

    input_image = "examples/sample_sheet_music.png"
    output_midi = "output/info_output.mid"

    if os.path.exists(input_image):
        try:
            converter.convert(input_image, output_midi)

            # Get detailed processing information
            info = converter.get_processing_info()

            print("\nProcessing Information:")
            print(f"  Number of staves: {info['num_staves']}")
            print(f"  Number of symbols: {info['num_symbols']}")
            print(f"  Tempo: {info['tempo']} BPM")
            print(f"  Clef: {info['clef']}")

            if 'staff_info' in info:
                for i, staff in enumerate(info['staff_info'], 1):
                    print(f"\n  Staff {i}:")
                    print(f"    Line spacing: {staff['line_spacing']:.1f} pixels")
                    print(f"    X range: {staff['x_range']}")

        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Image not found: {input_image}")

    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("SheetMusic2MIDI - Example Usage")
    print("=" * 60 + "\n")

    # Create output directory
    os.makedirs("output", exist_ok=True)

    # Run examples
    simple_conversion_example()
    custom_tempo_example()
    bass_clef_example()
    batch_conversion_example()
    debug_mode_example()
    get_processing_info_example()

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
