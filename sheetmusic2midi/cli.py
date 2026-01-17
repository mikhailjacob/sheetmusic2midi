"""Command-line interface for sheetmusic2midi"""

import argparse
import os
import sys
from .converter import SheetMusicConverter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Convert sheet music images to MIDI files using Optical Music Recognition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single image
  sheetmusic2midi input.png output.mid

  # Convert with specific tempo
  sheetmusic2midi input.png output.mid --tempo 140

  # Convert bass clef music
  sheetmusic2midi input.png output.mid --clef bass

  # Batch convert all images in a directory
  sheetmusic2midi --batch input_dir/ output_dir/

  # Combine multiple pages into one MIDI file
  sheetmusic2midi --multipage page1.png page2.png page3.png output.mid

  # Convert PDF sheet music to MIDI
  sheetmusic2midi sheet_music.pdf output.mid

  # Save intermediate processing images
  sheetmusic2midi input.png output.mid --save-intermediate
        """
    )

    parser.add_argument(
        'input',
        nargs='+',
        help='Input sheet music image file(s) or directory (for batch mode)'
    )

    parser.add_argument(
        'output',
        help='Output MIDI file path or directory (for batch/multipage mode)'
    )

    parser.add_argument(
        '--tempo',
        type=int,
        default=120,
        help='Tempo in BPM (beats per minute). Default: 120'
    )

    parser.add_argument(
        '--clef',
        choices=['treble', 'bass'],
        default='treble',
        help='Musical clef type. Default: treble'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch mode: convert all images in input directory'
    )

    parser.add_argument(
        '--multipage',
        action='store_true',
        help='Multi-page mode: combine multiple pages into single MIDI file'
    )

    parser.add_argument(
        '--save-intermediate',
        action='store_true',
        help='Save intermediate processing images for debugging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='sheetmusic2midi 0.1.0'
    )

    args = parser.parse_args()

    # Validate input - input is now a list
    input_paths = args.input

    # Validate modes
    if args.batch and args.multipage:
        print("Error: Cannot use both --batch and --multipage flags", file=sys.stderr)
        return 1

    # Create converter
    converter = SheetMusicConverter(tempo=args.tempo, clef=args.clef)

    try:
        if args.batch:
            # Batch conversion mode
            if len(input_paths) != 1:
                print("Error: In batch mode, provide exactly one input directory", file=sys.stderr)
                return 1

            input_dir = input_paths[0]
            if not os.path.isdir(input_dir):
                print("Error: In batch mode, input must be a directory", file=sys.stderr)
                return 1

            output_files = converter.batch_convert(input_dir, args.output)

            if output_files:
                print(f"\nSuccessfully converted {len(output_files)} file(s)")
                return 0
            else:
                print("No files were converted", file=sys.stderr)
                return 1

        elif args.multipage:
            # Multi-page conversion mode
            if len(input_paths) < 2:
                print("Error: Multi-page mode requires at least 2 input images", file=sys.stderr)
                return 1

            # Validate all input files exist
            for path in input_paths:
                if not os.path.exists(path):
                    print(f"Error: Input file '{path}' does not exist", file=sys.stderr)
                    return 1

            # Ensure output directory exists
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Convert multiple pages to single MIDI
            converter.convert_multipage(
                input_paths,
                args.output,
                save_intermediate=args.save_intermediate
            )

            return 0

        else:
            # Single file conversion mode
            if len(input_paths) != 1:
                print("Error: Single file mode requires exactly one input file", file=sys.stderr)
                print("Hint: Use --multipage for multiple pages or --batch for batch processing", file=sys.stderr)
                return 1

            input_file = input_paths[0]

            if not os.path.exists(input_file):
                print(f"Error: Input file '{input_file}' does not exist", file=sys.stderr)
                return 1

            if os.path.isdir(input_file):
                print("Error: Input is a directory. Use --batch flag for batch conversion",
                      file=sys.stderr)
                return 1

            # Ensure output directory exists
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Check if input is a PDF file
            if input_file.lower().endswith('.pdf'):
                # Convert PDF
                print("Detected PDF file, extracting pages...")
                converter.convert_pdf(
                    input_file,
                    args.output,
                    save_intermediate=args.save_intermediate
                )
            else:
                # Convert single image
                converter.convert(
                    input_file,
                    args.output,
                    save_intermediate=args.save_intermediate
                )

            return 0

    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\nError during conversion: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
