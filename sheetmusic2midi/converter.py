"""Main converter class for sheet music to MIDI conversion"""

import os
from typing import Optional, List
from .core.image_processor import ImageProcessor
from .core.staff_detector import StaffDetector
from .core.symbol_detector import SymbolDetector
from .core.midi_generator import MidiGenerator


class SheetMusicConverter:
    """
    Main class for converting sheet music images to MIDI files

    This class orchestrates the entire conversion pipeline:
    1. Image preprocessing
    2. Staff line detection
    3. Symbol detection and recognition
    4. MIDI file generation
    """

    def __init__(self, tempo: int = 120, clef: str = 'treble'):
        """
        Initialize the sheet music converter

        Args:
            tempo: Tempo in BPM (beats per minute)
            clef: Musical clef type ('treble' or 'bass')
        """
        self.tempo = tempo
        self.clef = clef

        # Initialize processing components
        self.image_processor = ImageProcessor()
        self.staff_detector = StaffDetector()
        self.symbol_detector = SymbolDetector(self.staff_detector)
        self.midi_generator = MidiGenerator(tempo=tempo)

        # Intermediate results
        self.binary_image = None
        self.image_no_staff = None

    def convert(self, input_image_path: str, output_midi_path: str,
                save_intermediate: bool = False) -> str:
        """
        Convert sheet music image to MIDI file

        Args:
            input_image_path: Path to input sheet music image
            output_midi_path: Path where MIDI file will be saved
            save_intermediate: Whether to save intermediate processing images

        Returns:
            Path to generated MIDI file
        """
        print(f"Converting {input_image_path} to MIDI...")

        # Step 1: Preprocess image
        print("\n[1/4] Preprocessing image...")
        self.binary_image = self.image_processor.full_preprocessing_pipeline(input_image_path)

        if save_intermediate:
            self._save_intermediate_image(self.binary_image, output_midi_path, "_1_preprocessed.png")

        # Step 2: Detect staff lines
        print("\n[2/4] Detecting staff lines...")
        staves = self.staff_detector.detect_staves(self.binary_image)

        if not staves:
            print("Warning: No staff lines detected. Results may be inaccurate.")

        # Remove staff lines to isolate symbols
        self.image_no_staff = self.staff_detector.remove_staff_lines(self.binary_image)

        if save_intermediate:
            self._save_intermediate_image(self.image_no_staff, output_midi_path, "_2_no_staff.png")

        # Step 3: Detect and recognize symbols
        print("\n[3/4] Detecting musical symbols...")
        symbols = self.symbol_detector.detect_symbols(
            self.binary_image,
            self.image_no_staff,
            clef=self.clef
        )

        if not symbols:
            print("Warning: No musical symbols detected.")
            # Create empty MIDI file
            self.midi_generator.symbols_to_midi([], output_midi_path)
            return output_midi_path

        # Step 4: Generate MIDI file
        print("\n[4/4] Generating MIDI file...")
        # Update MIDI generator with detected time signature
        self.midi_generator.time_signature = self.symbol_detector.time_signature
        self.midi_generator.symbols_to_midi_polyphonic(symbols, output_midi_path)

        # Print summary
        print(f"\n✓ Conversion complete!")
        print(f"  Input:  {input_image_path}")
        print(f"  Output: {output_midi_path}")
        print(f"  Detected: {len(staves)} staff/staves, {len(symbols)} notes")

        return output_midi_path

    def batch_convert(self, input_dir: str, output_dir: str,
                     file_extensions: Optional[List[str]] = None) -> List[str]:
        """
        Convert multiple sheet music images to MIDI files

        Args:
            input_dir: Directory containing input images
            output_dir: Directory where MIDI files will be saved
            file_extensions: List of image file extensions to process
                           (default: ['.png', '.jpg', '.jpeg', '.bmp'])

        Returns:
            List of paths to generated MIDI files
        """
        if file_extensions is None:
            file_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Find all image files
        image_files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in file_extensions):
                    image_files.append(os.path.join(root, file))

        print(f"Found {len(image_files)} image(s) to convert")

        # Convert each image
        output_files = []
        for i, image_path in enumerate(image_files, 1):
            print(f"\n{'='*60}")
            print(f"Processing {i}/{len(image_files)}: {os.path.basename(image_path)}")
            print('='*60)

            # Generate output path
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.mid")

            try:
                self.convert(image_path, output_path)
                output_files.append(output_path)
            except Exception as e:
                print(f"Error converting {image_path}: {e}")
                continue

        print(f"\n{'='*60}")
        print(f"Batch conversion complete: {len(output_files)}/{len(image_files)} successful")
        print('='*60)

        return output_files

    def _save_intermediate_image(self, image, output_midi_path: str, suffix: str):
        """Save intermediate processing image for debugging"""
        import cv2
        base_name = os.path.splitext(output_midi_path)[0]
        intermediate_path = f"{base_name}{suffix}"
        cv2.imwrite(intermediate_path, image)
        print(f"  Saved intermediate image: {intermediate_path}")

    def get_processing_info(self) -> dict:
        """
        Get information about the last conversion process

        Returns:
            Dictionary with processing information
        """
        info = {
            'num_staves': len(self.staff_detector.staves),
            'num_symbols': len(self.symbol_detector.symbols),
            'tempo': self.tempo,
            'clef': self.clef,
        }

        if self.staff_detector.staves:
            info['staff_info'] = [
                {
                    'lines': staff.lines,
                    'line_spacing': staff.line_spacing,
                    'x_range': (staff.x_start, staff.x_end)
                }
                for staff in self.staff_detector.staves
            ]

        if self.symbol_detector.symbols:
            info['symbol_summary'] = {
                'total': len(self.symbol_detector.symbols),
                'by_type': {}
            }
            for symbol in self.symbol_detector.symbols:
                symbol_type = symbol.symbol_type.value
                info['symbol_summary']['by_type'][symbol_type] = \
                    info['symbol_summary']['by_type'].get(symbol_type, 0) + 1

        return info
