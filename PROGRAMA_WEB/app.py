#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 PROCESSADOR DE IMAGENS EM LOTE - VERSÃO WEB V2
Aplicação web moderna para aplicar overlays/molduras em imagens
Desenvolvido com Streamlit - VERSÃO MELHORADA
"""

import streamlit as st
from PIL import Image
import io
import zipfile
from datetime import datetime
from pathlib import Path
import json
from image_processor import ImageProcessor

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="🎨 Processador de Imagens",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS CUSTOMIZADO MELHORADO ====================
st.markdown("""
<style>
    /* Tema escuro moderno */
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    }

    /* Títulos */
    h1 {
        color: #00d4ff !important;
        text-align: center;
        font-weight: 700;
        padding: 20px 0;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }

    h2 {
        color: #00ff88 !important;
        border-bottom: 2px solid #00ff88;
        padding-bottom: 10px;
    }

    h3 {
        color: #00d4ff !important;
    }

    /* Botões - VERSÃO MAIS CLEAN COM TAMANHO MELHORADO */
    .stButton>button {
        background: linear-gradient(135deg, #0099cc 0%, #007799 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 16px 32px !important;
        min-height: 50px !important;
        font-size: 16px !important;
        transition: all 0.3s !important;
        box-shadow: 0 2px 4px rgba(0, 153, 204, 0.2) !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 153, 204, 0.3) !important;
        background: linear-gradient(135deg, #00aadd 0%, #008899 100%) !important;
    }

    /* Botão primário especial */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #00cc88 0%, #009966 100%) !important;
    }

    /* Upload area */
    .uploadedFile {
        background: rgba(0, 212, 255, 0.1);
        border: 2px dashed #00d4ff;
        border-radius: 10px;
        padding: 20px;
    }

    /* Métricas */
    .stMetric {
        background: rgba(0, 212, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #00d4ff;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0099cc 0%, #00cc88 100%);
    }

    /* Imagens - tamanho controlado */
    .preview-container img {
        max-height: 400px !important;
        object-fit: contain !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INICIALIZAÇÃO ====================
if 'processor' not in st.session_state:
    st.session_state.processor = ImageProcessor()
    st.session_state.processed_images = []
    st.session_state.preview_image = None
    st.session_state.show_preview = False
    st.session_state.current_preview_index = 0  # Índice da imagem atual no preview
    st.session_state.stats = {
        'total': 0,
        'processed': 0,
        'failed': 0
    }
    st.session_state.keep_overlay_size = False

processor = st.session_state.processor

# ==================== FUNÇÕES AUXILIARES ====================

def load_preset(preset_file):
    """Carrega configurações de um preset"""
    try:
        preset_data = json.loads(preset_file.read())
        return preset_data
    except Exception as e:
        st.error(f"❌ Erro ao carregar preset: {str(e)}")
        return None

def save_preset(config):
    """Salva configurações como preset"""
    preset_data = json.dumps(config, indent=4, ensure_ascii=False)
    return preset_data

def create_download_zip(processed_images, format_ext, quality, prefix, suffix, progress_callback=None):
    """
    Cria arquivo ZIP com todas as imagens processadas
    ⚡ OTIMIZADO: Sem compressão do ZIP (imagens já são comprimidas)
    """
    zip_buffer = io.BytesIO()

    # ZIP_STORED = sem compressão (muito mais rápido, pois imagens já são comprimidas)
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zip_file:
        total = len(processed_images)

        for idx, (img, original_name) in enumerate(processed_images, 1):
            # Callback de progresso
            if progress_callback:
                progress_callback(idx, total, original_name)

            # Criar nome do arquivo
            name_without_ext = Path(original_name).stem
            new_name = f"{prefix}{name_without_ext}{suffix}.{format_ext}"

            # Salvar imagem em buffer
            img_buffer = io.BytesIO()

            if format_ext == 'png':
                # PNG: Sem optimize para velocidade
                img.save(img_buffer, 'PNG', compress_level=6)
            elif format_ext == 'webp':
                if quality == 100:
                    img.save(img_buffer, 'WEBP', lossless=True, quality=100, method=4)
                else:
                    # method=4 é mais rápido que method=6 com qualidade similar
                    img.save(img_buffer, 'WEBP', quality=quality, method=4)
            elif format_ext in ['jpg', 'jpeg']:
                # Converter para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                # Remover optimize e subsampling para velocidade
                img.save(img_buffer, 'JPEG', quality=quality)

            # Adicionar ao ZIP
            zip_file.writestr(new_name, img_buffer.getvalue())

    zip_buffer.seek(0)
    return zip_buffer

def load_overlay_image():
    """Carrega a imagem do overlay a partir do session_state"""
    if 'overlay_file' not in st.session_state or st.session_state.overlay_file is None:
        return None
    st.session_state.overlay_file.seek(0)
    return Image.open(st.session_state.overlay_file)

# ==================== HEADER ====================
st.markdown("# 🎨 PROCESSADOR DE IMAGENS EM LOTE")
st.markdown("### 💎 Aplique overlays, molduras e texto em múltiplas imagens com qualidade profissional")

st.markdown("---")

# ==================== SIDEBAR - CONFIGURAÇÕES ====================
with st.sidebar:
    st.markdown("## ⚙️ CONFIGURAÇÕES")

    # ===== INFO DO SERVIDOR =====
    st.info("💡 **Dica:** Para melhor performance, processe até 50 imagens por vez.")

    # ===== ARQUIVOS DE ENTRADA =====
    st.markdown("### 📂 ARQUIVOS DE ENTRADA")
    uploaded_files = st.file_uploader(
        "Arraste e solte ou selecione suas imagens",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        help="Envie as imagens que receberão o overlay"
    )

    # ===== UPLOAD DE OVERLAY =====
    st.markdown("### 🖼️ OVERLAY/MOLDURA")
    
    # Área de upload mais destacada
    st.markdown("**📁 Selecione sua moldura/overlay:**")
    overlay_file = st.file_uploader(
        "Drag and drop file here",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Imagem que será aplicada sobre todas as imagens",
        key="overlay_uploader"
    )
    
    # Armazenar overlay no session_state para persistência
    if overlay_file:
        st.session_state.overlay_file = overlay_file
        st.success(f"✅ Overlay carregado: {overlay_file.name}")
    else:
        st.info("ℹ️ Selecione um arquivo de overlay para continuar")

    keep_overlay_size = st.checkbox(
        "Manter resolução original do overlay",
        value=st.session_state.keep_overlay_size
    )
    st.session_state.keep_overlay_size = keep_overlay_size

    st.markdown("---")

    # ===== FORMATO E QUALIDADE =====
    st.markdown("### 💾 FORMATO E QUALIDADE")

    output_format = st.selectbox(
        "Formato de Saída",
        ["WEBP (Recomendado)", "PNG (Sem Perda)", "JPG"],
        help="WEBP oferece melhor compressão mantendo qualidade"
    )

    # Mapear formato
    format_map = {
        "WEBP (Recomendado)": "webp",
        "PNG (Sem Perda)": "png",
        "JPG": "jpg"
    }
    selected_format = format_map[output_format]

    # Slider de qualidade
    if selected_format in ['webp', 'jpg']:
        quality = st.slider(
            "Qualidade",
            min_value=1,
            max_value=100,
            value=95,
            help="100 = Máxima qualidade, 95 = Imperceptível, 85 = Otimizado para web"
        )

        # Indicador de qualidade
        if quality == 100:
            st.success("🌟 Qualidade Máxima (Lossless)")
        elif quality >= 90:
            st.info("💎 Qualidade Muito Alta")
        elif quality >= 80:
            st.info("✨ Qualidade Alta")
        elif quality >= 70:
            st.warning("📊 Qualidade Média")
        else:
            st.warning("⚡ Qualidade Básica")
    else:
        quality = 100
        st.success("🌟 PNG: Sempre sem perda de qualidade")

    st.markdown("---")

    # ===== RENOMEAÇÃO =====
    st.markdown("### ✏️ RENOMEAÇÃO (OPCIONAL)")

    col1, col2 = st.columns(2)
    with col1:
        prefix = st.text_input("Prefixo", "", help="Adiciona no início do nome")
    with col2:
        suffix = st.text_input("Sufixo", "", help="Adiciona no final do nome")

    if prefix or suffix:
        st.caption(f"📝 Exemplo: {prefix}imagem{suffix}.{selected_format}")

    st.markdown("---")

    # ===== TEXTO SOBREPOSTO =====
    st.markdown("### 📝 TEXTO SOBREPOSTO")

    text_enabled = st.checkbox("Adicionar texto nas imagens", value=False)

    if text_enabled:
        text_overlay = st.text_input(
            "Texto",
            "PROMOÇÃO",
            help="Texto que aparecerá nas imagens"
        )

        col1, col2 = st.columns(2)
        with col1:
            text_size = st.number_input("Tamanho", min_value=10, max_value=200, value=50)
        with col2:
            text_color = st.color_picker("Cor do Texto", "#FFFFFF")

        text_position = st.selectbox(
            "Posição",
            ["Superior Esquerda", "Superior Direita", "Inferior Esquerda", "Inferior Direita", "Centro"]
        )

        text_opacity = st.slider("Opacidade do Texto (%)", 0, 100, 100)

        # Fundo do texto
        text_bg_enabled = st.checkbox("Fundo atrás do texto", value=True)

        if text_bg_enabled:
            col1, col2 = st.columns(2)
            with col1:
                text_bg_color = st.color_picker("Cor do Fundo", "#000000")
            with col2:
                text_bg_opacity = st.slider("Opacidade Fundo (%)", 0, 100, 70)

    st.markdown("---")

    # ===== OPÇÕES DE DOWNLOAD =====
    st.markdown("### 📥 OPÇÕES DE DOWNLOAD")

    st.caption("As imagens processadas serão entregues em um arquivo ZIP para download.")

    st.markdown("---")

    # ===== PRESETS =====
    st.markdown("### 💾 PRESETS")

    preset_file = st.file_uploader(
        "📂 Carregar Preset",
        type=['json'],
        help="Carregue configurações salvas anteriormente"
    )

    if st.button("💾 Salvar Configurações Atuais", use_container_width=True):
        config = {
            "output_format": selected_format,
            "quality": quality,
            "prefix": prefix,
            "suffix": suffix,
            "text_enabled": text_enabled,
        }

        if text_enabled:
            config.update({
                "text_overlay": text_overlay,
                "text_size": text_size,
                "text_color": text_color,
                "text_position": text_position,
                "text_opacity": text_opacity,
                "text_bg_enabled": text_bg_enabled,
                "text_bg_color": text_bg_color if text_bg_enabled else "#000000",
                "text_bg_opacity": text_bg_opacity if text_bg_enabled else 70
            })

        preset_json = save_preset(config)
        st.download_button(
            label="📥 Baixar Preset",
            data=preset_json,
            file_name=f"preset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# ==================== ÁREA PRINCIPAL ====================

# ===== SELEÇÃO DE IMAGENS =====
st.markdown("## 📤 SELEÇÃO DE IMAGENS")

images_to_process = uploaded_files or []
total_images = len(images_to_process)

if total_images == 0:
    st.info("Envie imagens na barra lateral para começar.")
else:
    st.success(f"✅ {total_images} imagem(ns) carregada(s)")

    with st.expander(f"👁️ Visualizar {total_images} imagem(ns)", expanded=False):
        cols = st.columns(min(5, total_images))
        for idx, file_item in enumerate(images_to_process[:5]):
            with cols[idx]:
                file_item.seek(0)
                img = Image.open(file_item)
                st.image(img, caption=file_item.name, use_container_width=True)
        if total_images > 5:
            st.caption(f"... e mais {total_images - 5} imagem(ns)")

st.markdown("---")

# ===== PREVIEW E PROCESSAMENTO =====
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("## 👁️ PREVIEW")
    
    # Seletor de imagem para preview
    if total_images > 0:
        st.markdown("**📋 Escolha a imagem para preview:**")
        
        # Criar lista de nomes de arquivos para o seletor
        image_names = [f"{idx + 1}. {file_item.name}" for idx, file_item in enumerate(images_to_process)]
        
        # Seletor dropdown
        selected_image_name = st.selectbox(
            "Imagem para preview:",
            image_names,
            index=st.session_state.current_preview_index,
            key="preview_selector"
        )
        
        # Atualizar índice baseado na seleção
        st.session_state.current_preview_index = image_names.index(selected_image_name)
        
        # Botões de navegação
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
        
        with nav_col1:
            if st.button("⬅️ Anterior", use_container_width=True, disabled=st.session_state.current_preview_index == 0):
                st.session_state.current_preview_index = max(0, st.session_state.current_preview_index - 1)
                st.rerun()
        
        with nav_col2:
            if st.button("🔍 GERAR PREVIEW", use_container_width=True):
                # Verificar se overlay foi carregado usando session_state
                overlay_loaded = 'overlay_file' in st.session_state and st.session_state.overlay_file is not None
                
                if not overlay_loaded:
                    st.warning("⚠️ Selecione um arquivo de overlay primeiro!")
                elif total_images == 0:
                    st.warning("⚠️ Selecione ao menos uma imagem!")
                else:
                    with st.spinner("Gerando preview..."):
                        try:
                            # Processar imagem selecionada
                            current_idx = st.session_state.current_preview_index
                            
                            current_file = images_to_process[current_idx]
                            current_file.seek(0)
                            base_img = Image.open(current_file)
                            filename = current_file.name

                            overlay_img = load_overlay_image()
                            if overlay_img is None:
                                st.warning("⚠️ Não foi possível carregar o overlay.")
                            else:
                                result = processor.apply_overlay(
                                    base_img,
                                    overlay_img,
                                    st.session_state.keep_overlay_size
                                )

                                # Aplicar texto se habilitado
                                if text_enabled and text_overlay.strip():
                                    pos_map = {
                                        "Superior Esquerda": "superior_esquerda",
                                        "Superior Direita": "superior_direita",
                                        "Inferior Esquerda": "inferior_esquerda",
                                        "Inferior Direita": "inferior_direita",
                                        "Centro": "centro"
                                    }

                                    text_config = {
                                        "text": text_overlay,
                                        "size": text_size,
                                        "color": text_color,
                                        "position": pos_map[text_position],
                                        "opacity": text_opacity,
                                        "bg_enabled": text_bg_enabled,
                                        "bg_color": text_bg_color if text_bg_enabled else "#000000",
                                        "bg_opacity": text_bg_opacity if text_bg_enabled else 70
                                    }

                                    result = processor.add_text_overlay(result, text_config)

                                st.session_state.preview_image = result
                                st.session_state.show_preview = True
                                st.success(f"✅ Preview gerado: {filename}")

                        except Exception as e:
                            st.error(f"❌ Erro ao gerar preview: {str(e)}")
        
        with nav_col3:
            if st.button("➡️ Próxima", use_container_width=True, disabled=st.session_state.current_preview_index >= total_images - 1):
                st.session_state.current_preview_index = min(total_images - 1, st.session_state.current_preview_index + 1)
                st.rerun()
        
        # Informações da imagem atual
        current_idx = st.session_state.current_preview_index
        current_filename = images_to_process[current_idx].name
        
        st.info(f"📸 **Imagem atual:** {current_filename} ({current_idx + 1}/{total_images})")
        
        # Botão para fechar preview
        if st.session_state.show_preview and st.button("❌ Fechar Preview", use_container_width=True):
            st.session_state.show_preview = False
            st.session_state.preview_image = None
            st.rerun()

        # Mostrar preview
        if st.session_state.show_preview and st.session_state.preview_image:
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            st.image(
                st.session_state.preview_image,
                caption=f"Preview: {current_filename}",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Clique em 'GERAR PREVIEW' para visualizar o resultado")
    else:
        st.warning("⚠️ Selecione imagens primeiro para usar o preview")

with col2:
    st.markdown("## 🚀 PROCESSAMENTO")

    if st.button("🚀 PROCESSAR TODAS AS IMAGENS", use_container_width=True, type="primary"):
        overlay_loaded = 'overlay_file' in st.session_state and st.session_state.overlay_file is not None
        if not overlay_loaded:
            st.warning("⚠️ Selecione um arquivo de overlay primeiro!")
        elif total_images == 0:
            st.warning("⚠️ Selecione imagens para processar!")
        else:
            # Resetar estatísticas
            st.session_state.stats = {
                'total': total_images,
                'processed': 0,
                'failed': 0
            }
            st.session_state.processed_images = []

            # Barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()

            start_time = datetime.now()
            failed_files = []

            # ⚡ OTIMIZAÇÃO: Carregar overlay UMA VEZ antes do loop
            status_text.text("Carregando overlay...")
            overlay_img = load_overlay_image()
            if overlay_img is None:
                st.error("❌ Overlay não disponível.")
                st.stop()

            # Converter overlay para RGBA uma vez
            if overlay_img.mode != 'RGBA':
                overlay_img = overlay_img.convert('RGBA')

            status_text.text("Iniciando processamento...")

            # Processar cada imagem
            img_start_times = []  # Para calcular tempo médio

            for idx, file_item in enumerate(images_to_process):
                img_start = datetime.now()

                try:
                    filename = file_item.name
                    file_item.seek(0)
                    base_img = Image.open(file_item)

                    # Calcular tempo estimado restante
                    if idx > 0 and img_start_times:
                        avg_time = sum(img_start_times) / len(img_start_times)
                        remaining = total_images - idx
                        eta_seconds = avg_time * remaining
                        eta_text = f" - ETA: {int(eta_seconds)}s"
                    else:
                        eta_text = ""

                    percent = int(((idx + 1) / total_images) * 100)
                    status_text.text(f"⚡ [{percent}%] Processando: {filename} ({idx + 1}/{total_images}){eta_text}")

                    # Converter para RGBA
                    if base_img.mode != 'RGBA':
                        base_img = base_img.convert('RGBA')

                    # Aplicar overlay (já está carregado e em RGBA)
                    result = processor.apply_overlay(
                        base_img,
                        overlay_img,
                        st.session_state.keep_overlay_size
                    )

                    # Aplicar texto
                    if text_enabled and text_overlay.strip():
                        pos_map = {
                            "Superior Esquerda": "superior_esquerda",
                            "Superior Direita": "superior_direita",
                            "Inferior Esquerda": "inferior_esquerda",
                            "Inferior Direita": "inferior_direita",
                            "Centro": "centro"
                        }

                        text_config = {
                            "text": text_overlay,
                            "size": text_size,
                            "color": text_color,
                            "position": pos_map[text_position],
                            "opacity": text_opacity,
                            "bg_enabled": text_bg_enabled,
                            "bg_color": text_bg_color if text_bg_enabled else "#000000",
                            "bg_opacity": text_bg_opacity if text_bg_enabled else 70
                        }

                        result = processor.add_text_overlay(result, text_config)

                    st.session_state.processed_images.append((result, filename))
                    st.session_state.stats['processed'] += 1

                except Exception as e:
                    failed_files.append((filename, str(e)))
                    st.session_state.stats['failed'] += 1

                # Calcular tempo gasto nesta imagem
                img_end = datetime.now()
                img_time = (img_end - img_start).total_seconds()
                img_start_times.append(img_time)

                # Manter apenas últimas 5 medições para cálculo de média
                if len(img_start_times) > 5:
                    img_start_times.pop(0)

                progress_bar.progress((idx + 1) / total_images)

            # Finalizar
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            status_text.empty()
            progress_bar.empty()

            st.success("✅ Processamento concluído!")

            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", st.session_state.stats['total'])
            with col2:
                st.metric("✅ Processadas", st.session_state.stats['processed'])
            with col3:
                st.metric("❌ Falhas", st.session_state.stats['failed'])
            with col4:
                imgs_per_sec = st.session_state.stats['processed'] / max(duration, 0.1)
                st.metric("⚡ Velocidade", f"{imgs_per_sec:.1f} img/s")

            st.caption(f"⏱️ Tempo total: {duration:.2f} segundos | Média: {duration/max(total_images, 1):.2f}s por imagem")

            if failed_files:
                with st.expander("⚠️ Ver erros", expanded=False):
                    for filename, error in failed_files:
                        st.error(f"❌ {filename}: {error}")

    # Botão de download
    if st.session_state.processed_images:
        st.markdown("---")
        st.markdown("### 📥 DOWNLOAD")

        # Criar placeholder para feedback
        zip_progress_bar = st.progress(0)
        zip_status = st.empty()

        # Função de callback para progresso
        def zip_progress_callback(current, total, filename):
            percent = current / total
            zip_progress_bar.progress(percent)
            zip_status.text(f"📦 Preparando ZIP: {current}/{total} - {filename}")

        # Criar ZIP com feedback
        zip_start = datetime.now()
        zip_buffer = create_download_zip(
            st.session_state.processed_images,
            selected_format,
            quality,
            prefix,
            suffix,
            progress_callback=zip_progress_callback
        )
        zip_end = datetime.now()
        zip_duration = (zip_end - zip_start).total_seconds()

        # Limpar feedback
        zip_progress_bar.empty()
        zip_status.empty()

        filename = f"imagens_processadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        st.download_button(
            label=f"📥 BAIXAR TODAS ({len(st.session_state.processed_images)} imagens)",
            data=zip_buffer,
            file_name=filename,
            mime="application/zip",
            use_container_width=True
        )

        st.success(f"✅ {len(st.session_state.processed_images)} imagem(ns) pronta(s) para download!")
        st.caption(f"⚡ ZIP criado em {zip_duration:.2f} segundos")

        # Preview das processadas (compacto)
        with st.expander("👁️ Ver imagens processadas", expanded=False):
            cols = st.columns(min(5, len(st.session_state.processed_images)))
            for idx, (img, name) in enumerate(st.session_state.processed_images[:5]):
                with cols[idx]:
                    st.image(img, caption=name, use_container_width=True)
            if len(st.session_state.processed_images) > 5:
                st.caption(f"... e mais {len(st.session_state.processed_images) - 5} imagem(ns)")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🎨 <b>Processador de Imagens em Lote - Versão Web V2</b></p>
    <p>Desenvolvido com ❤️ em Python + Streamlit</p>
    <p>💡 Dica: Use WEBP com qualidade 95% para melhor equilíbrio</p>
</div>
""", unsafe_allow_html=True)
