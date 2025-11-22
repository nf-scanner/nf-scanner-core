"""
Módulo de extração de texto de arquivos de imagem para NF-Scanner-Core.

Este módulo fornece a interface para extrair texto de arquivos de imagem utilizando Tesseract.
"""

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

from nf_scanner_core.models import NFSe
from nf_scanner_core.parsers.ai_nfse_parser import AINFSeParser
from nf_scanner_core.parsers.nfse_parser import NFSeParser


class ImageExtractor:
    """
    Classe responsável por extrair texto e dados estruturados de arquivos de imagem.
    """

    def __init__(self, image_path: str, ai_parse: bool = False):
        """
        Inicializa o extrator de imagem com o caminho para o arquivo de imagem.

        Args:
            image_path: Caminho para o arquivo de imagem
        """
        self.image_path = image_path
        self.ai_parse = ai_parse

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Pré-processa a imagem para melhorar a qualidade do OCR.

        Implementa várias técnicas recomendadas pela documentação do Tesseract, por exemplo:
        - Redimensionamento (rescaling)
        - Binarização (thresholding)
        - Remoção de ruído

        Args:
            image: Imagem original em formato PIL

        Returns:
            Image.Image: Imagem processada para melhor qualidade de OCR
        """

        # Converte para RGB se for RGBA (remove canal alpha)
        if image.mode == "RGBA":
            image = image.convert("RGB")
        img_np = np.array(image)

        # Converte para escala de cinza
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np

        # Redimensiona para garantir boa resolução
        # Tesseract funciona melhor com pelo menos 300 DPI
        height, width = gray.shape
        if width < 1000:  # Um heurística simples para imagens pequenas
            scale_factor = 1500 / width
            gray = cv2.resize(
                gray,
                None,
                fx=scale_factor,
                fy=scale_factor,
                interpolation=cv2.INTER_CUBIC,
            )

        # Aplica binarização adaptativa (melhora contraste do texto)
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Remoção de ruído com filtro morfológico
        kernel = np.ones((1, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        return Image.fromarray(binary)

    def _extract_text(self) -> str:
        """
        Extrai o texto de um arquivo de imagem usando Tesseract OCR.

        Returns:
            str: Texto extraído do arquivo de imagem

        Raises:
            FileNotFoundError: Se o arquivo de imagem não for encontrado
            RuntimeError: Se houver um erro ao processar a imagem
        """
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(
                f"O arquivo de imagem não foi encontrado: {self.image_path}"
            )

        try:
            # Abre a imagem usando PIL
            image = Image.open(self.image_path)

            # Pré-processa a imagem para melhorar a qualidade do OCR
            processed_image = self._preprocess_image(image)

            # Adiciona configurações adicionais para o Tesseract
            config = "--psm 6 --oem 1"

            # Extrai o texto usando pytesseract
            extracted_text = pytesseract.image_to_string(
                processed_image, lang="por", config=config
            )

            return extracted_text.strip()

        except Exception as e:
            raise RuntimeError(f"Erro ao extrair o texto da imagem: {str(e)}")

    def extract(self) -> NFSe:
        """
        Extrai dados de uma NFSe a partir de uma imagem.

        Returns:
            NFSe: Objeto NFSe com os dados extraídos
        """
        text = self._extract_text()
        if self.ai_parse:
            return AINFSeParser.parse(text)

        return NFSeParser.parse(text)
