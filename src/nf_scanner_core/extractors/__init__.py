"""
Módulo de extractores para NF-Scanner-Core.

Este módulo contém as implementações de extractores para diferentes tipos de arquivo.
"""

from nf_scanner_core.extractors.pdf_extractor import PDFExtractor
from nf_scanner_core.extractors.image_extractor import ImageExtractor
from nf_scanner_core.extractors.ai_image_extractor import AIImageExtractor

__all__ = ["PDFExtractor", "ImageExtractor", "AIImageExtractor"]
