"""Musical symbol detection and recognition"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class SymbolType(Enum):
    """Types of musical symbols"""
    NOTE_HEAD = "note_head"
    NOTE_STEM = "note_stem"
    WHOLE_NOTE = "whole_note"
    HALF_NOTE = "half_note"
    QUARTER_NOTE = "quarter_note"
    EIGHTH_NOTE = "eighth_note"
    REST = "rest"
    SHARP = "sharp"
    FLAT = "flat"
    NATURAL = "natural"
    TREBLE_CLEF = "treble_clef"
    BASS_CLEF = "bass_clef"
    TIME_SIGNATURE = "time_signature"
    UNKNOWN = "unknown"


class NoteDuration(Enum):
    """Standard note durations"""
    WHOLE = 4.0
    HALF = 2.0
    QUARTER = 1.0
    EIGHTH = 0.5
    SIXTEENTH = 0.25


@dataclass
class MusicalSymbol:
    """Represents a detected musical symbol"""
    symbol_type: SymbolType
    x: int  # X-coordinate (center or left)
    y: int  # Y-coordinate (center or top)
    width: int
    height: int
    staff_position: Optional[float] = None  # Position on staff (0-4 for lines)
    confidence: float = 1.0
    note_duration: Optional[NoteDuration] = None
    pitch: Optional[str] = None  # Note name like 'C4', 'D5'

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2


class SymbolDetector:
    """Detects and classifies musical symbols"""

    def __init__(self, staff_detector=None):
        self.staff_detector = staff_detector
        self.symbols: List[MusicalSymbol] = []
        self.note_heads: List[MusicalSymbol] = []

    def detect_note_heads(self, image_no_staff: np.ndarray,
                         binary_image: np.ndarray) -> List[MusicalSymbol]:
        """
        Detect note heads (filled and hollow ovals)

        Args:
            image_no_staff: Image with staff lines removed
            binary_image: Original binary image with staff lines

        Returns:
            List of detected note head symbols
        """
        note_heads = []

        # Find contours in the image without staff lines
        contours, _ = cv2.findContours(
            image_no_staff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)

            # Note heads typically have a certain size range
            if area < 10 or area > 1000:
                continue

            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)

            # Note heads are roughly circular/oval
            aspect_ratio = w / h if h > 0 else 0

            # Check if shape is roughly circular (0.5 to 2.0 aspect ratio)
            if 0.4 <= aspect_ratio <= 2.5:
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)

                    # Circular shapes have circularity close to 1
                    if circularity > 0.3:
                        center_y = y + h // 2

                        # Get staff position
                        staff_pos = None
                        if self.staff_detector and self.staff_detector.staves:
                            _, staff_pos = self.staff_detector.get_staff_position(center_y)

                        # Determine if filled or hollow by checking pixel density
                        roi = image_no_staff[y:y+h, x:x+w]
                        pixel_density = np.sum(roi > 0) / (w * h) if (w * h) > 0 else 0

                        # Filled note heads (quarter notes, eighth notes, etc.)
                        # will have higher density
                        if pixel_density > 0.5:
                            symbol_type = SymbolType.NOTE_HEAD
                        else:
                            # Check original image with staff for hollow notes
                            roi_orig = binary_image[y:y+h, x:x+w]
                            density_orig = np.sum(roi_orig > 0) / (w * h) if (w * h) > 0 else 0
                            if density_orig > 0.2:
                                symbol_type = SymbolType.NOTE_HEAD
                            else:
                                continue

                        note_head = MusicalSymbol(
                            symbol_type=symbol_type,
                            x=x,
                            y=y,
                            width=w,
                            height=h,
                            staff_position=staff_pos
                        )
                        note_heads.append(note_head)

        # Sort note heads by x position (left to right)
        note_heads.sort(key=lambda n: n.x)
        self.note_heads = note_heads

        return note_heads

    def detect_stems(self, image_no_staff: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect note stems (vertical lines)

        Args:
            image_no_staff: Image with staff lines removed

        Returns:
            List of stem rectangles (x, y, width, height)
        """
        stems = []

        # Use morphological operations to detect vertical lines
        # Create vertical kernel
        kernel_height = 15
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_height))

        # Detect vertical lines
        vertical_lines = cv2.morphologyEx(image_no_staff, cv2.MORPH_OPEN, vertical_kernel)

        # Find contours of vertical lines
        contours, _ = cv2.findContours(
            vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Stems are thin and tall
            if w <= 5 and h >= 10:
                aspect_ratio = h / w if w > 0 else 0
                if aspect_ratio >= 3:
                    stems.append((x, y, w, h))

        return stems

    def associate_stems_with_heads(self, note_heads: List[MusicalSymbol],
                                   stems: List[Tuple[int, int, int, int]]) -> None:
        """
        Associate detected stems with note heads to determine note duration

        Args:
            note_heads: List of detected note heads
            stems: List of detected stems (x, y, width, height)
        """
        for note_head in note_heads:
            has_stem = False

            # Check if any stem is near this note head
            for stem_x, stem_y, stem_w, stem_h in stems:
                # Stem should be close to note head horizontally
                if abs(stem_x - note_head.x) < note_head.width:
                    # Stem should connect vertically
                    stem_bottom = stem_y + stem_h
                    stem_top = stem_y

                    if (stem_top <= note_head.center_y <= stem_bottom or
                        note_head.y <= stem_bottom <= note_head.y + note_head.height):
                        has_stem = True
                        break

            # Determine note type based on stem
            if has_stem:
                # For now, assume quarter note (would need more analysis for eighth, etc.)
                note_head.symbol_type = SymbolType.QUARTER_NOTE
                note_head.note_duration = NoteDuration.QUARTER
            else:
                # Check if it's a whole note (larger) or half note (hollow)
                if note_head.width > 15 or note_head.height > 15:
                    note_head.symbol_type = SymbolType.WHOLE_NOTE
                    note_head.note_duration = NoteDuration.WHOLE
                else:
                    note_head.symbol_type = SymbolType.HALF_NOTE
                    note_head.note_duration = NoteDuration.HALF

    def calculate_pitch(self, note_head: MusicalSymbol, clef: str = 'treble') -> str:
        """
        Calculate the pitch of a note based on staff position

        Args:
            note_head: Note head symbol with staff position
            clef: Type of clef ('treble' or 'bass')

        Returns:
            Note name with octave (e.g., 'C4', 'G5')
        """
        if note_head.staff_position is None:
            return 'C4'  # Default

        # For treble clef:
        # Lines (bottom to top): E4, G4, B4, D5, F5
        # Spaces (bottom to top): F4, A4, C5, E5

        # For bass clef:
        # Lines (bottom to top): G2, B2, D3, F3, A3
        # Spaces (bottom to top): A2, C3, E3, G3

        position = note_head.staff_position

        if clef == 'treble':
            # Map position to semitones from C4
            # Position 0 (bottom line) = E4 = +4 semitones from C4
            # Each position is approximately 1 semitone
            base_midi = 60  # C4

            # Treble clef: bottom line (position 4) is E4
            # We need to map position to pitch
            # Position 4 = E4 = MIDI 64
            # Position 3.5 = F4 = MIDI 65
            # Position 3 = G4 = MIDI 67
            # etc.

            # Simplified mapping: each half-step in position is 1 semitone
            # Position 4 (bottom line) = E4 = 64
            offset = int(round((4 - position) * 2))  # Approximate
            midi_note = 64 + offset

        else:  # bass clef
            # Position 4 (bottom line) = G2 = MIDI 43
            offset = int(round((4 - position) * 2))
            midi_note = 43 + offset

        # Convert MIDI number to note name
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_note // 12) - 1
        note_name = note_names[midi_note % 12]

        return f"{note_name}{octave}"

    def detect_symbols(self, binary_image: np.ndarray,
                      image_no_staff: np.ndarray,
                      clef: str = 'treble') -> List[MusicalSymbol]:
        """
        Complete symbol detection pipeline

        Args:
            binary_image: Original binary image with staff lines
            image_no_staff: Image with staff lines removed
            clef: Clef type for pitch calculation

        Returns:
            List of detected and classified symbols
        """
        # Detect note heads
        note_heads = self.detect_note_heads(image_no_staff, binary_image)

        # Detect stems
        stems = self.detect_stems(image_no_staff)

        # Associate stems with note heads
        self.associate_stems_with_heads(note_heads, stems)

        # Calculate pitches
        for note_head in note_heads:
            note_head.pitch = self.calculate_pitch(note_head, clef)

        self.symbols = note_heads

        print(f"Detected {len(note_heads)} notes")
        for i, note in enumerate(note_heads[:10]):  # Show first 10
            duration = note.note_duration.name if note.note_duration else "UNKNOWN"
            print(f"  Note {i+1}: {note.pitch} ({duration}) at x={note.x}")

        return self.symbols
