"""
Interface central para extração de NFSe.
"""

import os
import mimetypes

from nf_scanner_core.extractors.pdf_extractor import PDFExtractor
from nf_scanner_core.extractors.image_extractor import ImageExtractor
from nf_scanner_core.extractors.ai_image_extractor import AIImageExtractor
from nf_scanner_core.models import NFSe


class NFExtractor:
    """
    Classe principal para extração de dados de NFSe.

    Detecta automaticamente o tipo de arquivo (PDF ou imagem) e utiliza o extrator apropriado.
    """

    def __init__(
        self, extract_path: str, ai_extraction: bool = False, ai_parse: bool = False
    ):
        """
        Inicializa o extrator de NFSe com o caminho do arquivo e caminho de saída opcional.

        Args:
            extract_path: Caminho para o arquivo (PDF ou imagem) contendo a NFSe
            ai_extraction: Se True, usa IA para extração; se False, usa OCR
            ai_parse: Se True, usa IA para parsear os dados; se False, usa parseamento manual
        """
        self.SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
        self.SUPPORTED_PDF_TYPES = ["application/pdf"]
        self.SUPPORTED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]

        self.extract_path = extract_path
        self.ai_extraction = ai_extraction
        self.ai_parse = ai_parse
        self.file_type = self._determine_file_type()
        if self.file_type == "pdf" and self.ai_extraction:
            raise ValueError(
                "IA para extração de PDF não é eficiente pois a extração funciona perfeitamente com o PyMuPDF."
            )

        if self.file_type == "pdf":
            self.extractor = PDFExtractor(self.extract_path, self.ai_parse)
        elif self.file_type == "image" and not self.ai_extraction:
            self.extractor = ImageExtractor(self.extract_path, self.ai_parse)
        elif self.file_type == "image" and self.ai_extraction:
            self.extractor = AIImageExtractor(
                self.extract_path
            )  # Ao utilizar a IA para extração, não é necessário usar parser.
        else:
            raise ValueError(
                f"Tipo de arquivo não suportado: {self.extract_path}. "
                f"Extensões suportadas: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

    def _determine_file_type(self) -> str:
        """
        Determina o tipo de arquivo baseado na extensão ou tipo MIME.

        Returns:
            str: Tipo de arquivo ('pdf', 'image' ou None se não suportado)
        """
        if not os.path.exists(self.extract_path):
            raise FileNotFoundError(
                f"O arquivo não foi encontrado: {self.extract_path}"
            )

        mime_type, _ = mimetypes.guess_type(self.extract_path)
        if mime_type in self.SUPPORTED_PDF_TYPES:
            return "pdf"
        elif mime_type in self.SUPPORTED_IMAGE_TYPES:
            return "image"

        # Não foi possível determinar o tipo de arquivo
        return None

    def extract(self) -> NFSe:
        """
        Extrai dados da NFSe do arquivo.

        Returns:
            NFSe: Objeto contendo os dados estruturados da NFSe
        """
        return self.extractor.extract()
