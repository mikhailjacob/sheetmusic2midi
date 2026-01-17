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

  # Save intermediate processing images
  sheetmusic2midi input.png output.mid --save-intermediate
        """
    )

    parser.add_argument(
        'input',
        help='Input sheet music image file or directory (for batch mode)'
    )

    parser.add_argument(
        'output',
        help='Output MIDI file path or directory (for batch mode)'
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

    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist", file=sys.stderr)
        return 1

    # Create converter
    converter = SheetMusicConverter(tempo=args.tempo, clef=args.clef)

    try:
        if args.batch:
            # Batch conversion mode
            if not os.path.isdir(args.input):
                print("Error: In batch mode, input must be a directory", file=sys.stderr)
                return 1

            output_files = converter.batch_convert(args.input, args.output)

            if output_files:
                print(f"\nSuccessfully converted {len(output_files)} file(s)")
                return 0
            else:
                print("No files were converted", file=sys.stderr)
                return 1

        else:
            # Single file conversion mode
            if os.path.isdir(args.input):
                print("Error: Input is a directory. Use --batch flag for batch conversion",
                      file=sys.stderr)
                return 1

            # Ensure output directory exists
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Convert
            converter.convert(
                args.input,
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
