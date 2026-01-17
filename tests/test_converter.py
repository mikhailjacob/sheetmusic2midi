"""Test cases for SheetMusicConverter"""

import unittest
import os
import tempfile
from sheetmusic2midi import SheetMusicConverter


class TestSheetMusicConverter(unittest.TestCase):
    """Test cases for the main converter"""

    def setUp(self):
        """Set up test fixtures"""
        self.converter = SheetMusicConverter(tempo=120, clef='treble')
        self.temp_dir = tempfile.mkdtemp()

    def test_converter_initialization(self):
        """Test converter initializes correctly"""
        self.assertEqual(self.converter.tempo, 120)
        self.assertEqual(self.converter.clef, 'treble')
        self.assertIsNotNone(self.converter.image_processor)
        self.assertIsNotNone(self.converter.staff_detector)
        self.assertIsNotNone(self.converter.symbol_detector)
        self.assertIsNotNone(self.converter.midi_generator)

    def test_get_processing_info(self):
        """Test processing info retrieval"""
        info = self.converter.get_processing_info()
        self.assertIsInstance(info, dict)
        self.assertIn('num_staves', info)
        self.assertIn('num_symbols', info)
        self.assertIn('tempo', info)
        self.assertIn('clef', info)


class TestImageProcessor(unittest.TestCase):
    """Test cases for ImageProcessor"""

    def test_image_processor_initialization(self):
        """Test image processor initializes"""
        from sheetmusic2midi.core import ImageProcessor
        processor = ImageProcessor()
        self.assertIsNone(processor.original_image)
        self.assertIsNone(processor.processed_image)


class TestStaffDetector(unittest.TestCase):
    """Test cases for StaffDetector"""

    def test_staff_detector_initialization(self):
        """Test staff detector initializes"""
        from sheetmusic2midi.core import StaffDetector
        detector = StaffDetector()
        self.assertEqual(len(detector.staves), 0)


class TestSymbolDetector(unittest.TestCase):
    """Test cases for SymbolDetector"""

    def test_symbol_detector_initialization(self):
        """Test symbol detector initializes"""
        from sheetmusic2midi.core import SymbolDetector
        detector = SymbolDetector()
        self.assertEqual(len(detector.symbols), 0)


class TestMidiGenerator(unittest.TestCase):
    """Test cases for MidiGenerator"""

    def test_midi_generator_initialization(self):
        """Test MIDI generator initializes"""
        from sheetmusic2midi.core import MidiGenerator
        generator = MidiGenerator(tempo=120)
        self.assertEqual(generator.tempo, 120)

    def test_note_name_to_midi(self):
        """Test note name to MIDI conversion"""
        from sheetmusic2midi.core import MidiGenerator
        generator = MidiGenerator()

        # Test some common notes
        self.assertEqual(generator.note_name_to_midi('C4'), 60)
        self.assertEqual(generator.note_name_to_midi('A4'), 69)
        self.assertEqual(generator.note_name_to_midi('C5'), 72)


if __name__ == '__main__':
    unittest.main()
