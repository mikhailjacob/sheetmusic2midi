"""
Generate a simple synthetic sheet music image for testing

This creates a basic sheet music image with staff lines and note heads
that can be used to test the sheetmusic2midi converter.
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
    # Draw an ellipse for the note head
    axes = (radius, int(radius * 0.7))  # Slightly oval
    angle = -20  # Tilt the note head
    if filled:
        cv2.ellipse(image, (x, y), axes, angle, 0, 360, 0, -1)
    else:
        cv2.ellipse(image, (x, y), axes, angle, 0, 360, 0, 2)


def draw_note_stem(image, x, y, length, thickness=2):
    """Draw a note stem"""
    cv2.line(image, (x, y), (x, y - length), 0, thickness)


def create_simple_sheet_music(width=800, height=400, filename="sample_sheet_music.png"):
    """
    Create a simple sheet music image with a scale (C D E F G A B C)

    Args:
        width: Image width in pixels
        height: Image height in pixels
        filename: Output filename
    """
    # Create white background
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Staff parameters - increased for better detection
    line_spacing = 20
    line_thickness = 3
    staff_y_start = 120
    x_start = 50
    x_end = width - 50

    # Draw staff lines
    create_staff_lines(image, staff_y_start, line_spacing, line_thickness, x_start, x_end)

    # Note parameters - increased for better detection
    note_radius = 12
    stem_length = 45
    note_spacing = 80
    start_x = 150

    # Draw a C major scale: C D E F G A B C
    # Staff positions (from bottom to top):
    # E4 (line 0), F4 (space 0.5), G4 (line 1), A4 (space 1.5),
    # B4 (line 2), C5 (space 2.5), D5 (line 3), E5 (space 3.5), F5 (line 4)

    # For C major scale starting from C4 (below staff):
    notes = [
        # (x_offset, y_position, has_stem, filled)
        # C4 - on ledger line below staff
        (0, staff_y_start + 4 * line_spacing + line_spacing, True, True),
        # D4 - below bottom line
        (1, staff_y_start + 4 * line_spacing + line_spacing // 2, True, True),
        # E4 - on bottom line
        (2, staff_y_start + 4 * line_spacing, True, True),
        # F4 - first space
        (3, staff_y_start + 3.5 * line_spacing, True, True),
        # G4 - second line
        (4, staff_y_start + 3 * line_spacing, True, True),
        # A4 - second space
        (5, staff_y_start + 2.5 * line_spacing, True, True),
        # B4 - third line
        (6, staff_y_start + 2 * line_spacing, True, True),
        # C5 - third space
        (7, staff_y_start + 1.5 * line_spacing, True, True),
    ]

    for i, (x_offset, y_pos, has_stem, filled) in enumerate(notes):
        x = start_x + x_offset * note_spacing
        y = int(y_pos)

        # Draw note head
        draw_note_head(image, x, y, note_radius, filled)

        # Draw stem if needed
        if has_stem:
            stem_x = x + note_radius - 2
            draw_note_stem(image, stem_x, y, stem_length)

    # Draw a treble clef symbol (simplified version - just a vertical line with a curve)
    # In a real implementation, you'd draw a proper treble clef
    clef_x = 70
    clef_y_start = staff_y_start
    clef_y_end = staff_y_start + 4 * line_spacing

    # Simple vertical line as placeholder for clef
    cv2.line(image, (clef_x, clef_y_start), (clef_x, clef_y_end), 0, 3)
    cv2.circle(image, (clef_x, staff_y_start + 2 * line_spacing), 8, 0, 2)

    # Save image
    cv2.imwrite(filename, image)
    print(f"Generated test sheet music image: {filename}")
    print(f"  Size: {width}x{height} pixels")
    print(f"  Staff line spacing: {line_spacing} pixels")
    print(f"  Contains: C major scale (C4 to C5)")

    return image


def create_complex_sheet_music(filename="complex_sheet_music.png"):
    """Create a more complex sheet music example"""
    width = 1000
    height = 600
    image = np.ones((height, width), dtype=np.uint8) * 255

    line_spacing = 15
    line_thickness = 2

    # Create two staves
    staff1_y = 100
    staff2_y = 350

    x_start = 50
    x_end = width - 50

    # Draw both staves
    create_staff_lines(image, staff1_y, line_spacing, line_thickness, x_start, x_end)
    create_staff_lines(image, staff2_y, line_spacing, line_thickness, x_start, x_end)

    # Add some notes to first staff
    note_positions_1 = [
        (150, staff1_y + 2 * line_spacing, True, True),
        (250, staff1_y + 1.5 * line_spacing, True, True),
        (350, staff1_y + 3 * line_spacing, True, True),
        (450, staff1_y + 2.5 * line_spacing, True, True),
        (550, staff1_y + line_spacing, True, False),  # Half note
    ]

    # Add notes to second staff
    note_positions_2 = [
        (150, staff2_y + 3 * line_spacing, True, True),
        (250, staff2_y + 4 * line_spacing, True, True),
        (350, staff2_y + 2 * line_spacing, True, True),
        (450, staff2_y + 1.5 * line_spacing, True, True),
    ]

    note_radius = 10
    stem_length = 40

    # Draw notes on first staff
    for x, y, has_stem, filled in note_positions_1:
        draw_note_head(image, x, int(y), note_radius, filled)
        if has_stem:
            draw_note_stem(image, x + note_radius - 2, int(y), stem_length)

    # Draw notes on second staff
    for x, y, has_stem, filled in note_positions_2:
        draw_note_head(image, x, int(y), note_radius, filled)
        if has_stem:
            draw_note_stem(image, x + note_radius - 2, int(y), stem_length)

    cv2.imwrite(filename, image)
    print(f"\nGenerated complex test image: {filename}")
    print(f"  Contains: 2 staves with multiple notes")

    return image


def main():
    """Generate test images"""
    print("Generating test sheet music images...\n")

    # Create simple test image
    create_simple_sheet_music(
        width=800,
        height=400,
        filename="examples/sample_sheet_music.png"
    )

    # Create more complex test image
    create_complex_sheet_music("examples/complex_sheet_music.png")

    print("\nTest images generated successfully!")
    print("You can now use these with sheetmusic2midi converter.")


if __name__ == "__main__":
    main()
