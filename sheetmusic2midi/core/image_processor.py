"""Image preprocessing for sheet music OCR"""

import cv2
import numpy as np
from typing import Tuple, Optional


class ImageProcessor:
    """Handles image loading and preprocessing for sheet music recognition"""

    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.binary_image = None

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from file path

        Args:
            image_path: Path to the sheet music image

        Returns:
            Loaded image as numpy array
        """
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Could not load image from {image_path}")
        return self.original_image

    def preprocess(self, image: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Preprocess the image for better staff and symbol detection

        Args:
            image: Input image (uses loaded image if None)

        Returns:
            Preprocessed grayscale image
        """
        if image is None:
            if self.original_image is None:
                raise ValueError("No image loaded. Call load_image first.")
            image = self.original_image

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Apply slight Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        self.processed_image = blurred
        return blurred

    def binarize(self, image: Optional[np.ndarray] = None,
                 threshold_method: str = 'adaptive') -> np.ndarray:
        """
        Convert image to binary (black and white)

        Args:
            image: Input grayscale image (uses processed image if None)
            threshold_method: 'adaptive' or 'otsu' or 'simple'

        Returns:
            Binary image
        """
        if image is None:
            if self.processed_image is None:
                raise ValueError("No processed image. Call preprocess first.")
            image = self.processed_image

        if threshold_method == 'adaptive':
            # Adaptive thresholding works well for varying lighting
            binary = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 15, 10
            )
        elif threshold_method == 'otsu':
            # Otsu's method automatically finds optimal threshold
            _, binary = cv2.threshold(
                image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
        else:  # simple
            _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

        self.binary_image = binary
        return binary

    def remove_noise(self, binary_image: Optional[np.ndarray] = None,
                     kernel_size: int = 2) -> np.ndarray:
        """
        Remove small noise from binary image using morphological operations

        Args:
            binary_image: Input binary image (uses binary image if None)
            kernel_size: Size of morphological kernel

        Returns:
            Denoised binary image
        """
        if binary_image is None:
            if self.binary_image is None:
                raise ValueError("No binary image. Call binarize first.")
            binary_image = self.binary_image

        # Remove small noise
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        opened = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)

        return opened

    def deskew(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Detect and correct image skew/rotation

        Args:
            image: Input binary image

        Returns:
            Tuple of (deskewed image, rotation angle in degrees)
        """
        # Find all non-zero points (staff lines and symbols)
        coords = np.column_stack(np.where(image > 0))

        # Calculate rotation angle using minimum area rectangle
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]

            # Correct the angle
            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = angle - 90

            # Rotate image
            if abs(angle) > 0.5:  # Only rotate if significant skew
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    image, M, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
                return rotated, angle

        return image, 0.0

    def full_preprocessing_pipeline(self, image_path: str) -> np.ndarray:
        """
        Complete preprocessing pipeline from image path to clean binary image

        Args:
            image_path: Path to sheet music image

        Returns:
            Preprocessed binary image ready for staff/symbol detection
        """
        # Load image
        self.load_image(image_path)

        # Preprocess
        processed = self.preprocess()

        # Binarize
        binary = self.binarize(processed)

        # Remove noise
        denoised = self.remove_noise(binary)

        # Deskew
        deskewed, angle = self.deskew(denoised)

        if abs(angle) > 0.5:
            print(f"Image was rotated by {angle:.2f} degrees")

        return deskewed
