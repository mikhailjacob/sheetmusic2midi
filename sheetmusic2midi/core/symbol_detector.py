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
    SIXTEENTH_NOTE = "sixteenth_note"
    WHOLE_REST = "whole_rest"
    HALF_REST = "half_rest"
    QUARTER_REST = "quarter_rest"
    EIGHTH_REST = "eighth_rest"
    SHARP = "sharp"
    FLAT = "flat"
    NATURAL = "natural"
    TREBLE_CLEF = "treble_clef"
    BASS_CLEF = "bass_clef"
    TIME_SIGNATURE = "time_signature"
    KEY_SIGNATURE = "key_signature"
    BEAM = "beam"
    UNKNOWN = "unknown"


class NoteDuration(Enum):
    """Standard note durations"""
    WHOLE = 4.0
    HALF = 2.0
    QUARTER = 1.0
    EIGHTH = 0.5
    SIXTEENTH = 0.25


class Accidental(Enum):
    """Musical accidentals"""
    NONE = 0
    SHARP = 1
    FLAT = -1
    NATURAL = 0
    DOUBLE_SHARP = 2
    DOUBLE_FLAT = -2


class TimeSignature:
    """Represents a time signature"""
    def __init__(self, numerator: int = 4, denominator: int = 4):
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        return f"{self.numerator}/{self.denominator}"

    def __repr__(self):
        return f"TimeSignature({self.numerator}/{self.denominator})"


class KeySignature:
    """Represents a key signature"""
    def __init__(self, sharps: int = 0, flats: int = 0):
        self.sharps = sharps
        self.flats = flats

    def __str__(self):
        if self.sharps > 0:
            return f"{self.sharps} sharps"
        elif self.flats > 0:
            return f"{self.flats} flats"
        return "C major / A minor"

    def __repr__(self):
        return f"KeySignature(sharps={self.sharps}, flats={self.flats})"


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
    accidental: Accidental = Accidental.NONE  # Sharp, flat, natural, etc.
    is_beamed: bool = False  # Whether note is part of a beam group
    beam_group_id: Optional[int] = None  # ID of beam group this note belongs to
    time_signature: Optional[TimeSignature] = None  # For time signature symbols
    key_signature: Optional[KeySignature] = None  # For key signature symbols

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
        self.accidentals: List[MusicalSymbol] = []
        self.rests: List[MusicalSymbol] = []
        self.beams: List[Tuple[int, int, int, int]] = []
        self.time_signature: Optional[TimeSignature] = TimeSignature(4, 4)  # Default 4/4
        self.key_signature: Optional[KeySignature] = KeySignature(0, 0)  # Default C major

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

    def detect_accidentals(self, image_no_staff: np.ndarray,
                          binary_image: np.ndarray) -> List[MusicalSymbol]:
        """
        Detect accidentals (sharps, flats, naturals)

        Args:
            image_no_staff: Image with staff lines removed
            binary_image: Original binary image

        Returns:
            List of detected accidental symbols
        """
        accidentals = []

        # Find contours
        contours, _ = cv2.findContours(
            image_no_staff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)

            # Accidentals have specific size range
            if area < 20 or area > 500:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / w if w > 0 else 0

            # Get staff position
            center_y = y + h // 2
            staff_pos = None
            if self.staff_detector and self.staff_detector.staves:
                _, staff_pos = self.staff_detector.get_staff_position(center_y)

            # Sharp: tall and narrow (aspect ratio > 2)
            if aspect_ratio > 2.0 and aspect_ratio < 4.0:
                # Check for horizontal lines (sharp has # pattern)
                roi = image_no_staff[y:y+h, x:x+w]
                horizontal_proj = np.sum(roi, axis=1)

                # Sharp should have strong horizontal components
                peaks = 0
                threshold = np.max(horizontal_proj) * 0.5 if np.max(horizontal_proj) > 0 else 0
                for val in horizontal_proj:
                    if val > threshold:
                        peaks += 1

                if peaks >= 2:  # Sharp has at least 2 horizontal lines
                    accidental = MusicalSymbol(
                        symbol_type=SymbolType.SHARP,
                        x=x, y=y, width=w, height=h,
                        staff_position=staff_pos,
                        accidental=Accidental.SHARP
                    )
                    accidentals.append(accidental)

            # Flat: tall with rounded bottom (aspect ratio > 1.5)
            elif aspect_ratio > 1.5 and aspect_ratio < 3.0:
                # Flat has more pixels in bottom half
                roi = image_no_staff[y:y+h, x:x+w]
                mid_h = h // 2
                top_density = np.sum(roi[:mid_h, :]) / (w * mid_h) if (w * mid_h) > 0 else 0
                bottom_density = np.sum(roi[mid_h:, :]) / (w * (h - mid_h)) if (w * (h - mid_h)) > 0 else 0

                if bottom_density > top_density * 1.2:
                    accidental = MusicalSymbol(
                        symbol_type=SymbolType.FLAT,
                        x=x, y=y, width=w, height=h,
                        staff_position=staff_pos,
                        accidental=Accidental.FLAT
                    )
                    accidentals.append(accidental)

            # Natural: tall and rectangular (aspect ratio 2-3)
            elif aspect_ratio > 1.8 and aspect_ratio < 2.8:
                # Natural has vertical lines with horizontal connectors
                accidental = MusicalSymbol(
                    symbol_type=SymbolType.NATURAL,
                    x=x, y=y, width=w, height=h,
                    staff_position=staff_pos,
                    accidental=Accidental.NATURAL
                )
                accidentals.append(accidental)

        self.accidentals = accidentals
        return accidentals

    def detect_rests(self, image_no_staff: np.ndarray) -> List[MusicalSymbol]:
        """
        Detect rest symbols

        Args:
            image_no_staff: Image with staff lines removed

        Returns:
            List of detected rest symbols
        """
        rests = []

        contours, _ = cv2.findContours(
            image_no_staff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)

            # Rests have specific size ranges
            if area < 15 or area > 800:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / w if w > 0 else 0

            center_y = y + h // 2
            staff_pos = None
            if self.staff_detector and self.staff_detector.staves:
                _, staff_pos = self.staff_detector.get_staff_position(center_y)

            # Whole rest: small horizontal rectangle
            if 0.2 <= aspect_ratio <= 0.6 and area < 200:
                rest = MusicalSymbol(
                    symbol_type=SymbolType.WHOLE_REST,
                    x=x, y=y, width=w, height=h,
                    staff_position=staff_pos,
                    note_duration=NoteDuration.WHOLE
                )
                rests.append(rest)

            # Half rest: similar to whole rest but positioned differently
            elif 0.3 <= aspect_ratio <= 0.7 and area < 200:
                rest = MusicalSymbol(
                    symbol_type=SymbolType.HALF_REST,
                    x=x, y=y, width=w, height=h,
                    staff_position=staff_pos,
                    note_duration=NoteDuration.HALF
                )
                rests.append(rest)

            # Quarter rest: complex shape, taller
            elif aspect_ratio > 1.5 and aspect_ratio < 3.0:
                # Quarter rest is irregular and tall
                rest = MusicalSymbol(
                    symbol_type=SymbolType.QUARTER_REST,
                    x=x, y=y, width=w, height=h,
                    staff_position=staff_pos,
                    note_duration=NoteDuration.QUARTER
                )
                rests.append(rest)

            # Eighth rest: has a flag
            elif aspect_ratio > 1.2 and aspect_ratio < 2.0:
                rest = MusicalSymbol(
                    symbol_type=SymbolType.EIGHTH_REST,
                    x=x, y=y, width=w, height=h,
                    staff_position=staff_pos,
                    note_duration=NoteDuration.EIGHTH
                )
                rests.append(rest)

        self.rests = rests
        return rests

    def detect_beams(self, image_no_staff: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect beam lines connecting eighth notes and shorter durations

        Args:
            image_no_staff: Image with staff lines removed

        Returns:
            List of beam rectangles (x, y, width, height)
        """
        beams = []

        # Create horizontal kernel to detect beams
        kernel_width = 20
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, 1))

        # Detect horizontal lines (potential beams)
        horizontal_lines = cv2.morphologyEx(image_no_staff, cv2.MORPH_OPEN, horizontal_kernel)

        # Find contours
        contours, _ = cv2.findContours(
            horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Beams are long and thin
            if w >= 15 and h <= 5:
                aspect_ratio = w / h if h > 0 else 0
                if aspect_ratio >= 4:
                    beams.append((x, y, w, h))

        self.beams = beams
        return beams

    def associate_beams_with_notes(self, note_heads: List[MusicalSymbol],
                                   beams: List[Tuple[int, int, int, int]]) -> None:
        """
        Associate detected beams with note heads to identify beamed groups

        Args:
            note_heads: List of detected note heads
            beams: List of detected beams
        """
        beam_group_id = 0

        for beam_x, beam_y, beam_w, beam_h in beams:
            # Find notes that are connected by this beam
            beamed_notes = []

            for note in note_heads:
                # Check if note stem connects to this beam
                # Beam should be horizontally aligned with note x position
                if beam_x <= note.center_x <= beam_x + beam_w:
                    # Check vertical proximity
                    if abs(note.y - beam_y) < 40 or abs((note.y + note.height) - beam_y) < 40:
                        beamed_notes.append(note)

            # Mark all these notes as beamed with same group ID
            if len(beamed_notes) >= 2:
                for note in beamed_notes:
                    note.is_beamed = True
                    note.beam_group_id = beam_group_id
                    # Beamed notes are at least eighth notes
                    if note.note_duration == NoteDuration.QUARTER:
                        note.symbol_type = SymbolType.EIGHTH_NOTE
                        note.note_duration = NoteDuration.EIGHTH

                beam_group_id += 1

    def apply_accidentals_to_notes(self, note_heads: List[MusicalSymbol],
                                   accidentals: List[MusicalSymbol]) -> None:
        """
        Apply detected accidentals to nearby notes

        Args:
            note_heads: List of note heads
            accidentals: List of detected accidentals
        """
        for accidental in accidentals:
            # Find the note immediately to the right of this accidental
            closest_note = None
            min_distance = float('inf')

            for note in note_heads:
                # Accidental should be to the left of the note
                if note.x > accidental.x:
                    distance = note.x - accidental.x
                    # Should be close horizontally and vertically aligned
                    vertical_diff = abs(note.center_y - accidental.center_y)

                    if distance < 30 and vertical_diff < 15:
                        if distance < min_distance:
                            min_distance = distance
                            closest_note = note

            if closest_note:
                closest_note.accidental = accidental.accidental

    def detect_time_signature(self, binary_image: np.ndarray) -> Optional[TimeSignature]:
        """
        Detect time signature at the beginning of the staff

        Args:
            binary_image: Original binary image

        Returns:
            Detected TimeSignature or default 4/4
        """
        # Look for time signature near the left side of the first staff
        if not self.staff_detector or not self.staff_detector.staves:
            return TimeSignature(4, 4)

        first_staff = self.staff_detector.staves[0]

        # Search region: left portion of staff
        search_x_start = first_staff.x_start
        search_x_end = min(first_staff.x_start + 150, first_staff.x_end)
        search_y_start = first_staff.top - 10
        search_y_end = first_staff.bottom + 10

        # Extract region
        if (search_x_end > search_x_start and search_y_end > search_y_start and
            search_x_start >= 0 and search_y_start >= 0 and
            search_x_end <= binary_image.shape[1] and search_y_end <= binary_image.shape[0]):

            region = binary_image[search_y_start:search_y_end, search_x_start:search_x_end]

            # Look for vertical stacks of numbers (time signature pattern)
            # This is simplified - in practice would use pattern matching or OCR
            contours, _ = cv2.findContours(
                region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # For now, return default 4/4
            # In a full implementation, would analyze contours to recognize digits
            self.time_signature = TimeSignature(4, 4)
        else:
            self.time_signature = TimeSignature(4, 4)

        return self.time_signature

    def detect_key_signature(self, binary_image: np.ndarray) -> Optional[KeySignature]:
        """
        Detect key signature by counting sharps or flats at staff beginning

        Args:
            binary_image: Original binary image

        Returns:
            Detected KeySignature
        """
        if not self.staff_detector or not self.staff_detector.staves:
            return KeySignature(0, 0)

        first_staff = self.staff_detector.staves[0]

        # Search region after clef but before notes
        search_x_start = first_staff.x_start + 20
        search_x_end = min(first_staff.x_start + 200, first_staff.x_end)
        search_y_start = first_staff.top
        search_y_end = first_staff.bottom

        # Extract region
        if (search_x_end > search_x_start and search_y_end > search_y_start and
            search_x_start >= 0 and search_y_start >= 0 and
            search_x_end <= binary_image.shape[1] and search_y_end <= binary_image.shape[0]):

            region = binary_image[search_y_start:search_y_end, search_x_start:search_x_end]

            # Count sharps and flats in key signature region
            sharps = 0
            flats = 0

            # Detect accidentals in this region
            temp_symbols = []
            contours, _ = cv2.findContours(
                region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            for contour in contours:
                area = cv2.contourArea(contour)
                if 20 < area < 300:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w if w > 0 else 0

                    # Count sharps (tall narrow symbols)
                    if aspect_ratio > 2.0 and aspect_ratio < 4.0:
                        sharps += 1
                    # Count flats (tall with rounded bottom)
                    elif aspect_ratio > 1.5 and aspect_ratio < 3.0:
                        flats += 1

            self.key_signature = KeySignature(sharps, flats)
        else:
            self.key_signature = KeySignature(0, 0)

        return self.key_signature

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
        # Detect time and key signatures first
        self.detect_time_signature(binary_image)
        self.detect_key_signature(binary_image)

        print(f"Time signature: {self.time_signature}")
        print(f"Key signature: {self.key_signature}")

        # Detect note heads
        note_heads = self.detect_note_heads(image_no_staff, binary_image)

        # Detect stems
        stems = self.detect_stems(image_no_staff)

        # Associate stems with note heads
        self.associate_stems_with_heads(note_heads, stems)

        # Detect beams and associate with notes
        beams = self.detect_beams(image_no_staff)
        self.associate_beams_with_notes(note_heads, beams)

        # Detect accidentals
        accidentals = self.detect_accidentals(image_no_staff, binary_image)

        # Apply accidentals to notes
        self.apply_accidentals_to_notes(note_heads, accidentals)

        # Detect rests
        rests = self.detect_rests(image_no_staff)

        # Calculate pitches (after accidentals are applied)
        for note_head in note_heads:
            base_pitch = self.calculate_pitch(note_head, clef)

            # Apply accidental if present
            if note_head.accidental != Accidental.NONE:
                note_head.pitch = self.apply_accidental_to_pitch(
                    base_pitch, note_head.accidental
                )
            else:
                note_head.pitch = base_pitch

        # Combine all symbols
        self.symbols = note_heads + rests + accidentals

        # Sort by x position
        self.symbols.sort(key=lambda s: s.x)

        print(f"Detected {len(note_heads)} notes, {len(rests)} rests, "
              f"{len(accidentals)} accidentals, {len(beams)} beams")

        for i, note in enumerate(note_heads[:10]):  # Show first 10
            duration = note.note_duration.name if note.note_duration else "UNKNOWN"
            accidental_str = f" {note.accidental.name}" if note.accidental != Accidental.NONE else ""
            beam_str = f" (beamed)" if note.is_beamed else ""
            print(f"  Note {i+1}: {note.pitch}{accidental_str} ({duration}){beam_str} at x={note.x}")

        return self.symbols

    def apply_accidental_to_pitch(self, pitch: str, accidental: Accidental) -> str:
        """
        Apply an accidental to a pitch name

        Args:
            pitch: Base pitch (e.g., 'C4')
            accidental: Accidental to apply

        Returns:
            Modified pitch string
        """
        if accidental == Accidental.NONE or accidental == Accidental.NATURAL:
            return pitch

        # Parse pitch
        if len(pitch) < 2:
            return pitch

        note = pitch[:-1]  # Everything except octave
        octave = pitch[-1]

        # Remove existing accidentals
        note_base = note[0]

        # Apply new accidental
        if accidental == Accidental.SHARP:
            return f"{note_base}#{octave}"
        elif accidental == Accidental.FLAT:
            return f"{note_base}b{octave}"
        elif accidental == Accidental.DOUBLE_SHARP:
            return f"{note_base}##{ octave}"
        elif accidental == Accidental.DOUBLE_FLAT:
            return f"{note_base}bb{octave}"

        return pitch
