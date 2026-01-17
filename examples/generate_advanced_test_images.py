"""
Generate advanced test images with accidentals, rests, and beamed notes

This creates sheet music images with the newly supported features.
"""

import cv2
import numpy as np


def create_staff_lines(image, y_start, line_spacing, line_thickness, x_start, x_end):
    """Draw 5 horizontal staff lines"""
    for i in range(5):
        y = y_start + i * line_spacing
        cv2.line(image, (x_start, y), (x_end, y), 0, line_thickness)


def draw_note_head(image, x, y, radius, filled=True):
    """Draw a note head (oval shape)"""
    axes = (radius, int(radius * 0.7))
    angle = -20
    if filled:
        cv2.ellipse(image, (x, y), axes, angle, 0, 360, 0, -1)
    else:
        cv2.ellipse(image, (x, y), axes, angle, 0, 360, 0, 2)


def draw_note_stem(image, x, y, length, thickness=2):
    """Draw a note stem"""
    cv2.line(image, (x, y), (x, y - length), 0, thickness)


def draw_sharp(image, x, y, size=10):
    """Draw a sharp symbol (#)"""
    # Two vertical lines
    cv2.line(image, (x-3, y-size), (x-3, y+size), 0, 2)
    cv2.line(image, (x+3, y-size), (x+3, y+size), 0, 2)
    # Two horizontal lines (slanted)
    cv2.line(image, (x-5, y-3), (x+5, y-2), 0, 2)
    cv2.line(image, (x-5, y+3), (x+5, y+4), 0, 2)


def draw_flat(image, x, y, size=12):
    """Draw a flat symbol (b)"""
    # Vertical line
    cv2.line(image, (x, y-size), (x, y+size//2), 0, 2)
    # Rounded bottom part
    cv2.ellipse(image, (x+3, y+2), (4, 5), 0, -90, 180, 0, 2)


def draw_natural(image, x, y, size=10):
    """Draw a natural symbol"""
    # Two vertical lines
    cv2.line(image, (x-3, y-size), (x-3, y+2), 0, 2)
    cv2.line(image, (x+3, y-2), (x+3, y+size), 0, 2)
    # Two horizontal connectors
    cv2.line(image, (x-3, y-2), (x+3, y-2), 0, 2)
    cv2.line(image, (x-3, y+2), (x+3, y+2), 0, 2)


def draw_quarter_rest(image, x, y):
    """Draw a quarter rest"""
    # Simplified quarter rest (zigzag shape)
    points = np.array([
        [x, y-15],
        [x+5, y-10],
        [x, y-5],
        [x+5, y],
        [x, y+5],
        [x+5, y+10]
    ], np.int32)
    cv2.polylines(image, [points], False, 0, 2)


def draw_half_rest(image, x, y, width=10):
    """Draw a half rest (sits on line)"""
    cv2.rectangle(image, (x-width//2, y), (x+width//2, y+4), 0, -1)


def draw_whole_rest(image, x, y, width=10):
    """Draw a whole rest (hangs from line)"""
    cv2.rectangle(image, (x-width//2, y-4), (x+width//2, y), 0, -1)


def draw_beam(image, x1, x2, y, thickness=3):
    """Draw a beam connecting notes"""
    cv2.line(image, (x1, y), (x2, y), 0, thickness)


def create_sheet_with_accidentals(filename="sheet_with_accidentals.png"):
    """Create sheet music with sharps, flats, and naturals"""
    width, height = 900, 400
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Staff parameters
    line_spacing = 20
    line_thickness = 3
    staff_y_start = 120
    x_start = 50
    x_end = width - 50

    # Draw staff lines
    create_staff_lines(image, staff_y_start, line_spacing, line_thickness, x_start, x_end)

    # Note parameters
    note_radius = 12
    stem_length = 45
    note_spacing = 90
    start_x = 150

    # Draw notes with accidentals
    notes = [
        # (x_offset, y_pos, accidental_type, note_type)
        (0, staff_y_start + 3 * line_spacing, 'sharp', 'quarter'),  # G#
        (1, staff_y_start + 2.5 * line_spacing, None, 'quarter'),    # A
        (2, staff_y_start + 2 * line_spacing, 'flat', 'quarter'),    # Bb
        (3, staff_y_start + 1.5 * line_spacing, None, 'quarter'),    # C
        (4, staff_y_start + line_spacing, 'natural', 'quarter'),     # D natural
        (5, staff_y_start + 0.5 * line_spacing, 'sharp', 'quarter'), # E#
    ]

    for i, (x_offset, y_pos, accidental, note_type) in enumerate(notes):
        x = start_x + x_offset * note_spacing
        y = int(y_pos)

        # Draw accidental if present
        if accidental == 'sharp':
            draw_sharp(image, x - 25, y, size=8)
        elif accidental == 'flat':
            draw_flat(image, x - 25, y, size=10)
        elif accidental == 'natural':
            draw_natural(image, x - 25, y, size=8)

        # Draw note head
        draw_note_head(image, x, y, note_radius, filled=True)

        # Draw stem
        stem_x = x + note_radius - 2
        draw_note_stem(image, stem_x, y, stem_length)

    cv2.imwrite(filename, image)
    print(f"Generated sheet music with accidentals: {filename}")
    return image


def create_sheet_with_rests(filename="sheet_with_rests.png"):
    """Create sheet music with various rest symbols"""
    width, height = 900, 400
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Staff parameters
    line_spacing = 20
    line_thickness = 3
    staff_y_start = 120
    x_start = 50
    x_end = width - 50

    # Draw staff lines
    create_staff_lines(image, staff_y_start, line_spacing, line_thickness, x_start, x_end)

    note_radius = 12
    stem_length = 45
    spacing = 100
    start_x = 150

    # Pattern: note, rest, note, rest, etc.
    elements = [
        ('note', staff_y_start + 2 * line_spacing),  # Note
        ('whole_rest', staff_y_start + line_spacing),  # Whole rest
        ('note', staff_y_start + 3 * line_spacing),  # Note
        ('half_rest', staff_y_start + 2 * line_spacing),  # Half rest
        ('note', staff_y_start + line_spacing),  # Note
        ('quarter_rest', staff_y_start + 2 * line_spacing),  # Quarter rest
    ]

    for i, (elem_type, y_pos) in enumerate(elements):
        x = start_x + i * spacing
        y = int(y_pos)

        if elem_type == 'note':
            # Draw quarter note
            draw_note_head(image, x, y, note_radius, filled=True)
            stem_x = x + note_radius - 2
            draw_note_stem(image, stem_x, y, stem_length)

        elif elem_type == 'whole_rest':
            draw_whole_rest(image, x, y, width=14)

        elif elem_type == 'half_rest':
            draw_half_rest(image, x, y, width=14)

        elif elem_type == 'quarter_rest':
            draw_quarter_rest(image, x, y)

    cv2.imwrite(filename, image)
    print(f"Generated sheet music with rests: {filename}")
    return image


def create_sheet_with_beamed_notes(filename="sheet_with_beamed_notes.png"):
    """Create sheet music with beamed eighth notes"""
    width, height = 900, 400
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Staff parameters
    line_spacing = 20
    line_thickness = 3
    staff_y_start = 120
    x_start = 50
    x_end = width - 50

    # Draw staff lines
    create_staff_lines(image, staff_y_start, line_spacing, line_thickness, x_start, x_end)

    note_radius = 12
    stem_length = 45

    # First group of beamed notes
    group1_notes = [
        (180, staff_y_start + 2 * line_spacing),
        (220, staff_y_start + 1.5 * line_spacing),
        (260, staff_y_start + line_spacing),
        (300, staff_y_start + 1.5 * line_spacing),
    ]

    # Draw first group
    stem_tops = []
    for x, y in group1_notes:
        y = int(y)
        draw_note_head(image, x, y, note_radius, filled=True)
        stem_x = x + note_radius - 2
        stem_top_y = y - stem_length
        draw_note_stem(image, stem_x, y, stem_length)
        stem_tops.append((stem_x, stem_top_y))

    # Draw beam for first group
    beam_y = int(np.mean([y for _, y in stem_tops]))
    draw_beam(image, stem_tops[0][0], stem_tops[-1][0], beam_y, thickness=4)

    # Second group of beamed notes
    group2_notes = [
        (420, staff_y_start + 3 * line_spacing),
        (460, staff_y_start + 2.5 * line_spacing),
        (500, staff_y_start + 2 * line_spacing),
    ]

    # Draw second group
    stem_tops2 = []
    for x, y in group2_notes:
        y = int(y)
        draw_note_head(image, x, y, note_radius, filled=True)
        stem_x = x + note_radius - 2
        stem_top_y = y - stem_length
        draw_note_stem(image, stem_x, y, stem_length)
        stem_tops2.append((stem_x, stem_top_y))

    # Draw beam for second group
    beam_y2 = int(np.mean([y for _, y in stem_tops2]))
    draw_beam(image, stem_tops2[0][0], stem_tops2[-1][0], beam_y2, thickness=4)

    cv2.imwrite(filename, image)
    print(f"Generated sheet music with beamed notes: {filename}")
    return image


def create_comprehensive_test(filename="comprehensive_test.png"):
    """Create a comprehensive test with all features"""
    width, height = 1200, 400
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Staff parameters
    line_spacing = 20
    line_thickness = 3
    staff_y_start = 120
    x_start = 50
    x_end = width - 50

    # Draw staff lines
    create_staff_lines(image, staff_y_start, line_spacing, line_thickness, x_start, x_end)

    note_radius = 12
    stem_length = 45

    # Complex pattern: notes with accidentals, rests, and beamed notes
    x_pos = 150

    # Note with sharp
    draw_sharp(image, x_pos - 25, staff_y_start + 2 * line_spacing, size=8)
    draw_note_head(image, x_pos, staff_y_start + 2 * line_spacing, note_radius, filled=True)
    draw_note_stem(image, x_pos + note_radius - 2, staff_y_start + 2 * line_spacing, stem_length)

    x_pos += 80

    # Quarter rest
    draw_quarter_rest(image, x_pos, staff_y_start + 2 * line_spacing)

    x_pos += 80

    # Beamed group with flat
    beam_notes = []
    draw_flat(image, x_pos - 25, staff_y_start + 3 * line_spacing, size=10)

    for i, y_offset in enumerate([3, 2.5, 2, 1.5]):
        note_x = x_pos + i * 40
        note_y = staff_y_start + y_offset * line_spacing
        draw_note_head(image, note_x, int(note_y), note_radius, filled=True)
        stem_x = note_x + note_radius - 2
        stem_top = int(note_y - stem_length)
        draw_note_stem(image, stem_x, int(note_y), stem_length)
        beam_notes.append((stem_x, stem_top))

    # Draw beam
    beam_y = int(np.mean([y for _, y in beam_notes]))
    draw_beam(image, beam_notes[0][0], beam_notes[-1][0], beam_y, thickness=4)

    x_pos += 200

    # Half rest
    draw_half_rest(image, x_pos, staff_y_start + 2 * line_spacing, width=14)

    x_pos += 80

    # Note with natural
    draw_natural(image, x_pos - 25, staff_y_start + line_spacing, size=8)
    draw_note_head(image, x_pos, staff_y_start + line_spacing, note_radius, filled=True)
    draw_note_stem(image, x_pos + note_radius - 2, staff_y_start + line_spacing, stem_length)

    cv2.imwrite(filename, image)
    print(f"Generated comprehensive test image: {filename}")
    return image


def main():
    """Generate all advanced test images"""
    print("Generating advanced test images...\n")

    create_sheet_with_accidentals("examples/sheet_with_accidentals.png")
    create_sheet_with_rests("examples/sheet_with_rests.png")
    create_sheet_with_beamed_notes("examples/sheet_with_beamed_notes.png")
    create_comprehensive_test("examples/comprehensive_test.png")

    print("\nAll advanced test images generated successfully!")


if __name__ == "__main__":
    main()
