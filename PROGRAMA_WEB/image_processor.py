#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO DE PROCESSAMENTO DE IMAGENS
Funções para aplicar overlays, texto e salvar imagens com qualidade controlada
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict, List


class ImageProcessor:
    """Classe para processamento de imagens"""

    # Formatos suportados
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.webp'}

    def __init__(self):
        """Inicializa o processador"""
        self.default_font = None
        self.load_default_font()

    def load_default_font(self):
        """Carrega fonte padrão para texto"""
        try:
            # Tentar carregar fonte do sistema
            if os.name == 'nt':  # Windows
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf",
                    "C:/Windows/Fonts/segoeui.ttf"
                ]
            else:  # Linux/Mac (incluindo Streamlit Cloud)
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    # Fontes alternativas para ambientes cloud
                    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
                    "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"
                ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.default_font = font_path
                    print(f"✅ Fonte carregada: {font_path}")
                    break

            # Se nenhuma fonte foi encontrada, não é erro crítico
            if not self.default_font:
                print("⚠️ Nenhuma fonte TTF encontrada. Usando fonte padrão do PIL.")

        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível carregar fonte padrão: {e}")

    def get_image_files(self, folder: str) -> List[str]:
        """
        Retorna lista de arquivos de imagem em uma pasta

        Args:
            folder: Caminho da pasta

        Returns:
            Lista de caminhos completos de imagens
        """
        image_files = []

        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)

                if os.path.isfile(file_path):
                    ext = Path(filename).suffix.lower()
                    if ext in self.SUPPORTED_FORMATS:
                        image_files.append(file_path)

        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")

        return sorted(image_files)

    def process_image(
        self,
        base_image_path: str,
        overlay_path: str,
        text_config: Optional[Dict] = None,
        keep_overlay_size: bool = False
    ) -> Image.Image:
        """
        Processa uma imagem aplicando overlay e texto

        Args:
            base_image_path: Caminho da imagem base
            overlay_path: Caminho do overlay/moldura
            text_config: Configurações de texto (opcional)

        Returns:
            Imagem processada
        """
        # Carregar imagem base
        base = Image.open(base_image_path)

        # Aplicar overlay
        overlay = Image.open(overlay_path)
        result = self.apply_overlay(base, overlay, keep_overlay_size)

        # Aplicar texto se configurado
        if text_config:
            result = self.add_text_overlay(result, text_config)

        return result

    def apply_overlay(
        self,
        base_image: Image.Image,
        overlay_image: Image.Image,
        keep_original_size: bool = False
    ) -> Image.Image:
        """
        Combina base e overlay com opção de manter a resolução original do overlay.
        ⚡ OTIMIZADO: Assume que imagens já estão em RGBA (convertidas antes do loop)
        """
        # ⚡ OTIMIZAÇÃO: Não fazer cópia se já está no formato correto
        base = base_image
        overlay = overlay_image

        if not keep_original_size:
            # Verificar se já está no tamanho correto (evita resize desnecessário)
            if overlay.size == base.size:
                return Image.alpha_composite(base, overlay)

            # Usar LANCZOS para qualidade, mas com otimização
            overlay_resized = overlay.resize(base.size, Image.Resampling.LANCZOS)
            return Image.alpha_composite(base, overlay_resized)

        # Manter resolução original do overlay SEM ACHATAR a imagem base
        # Usar comportamento "cover" - expande até preencher completamente

        # Criar canvas do tamanho do overlay
        canvas = Image.new('RGBA', overlay.size, (0, 0, 0, 0))

        # Calcular tamanho da base mantendo proporções (cover - preenche tudo)
        base_ratio = base.width / base.height
        overlay_ratio = overlay.width / overlay.height

        if base_ratio > overlay_ratio:
            # Base é mais larga: ajustar pela ALTURA (para cobrir tudo)
            new_height = overlay.height
            new_width = int(overlay.height * base_ratio)
        else:
            # Base é mais alta: ajustar pela LARGURA (para cobrir tudo)
            new_width = overlay.width
            new_height = int(overlay.width / base_ratio)

        # Redimensionar base mantendo proporções
        base_resized = base.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Centralizar base no canvas (pode cortar as bordas)
        x_offset = (overlay.width - new_width) // 2
        y_offset = (overlay.height - new_height) // 2
        canvas.paste(base_resized, (x_offset, y_offset))

        # Aplicar overlay por cima
        return Image.alpha_composite(canvas, overlay)

    def add_text_overlay(self, image: Image.Image, config: Dict) -> Image.Image:
        """
        Adiciona texto sobre a imagem

        Args:
            image: Imagem PIL
            config: Dicionário com configurações de texto

        Returns:
            Imagem com texto
        """
        # Criar cópia para não modificar original
        img = image.copy()

        # Criar camada de desenho
        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Carregar fonte
        font_size = config.get('size', 40)
        try:
            if self.default_font:
                font = ImageFont.truetype(self.default_font, font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Obter texto
        text = config.get('text', '')
        if not text:
            return img

        # Calcular tamanho do texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calcular posição
        position = config.get('position', 'superior_direita')
        padding = 20

        if position == 'superior_esquerda':
            x = padding
            y = padding
        elif position == 'superior_direita':
            x = img.width - text_width - padding
            y = padding
        elif position == 'inferior_esquerda':
            x = padding
            y = img.height - text_height - padding
        elif position == 'inferior_direita':
            x = img.width - text_width - padding
            y = img.height - text_height - padding
        elif position == 'centro':
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        else:
            x = padding
            y = padding

        # Desenhar fundo se habilitado
        if config.get('bg_enabled', False):
            bg_color = config.get('bg_color', '#000000')
            bg_opacity = config.get('bg_opacity', 70)

            # Converter cor hex para RGB
            bg_rgb = self.hex_to_rgb(bg_color)
            bg_alpha = int(255 * (bg_opacity / 100))

            # Adicionar padding ao fundo
            bg_padding = 15
            bg_rect = [
                x - bg_padding,
                y - bg_padding,
                x + text_width + bg_padding,
                y + text_height + bg_padding
            ]

            draw.rectangle(bg_rect, fill=(*bg_rgb, bg_alpha))

        # Desenhar texto
        text_color = config.get('color', '#FFFFFF')
        text_opacity = config.get('opacity', 100)

        # Converter cor hex para RGB
        text_rgb = self.hex_to_rgb(text_color)
        text_alpha = int(255 * (text_opacity / 100))

        draw.text((x, y), text, font=font, fill=(*text_rgb, text_alpha))

        # Combinar com imagem original
        result = Image.alpha_composite(img, txt_layer)

        return result

    def hex_to_rgb(self, hex_color: str) -> tuple:
        """
        Converte cor hexadecimal para RGB

        Args:
            hex_color: Cor em formato hex (#RRGGBB)

        Returns:
            Tupla (R, G, B)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def save_image(
        self,
        image: Image.Image,
        original_path: str,
        dest_folder: str,
        output_format: Optional[str] = None,
        quality: int = 95,
        prefix: str = "",
        suffix: str = ""
    ) -> str:
        """
        Salva imagem processada

        Args:
            image: Imagem PIL
            original_path: Caminho da imagem original
            dest_folder: Pasta de destino
            output_format: Formato de saída (None = manter original)
            quality: Qualidade (1-100) para WEBP e JPG
            prefix: Prefixo para nome do arquivo
            suffix: Sufixo para nome do arquivo

        Returns:
            Caminho do arquivo salvo
        """
        # Obter nome e extensão originais
        original_name = Path(original_path).stem
        original_ext = Path(original_path).suffix.lower()

        # Determinar formato de saída
        if output_format:
            ext = f".{output_format.lower()}"
        else:
            ext = original_ext

        # Construir novo nome
        new_name = f"{prefix}{original_name}{suffix}{ext}"
        output_path = os.path.join(dest_folder, new_name)

        # Preparar imagem para salvamento
        save_image = image

        # Converter para RGB se necessário (JPG não suporta transparência)
        if ext in ['.jpg', '.jpeg']:
            if save_image.mode in ('RGBA', 'LA', 'P'):
                # Criar fundo branco
                background = Image.new('RGB', save_image.size, (255, 255, 255))
                if save_image.mode == 'P':
                    save_image = save_image.convert('RGBA')
                background.paste(save_image, mask=save_image.split()[-1])
                save_image = background
            elif save_image.mode != 'RGB':
                save_image = save_image.convert('RGB')

        # Salvar com configurações apropriadas
        if ext == '.png':
            # PNG: Sempre sem perda
            save_image.save(output_path, 'PNG', optimize=True)

        elif ext == '.webp':
            # WEBP: Qualidade controlada (similar ao Photoshop)
            # quality=100 = sem perda
            # quality=1-99 = com perda controlada
            if quality == 100:
                # Modo lossless (sem perda)
                save_image.save(output_path, 'WEBP', lossless=True, quality=100)
            else:
                # Modo lossy com qualidade especificada
                save_image.save(output_path, 'WEBP', quality=quality, method=6)

        elif ext in ['.jpg', '.jpeg']:
            # JPG: Qualidade controlada
            save_image.save(
                output_path,
                'JPEG',
                quality=quality,
                optimize=True,
                subsampling=0  # Melhor qualidade de cor
            )

        else:
            # Formato desconhecido, tentar salvar como está
            save_image.save(output_path)

        return output_path

    def get_image_info(self, image_path: str) -> Dict:
        """
        Obtém informações sobre uma imagem

        Args:
            image_path: Caminho da imagem

        Returns:
            Dicionário com informações
        """
        try:
            img = Image.open(image_path)
            return {
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format,
                'size_kb': os.path.getsize(image_path) / 1024
            }
        except Exception as e:
            return {'error': str(e)}
