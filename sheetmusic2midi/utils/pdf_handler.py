"""PDF handling utilities for sheet music conversion"""

import os
import tempfile
from typing import List, Optional

try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class PDFHandler:
    """Handles PDF file operations for sheet music conversion"""

    @staticmethod
    def is_pdf_supported() -> bool:
        """
        Check if PDF support is available

        Returns:
            True if pdf2image is installed, False otherwise
        """
        return PDF_SUPPORT

    @staticmethod
    def pdf_to_images(pdf_path: str, dpi: int = 300, temp_dir: Optional[str] = None) -> List[str]:
        """
        Convert PDF pages to image files

        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for image conversion (default 300 DPI for good quality)
            temp_dir: Directory for temporary image files (default: system temp)

        Returns:
            List of paths to generated image files (one per page)

        Raises:
            ImportError: If pdf2image is not installed
            FileNotFoundError: If PDF file doesn't exist
        """
        if not PDF_SUPPORT:
            raise ImportError(
                "PDF support requires pdf2image library. "
                "Install it with: pip install pdf2image"
            )

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Create temporary directory if not specified
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="sheetmusic2midi_")

        print(f"Converting PDF to images (DPI: {dpi})...")

        # Convert PDF pages to images
        try:
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                output_folder=temp_dir,
                fmt='png'
            )
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF: {e}")

        # Save images and collect paths
        image_paths = []
        for i, image in enumerate(images, 1):
            image_path = os.path.join(temp_dir, f"page_{i:03d}.png")
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
            print(f"  Extracted page {i}/{len(images)}")

        print(f"Successfully extracted {len(image_paths)} page(s) from PDF")

        return image_paths

    @staticmethod
    def cleanup_temp_images(image_paths: List[str]) -> None:
        """
        Clean up temporary image files

        Args:
            image_paths: List of image file paths to delete
        """
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Warning: Could not delete temporary file {path}: {e}")

        # Try to remove the directory if empty
        if image_paths:
            try:
                temp_dir = os.path.dirname(image_paths[0])
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception:
                pass  # Ignore errors during cleanup
