# 🎨 Processador de Imagens em Lote (versão web)

Aplicação Streamlit para aplicar overlays, molduras e textos em várias imagens ao mesmo tempo. Ideal para equipes que precisam gerar artes de maneira rápida e consistente direto no navegador.

---

## 🚀 Principais recursos
- Upload múltiplo de imagens (`png`, `jpg`, `jpeg`, `webp`).
- Aplicação de overlays redimensionados automaticamente.
- Texto opcional com controle de cor, posição, opacidade e fundo.
- Preview antes do processamento.
- Download único em arquivo `.zip` preparado com todas as imagens.
- Presets em JSON para salvar e reutilizar configurações.

---

## 🛠️ Requisitos
- Python 3.9 ou superior.
- pip (geralmente já vem com o Python).

---

## 💻 Como executar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

O Streamlit abrirá automaticamente o app em `http://localhost:8501`.

---

## ☁️ Publicando no Streamlit Community Cloud
1. Suba o conteúdo desta pasta para um repositório Git (GitHub/GitLab).
2. No painel do [Streamlit Community Cloud](https://streamlit.io/cloud), escolha **New app** e conecte sua conta GitHub.
3. Aponte para o repositório, branch principal e arquivo `app.py`.
4. Confirme o deploy. O serviço instala as dependências listadas em `requirements.txt` e expõe o app com HTTPS automaticamente.
5. Compartilhe o link gerado (`https://seuapp.streamlit.app`). O serviço acorda quando alguém acessa.

Se precisar de ajustes avançados (ex.: Render, Railway ou VPS), consulte `HOSPEDAGEM_WEB.md`.

---

## 📁 Estrutura
```
.
├── app.py               # Interface principal Streamlit
├── image_processor.py   # Regras de processamento (overlay/texto)
├── presets_exemplos/    # Presets em JSON para exemplos de configuração
├── requirements.txt     # Dependências mínimas
└── HOSPEDAGEM_WEB.md    # Guia detalhado de hospedagem
```

---

## 💡 Dicas rápidas
- Use overlays com transparência (PNG/WebP) do mesmo tamanho das imagens-alvo para melhores resultados.
- Para textos com cores claras, ative o fundo com opacidade média e garanta contraste.
- Qualidade recomendada para WebP: 90–95 (ótimo equilíbrio entre tamanho e fidelidade).
- Sempre faça download do arquivo `.zip` antes de recarregar a página para não perder o processamento feito.

Boa criação! 🖼️✨
