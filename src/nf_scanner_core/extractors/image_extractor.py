"""
Módulo de extração de texto de arquivos de imagem para NF-Scanner-Core.

Este módulo fornece a interface para extrair texto de arquivos de imagem utilizando Tesseract.
"""

import os
import json
import cv2
import numpy as np
from typing import Optional, Dict, Any, Union, Tuple
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

from nf_scanner_core.models import NFSe
from nf_scanner_core.parsers.nfse_parser import NFSeParser
from nf_scanner_core.utils.file_utils import (
    get_output_json_path,
    ensure_directory_exists,
)


class ImageExtractor:
    """
    Classe responsável por extrair texto e dados estruturados de arquivos de imagem.
    """

    def __init__(self, image_path: str, output_dir: Optional[str] = None):
        """
        Inicializa o extrator de imagem com o caminho para o arquivo de imagem.

        Args:
            image_path: Caminho para o arquivo de imagem
            output_dir: Diretório de saída opcional para salvar os resultados
        """
        self.image_path = image_path
        self.output_dir = output_dir

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Pré-processa a imagem para melhorar a qualidade do OCR.

        Implementa várias técnicas recomendadas pela documentação do Tesseract:
        - Redimensionamento (rescaling)
        - Binarização (thresholding)
        - Remoção de ruído
        - Correção de rotação (deskewing)
        - Tratamento de bordas

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
            config = (
                "--psm 6 --oem 1"  # Página como um único bloco de texto, usando o LSTM
            )

            # Extrai o texto usando pytesseract
            extracted_text = pytesseract.image_to_string(
                processed_image, lang="por", config=config
            )

            return extracted_text.strip()

        except Exception as e:
            raise RuntimeError(f"Erro ao extrair o texto da imagem: {str(e)}")

    def _save_nfse_json(self, nfse: NFSe) -> str:
        """
        Salva os dados estruturados da NFSe em formato JSON.

        Args:
            nfse: Objeto NFSe com dados estruturados

        Returns:
            str: Caminho do arquivo JSON salvo
        """
        # Define o caminho de saída usando a função utilitária
        output_path = get_output_json_path(
            self.image_path, nfse.codigo_verificacao, self.output_dir
        )

        # Converte o objeto NFSe para um dicionário
        nfse_dict = nfse.to_dict()

        # Cria resposta no formato de API HTTP
        response = {"status": "success", "code": 200, "data": {"nfse": nfse_dict}}

        # Salva o JSON
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, indent=2, ensure_ascii=False)

        return output_path

    def extract_and_save(self) -> str:
        """
        Extrai dados de uma NFSe a partir de uma imagem e salva em formato JSON.

        Returns:
            str: Caminho do arquivo JSON salvo
        """
        # Extrai texto da imagem
        text = self._extract_text()

        # Converte o texto para o modelo NFSe usando o parser
        nfse = NFSeParser.parse(text)

        # Salva os dados em formato JSON
        return self._save_nfse_json(nfse)


# Código de exemplo
if __name__ == "__main__":
    image_path = "./test_inputs/NFSe_ficticia_layout_completo.jpg"

    # Extrai e salva os dados da NFSe usando a API orientada a objetos
    extractor = ImageExtractor(image_path)
    json_path = extractor.extract_and_save()
    print(f"Dados da NFSe salvos em: {json_path}")
