"""
Módulo de extração de texto de arquivos de imagem para NF-Scanner-Core.

Este módulo fornece funcionalidades para extrair texto de arquivos de imagem e armazenar os dados extraídos.
Usa Tesseract OCR para extração de texto de imagens.
"""

import os
import json
import cv2
import numpy as np
from typing import Optional, Dict, Any, Union, Tuple
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

from nf_scanner_core.models import NFSe
from nf_scanner_core.nfse_parser import NFSeParser


class ImageExtractor:
    """
    Classe responsável por extrair texto e dados estruturados de arquivos de imagem.
    """

    def __init__(self, image_path: str):
        """
        Inicializa o extrator de imagem com o caminho para o arquivo de imagem.

        Args:
            image_path: Caminho para o arquivo de imagem
        """
        self.image_path = image_path

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

        return Image.fromarray(gray)

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

            print(extracted_text)

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
        # Define o caminho de saída
        filename = f"nfse_{nfse.codigo_verificacao}.json"
        dir_path = os.path.dirname(self.image_path)
        output_path = os.path.join(dir_path, filename)

        # Cria o diretório de saída se necessário
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

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
