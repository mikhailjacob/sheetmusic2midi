"""Staff line detection for sheet music"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Staff:
    """Represents a musical staff (5 lines)"""
    lines: List[int]  # Y-coordinates of the 5 staff lines
    line_spacing: float  # Average spacing between lines
    x_start: int  # Starting x coordinate
    x_end: int  # Ending x coordinate

    @property
    def top(self) -> int:
        """Top boundary of the staff"""
        return self.lines[0]

    @property
    def bottom(self) -> int:
        """Bottom boundary of the staff"""
        return self.lines[-1]

    @property
    def height(self) -> int:
        """Total height of the staff"""
        return self.bottom - self.top


class StaffDetector:
    """Detects staff lines in sheet music images"""

    def __init__(self):
        self.staves: List[Staff] = []
        self.line_thickness: Optional[int] = None

    def detect_staff_lines(self, binary_image: np.ndarray) -> List[int]:
        """
        Detect horizontal staff lines using projection profile

        Args:
            binary_image: Binary image with staff lines

        Returns:
            List of y-coordinates of detected lines
        """
        # Calculate horizontal projection (sum of white pixels in each row)
        horizontal_projection = np.sum(binary_image, axis=1)

        # Normalize projection
        height = binary_image.shape[0]
        max_val = np.max(horizontal_projection)
        if max_val > 0:
            horizontal_projection = horizontal_projection / max_val

        # Find peaks in the projection (these correspond to staff lines)
        # Staff lines will have high values in the projection
        threshold = 0.7
        potential_lines = []

        for y in range(height):
            if horizontal_projection[y] > threshold:
                potential_lines.append(y)

        # Group consecutive y-values and take the center of each group
        line_positions = []
        if potential_lines:
            current_group = [potential_lines[0]]

            for y in potential_lines[1:]:
                if y - current_group[-1] <= 2:  # Lines within 2 pixels are same line
                    current_group.append(y)
                else:
                    # Save center of current group
                    line_positions.append(int(np.mean(current_group)))
                    current_group = [y]

            # Don't forget the last group
            line_positions.append(int(np.mean(current_group)))

        return line_positions

    def estimate_line_thickness(self, binary_image: np.ndarray,
                               line_positions: List[int]) -> int:
        """
        Estimate the thickness of staff lines

        Args:
            binary_image: Binary image
            line_positions: Y-coordinates of detected lines

        Returns:
            Estimated line thickness in pixels
        """
        if not line_positions:
            return 2  # Default thickness

        thicknesses = []
        for y in line_positions[:5]:  # Check first few lines
            # Count consecutive white pixels vertically around this line
            start_y = max(0, y - 5)
            end_y = min(binary_image.shape[0], y + 5)

            # Sample from middle of image
            x = binary_image.shape[1] // 2

            thickness = 0
            for check_y in range(start_y, end_y):
                if binary_image[check_y, x] > 0:
                    thickness += 1

            if thickness > 0:
                thicknesses.append(thickness)

        if thicknesses:
            self.line_thickness = int(np.median(thicknesses))
        else:
            self.line_thickness = 2

        return self.line_thickness

    def group_lines_into_staves(self, line_positions: List[int],
                                binary_image: np.ndarray) -> List[Staff]:
        """
        Group detected lines into musical staves (sets of 5 lines)

        Args:
            line_positions: Y-coordinates of all detected lines
            binary_image: Binary image for determining x extent

        Returns:
            List of Staff objects
        """
        if len(line_positions) < 5:
            return []

        staves = []
        i = 0

        while i <= len(line_positions) - 5:
            # Take next 5 lines
            staff_lines = line_positions[i:i+5]

            # Calculate spacing between these lines
            spacings = [staff_lines[j+1] - staff_lines[j] for j in range(4)]
            avg_spacing = np.mean(spacings)
            spacing_std = np.std(spacings)

            # Check if spacing is consistent (should be for a real staff)
            if spacing_std < avg_spacing * 0.3:  # 30% tolerance
                # Find x extent of this staff
                staff_top = staff_lines[0]
                staff_bottom = staff_lines[4]

                # Look for where staff starts and ends horizontally
                staff_region = binary_image[staff_top:staff_bottom+1, :]
                horizontal_sum = np.sum(staff_region, axis=0)

                # Find first and last positions with significant content
                threshold = np.max(horizontal_sum) * 0.1
                x_positions = np.where(horizontal_sum > threshold)[0]

                if len(x_positions) > 0:
                    x_start = int(x_positions[0])
                    x_end = int(x_positions[-1])

                    staff = Staff(
                        lines=staff_lines,
                        line_spacing=avg_spacing,
                        x_start=x_start,
                        x_end=x_end
                    )
                    staves.append(staff)

                i += 5  # Move to next potential staff
            else:
                i += 1  # Try next line

        self.staves = staves
        return staves

    def detect_staves(self, binary_image: np.ndarray) -> List[Staff]:
        """
        Complete staff detection pipeline

        Args:
            binary_image: Preprocessed binary image

        Returns:
            List of detected Staff objects
        """
        # Detect all horizontal lines
        line_positions = self.detect_staff_lines(binary_image)

        # Estimate line thickness
        self.estimate_line_thickness(binary_image, line_positions)

        # Group into staves
        staves = self.group_lines_into_staves(line_positions, binary_image)

        print(f"Detected {len(staves)} staff/staves")
        for idx, staff in enumerate(staves):
            print(f"  Staff {idx+1}: lines at {staff.lines}, "
                  f"spacing={staff.line_spacing:.1f}px")

        return staves

    def remove_staff_lines(self, binary_image: np.ndarray) -> np.ndarray:
        """
        Remove staff lines from image to isolate symbols

        Args:
            binary_image: Binary image with staff lines

        Returns:
            Image with staff lines removed
        """
        result = binary_image.copy()

        if self.line_thickness is None:
            self.line_thickness = 2

        for staff in self.staves:
            for line_y in staff.lines:
                # Remove horizontal line
                top = max(0, line_y - self.line_thickness)
                bottom = min(binary_image.shape[0], line_y + self.line_thickness + 1)
                result[top:bottom, staff.x_start:staff.x_end] = 0

        return result

    def get_staff_position(self, y: int) -> Tuple[Optional[Staff], Optional[int]]:
        """
        Determine which staff a y-coordinate belongs to and position within staff

        Args:
            y: Y-coordinate

        Returns:
            Tuple of (Staff object, position) where position is:
            - Line positions: 0-4 for the 5 lines
            - Space positions: 0.5, 1.5, 2.5, 3.5 for spaces between lines
            - None if not on a staff
        """
        for staff in self.staves:
            if staff.top <= y <= staff.bottom:
                # Normalize position within staff
                relative_y = y - staff.top
                position = relative_y / staff.line_spacing

                return staff, position

        return None, None
