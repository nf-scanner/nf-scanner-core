"""
Interface central para extração de NFSe.
"""

import os
import mimetypes
from typing import Optional, Dict, Any, List, Union

from nf_scanner_core.extractors.pdf_extractor import PDFExtractor
from nf_scanner_core.extractors.image_extractor import ImageExtractor
from nf_scanner_core.models import NFSe


class NFExtractor:
    """
    Classe principal para extração de dados de NFSe.

    Detecta automaticamente o tipo de arquivo (PDF ou imagem) e utiliza o extrator apropriado.
    """

    def __init__(self, extract_path: str, output_dir: Optional[str] = None):
        """
        Inicializa o extrator de NFSe com o caminho do arquivo e caminho de saída opcional.

        Args:
            extract_path: Caminho para o arquivo (PDF ou imagem) contendo a NFSe
            output_dir: Caminho de saída opcional para salvar os resultados (se None, usa o mesmo diretório do arquivo)
        """
        self.SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
        self.SUPPORTED_PDF_TYPES = ["application/pdf"]
        self.SUPPORTED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]

        self.extract_path = extract_path
        self.output_dir = output_dir if output_dir else os.path.dirname(extract_path)
        self.file_type = self._determine_file_type()
        if self.file_type == "pdf":
            self.extractor = PDFExtractor(self.extract_path, self.output_dir)
        elif self.file_type == "image":
            self.extractor = ImageExtractor(self.extract_path, self.output_dir)
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
        text = self.extractor._extract_text()
        from nf_scanner_core.parsers.nfse_parser import NFSeParser

        return NFSeParser.parse(text)

    def extract_and_save(self) -> str:
        """
        Extrai dados da NFSe do arquivo e salva em formato JSON.

        Returns:
            str: Caminho do arquivo JSON salvo
        """
        return self.extractor.extract_and_save()

    def get_file_type(self) -> str:
        """
        Retorna o tipo de arquivo detectado.

        Returns:
            str: Tipo de arquivo ('pdf' ou 'image')
        """
        return self.file_type


# Código de exemplo
if __name__ == "__main__":
    file_path = "./test_inputs/NFSe_ficticia_layout_completo.pdf"

    # Cria o extrator que automaticamente detecta o tipo de arquivo
    extractor = NFExtractor(file_path)

    # Extrai e salva os dados da NFSe
    json_path = extractor.extract_and_save()
    print(f"Dados da NFSe salvos em: {json_path}")
    print(f"Tipo de arquivo: {extractor.get_file_type()}")
