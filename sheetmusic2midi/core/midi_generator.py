"""MIDI file generation from detected musical symbols"""

import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
from typing import List, Optional
from .symbol_detector import MusicalSymbol, NoteDuration, SymbolType


class MidiGenerator:
    """Generates MIDI files from detected musical symbols"""

    def __init__(self, tempo: int = 120, ticks_per_beat: int = 480):
        """
        Initialize MIDI generator

        Args:
            tempo: Tempo in BPM (beats per minute)
            ticks_per_beat: MIDI ticks per quarter note
        """
        self.tempo = tempo
        self.ticks_per_beat = ticks_per_beat
        self.midi_file = None

    def note_name_to_midi(self, note_name: str) -> int:
        """
        Convert note name (e.g., 'C4', 'G#5') to MIDI note number

        Args:
            note_name: Note name with octave

        Returns:
            MIDI note number (0-127)
        """
        if not note_name or len(note_name) < 2:
            return 60  # Default to C4

        # Parse note name
        note = note_name[:-1]  # Everything except last char
        try:
            octave = int(note_name[-1])
        except ValueError:
            octave = 4

        # Map note names to semitones
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }

        semitone = note_map.get(note, 0)
        midi_number = (octave + 1) * 12 + semitone

        # Clamp to valid MIDI range
        return max(0, min(127, midi_number))

    def duration_to_ticks(self, duration: Optional[NoteDuration]) -> int:
        """
        Convert note duration to MIDI ticks

        Args:
            duration: Note duration enum

        Returns:
            Number of MIDI ticks
        """
        if duration is None:
            duration = NoteDuration.QUARTER

        # Duration value is in quarter notes
        # For example: WHOLE = 4.0 quarter notes, QUARTER = 1.0 quarter notes
        quarter_notes = duration.value
        ticks = int(quarter_notes * self.ticks_per_beat)

        return ticks

    def symbols_to_midi(self, symbols: List[MusicalSymbol],
                       output_path: str,
                       instrument: int = 0) -> MidiFile:
        """
        Convert musical symbols to MIDI file

        Args:
            symbols: List of detected musical symbols
            output_path: Path to save MIDI file
            instrument: MIDI instrument number (0 = Acoustic Grand Piano)

        Returns:
            Generated MidiFile object
        """
        # Create MIDI file and track
        self.midi_file = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        self.midi_file.tracks.append(track)

        # Add track name
        track.append(MetaMessage('track_name', name='Sheet Music Track', time=0))

        # Set tempo
        track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo), time=0))

        # Set instrument
        track.append(Message('program_change', program=instrument, time=0))

        # Filter only note symbols and sort by x position (temporal order)
        notes = [s for s in symbols if s.pitch is not None]
        notes.sort(key=lambda n: n.x)

        # Convert notes to MIDI messages
        current_time = 0

        for note in notes:
            # Convert note name to MIDI number
            midi_note = self.note_name_to_midi(note.pitch)

            # Get duration in ticks
            duration_ticks = self.duration_to_ticks(note.note_duration)

            # Note on (velocity = 64, medium volume)
            track.append(Message('note_on', note=midi_note, velocity=64, time=0))

            # Note off after duration
            track.append(Message('note_off', note=midi_note, velocity=64, time=duration_ticks))

        # End of track
        track.append(MetaMessage('end_of_track', time=0))

        # Save MIDI file
        self.midi_file.save(output_path)
        print(f"MIDI file saved to: {output_path}")

        return self.midi_file

    def symbols_to_midi_polyphonic(self, symbols: List[MusicalSymbol],
                                   output_path: str,
                                   instrument: int = 0,
                                   time_threshold: int = 20) -> MidiFile:
        """
        Convert musical symbols to MIDI file with polyphonic support
        (multiple notes at the same time)

        Args:
            symbols: List of detected musical symbols
            output_path: Path to save MIDI file
            instrument: MIDI instrument number
            time_threshold: X-position difference threshold to consider notes simultaneous

        Returns:
            Generated MidiFile object
        """
        # Create MIDI file and track
        self.midi_file = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        self.midi_file.tracks.append(track)

        # Add metadata
        track.append(MetaMessage('track_name', name='Sheet Music Track', time=0))
        track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo), time=0))
        track.append(Message('program_change', program=instrument, time=0))

        # Filter and sort notes
        notes = [s for s in symbols if s.pitch is not None]
        notes.sort(key=lambda n: n.x)

        if not notes:
            # Empty track
            track.append(MetaMessage('end_of_track', time=0))
            self.midi_file.save(output_path)
            return self.midi_file

        # Group notes that occur at similar x positions (chords)
        note_groups = []
        current_group = [notes[0]]

        for note in notes[1:]:
            if note.x - current_group[0].x <= time_threshold:
                current_group.append(note)
            else:
                note_groups.append(current_group)
                current_group = [note]

        note_groups.append(current_group)

        # Convert grouped notes to MIDI
        for group in note_groups:
            # All notes in group start at the same time
            for note in group:
                midi_note = self.note_name_to_midi(note.pitch)
                track.append(Message('note_on', note=midi_note, velocity=64, time=0))

            # Find the maximum duration in the group
            max_duration = max(
                self.duration_to_ticks(note.note_duration) for note in group
            )

            # Turn off all notes after the maximum duration
            for note in group:
                midi_note = self.note_name_to_midi(note.pitch)
                track.append(Message('note_off', note=midi_note, velocity=64, time=0))

            # Advance time by the duration
            # We need to subtract the duration from the first note_off
            if track:
                # Set the time on the first note_off in this group
                for i in range(len(track) - len(group), len(track)):
                    if track[i].type == 'note_off':
                        track[i].time = max_duration
                        break

        # End of track
        track.append(MetaMessage('end_of_track', time=0))

        # Save MIDI file
        self.midi_file.save(output_path)
        print(f"Polyphonic MIDI file saved to: {output_path}")

        return self.midi_file

    def get_midi_info(self) -> dict:
        """
        Get information about the generated MIDI file

        Returns:
            Dictionary with MIDI file information
        """
        if self.midi_file is None:
            return {}

        info = {
            'ticks_per_beat': self.midi_file.ticks_per_beat,
            'tempo_bpm': self.tempo,
            'num_tracks': len(self.midi_file.tracks),
            'length_ticks': self.midi_file.length,
        }

        return info
