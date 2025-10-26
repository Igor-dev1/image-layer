# 🛰️ Guia de Hospedagem – Processador de Imagens Web

Este documento resume as opções para colocar o projeto `PROGRAMA_WEB` no ar em um ambiente externo. O aplicativo é feito em **Streamlit** e precisa manter um processo Python rodando continuamente, portanto, hospedagens compartilhadas tradicionais (cPanel/LAMP) não são adequadas sem grandes adaptações.

---

## 1. Diagnóstico Rápido
- `app.py` roda com `streamlit run app.py`, escutando na porta 8501.
- Dependências Python: `streamlit` e `Pillow` (instale com `pip install -r requirements.txt`).
- O código procura fontes do sistema (ex.: `DejaVuSans-Bold`), então o ambiente de hospedagem deve possuir pelo menos uma fonte TTF reconhecida.

---

## 2. Opção Recomendada – Streamlit Community Cloud (Gratuito)
1. Suba o projeto para um repositório Git público (GitHub ou GitLab).  
   - Estruture a pasta com `app.py`, `requirements.txt`, `HOSPEDAGEM_WEB.md`, etc.
2. Acesse [https://streamlit.io/cloud](https://streamlit.io/cloud) e conecte sua conta GitHub.
3. Crie uma nova app escolhendo o repositório e o arquivo `app.py`.
4. Aguarde o build automático. O Streamlit Cloud gerencia porta, HTTPS e reinicialização automática.
5. Compartilhe o link fornecido (ex.: `https://seuapp.streamlit.app`).

**Observações:**  
- O plano gratuito dorme se ficar inativo, mas acorda quando alguém acessa.  
- Repositório precisa ser público. Para repositórios privados, é necessário plano pago.

---

## 3. Opção Alternativa – Plataformas PaaS (Render, Railway, Hugging Face, Deta, Fly.io)
Esses serviços suportam aplicações Python com processos sempre ativos.

### Passos gerais
1. Crie um repositório Git (público ou privado).
2. Em Render/Railway/Fly, configure o deploy via CLI ou painel web apontando para o repositório.
3. Defina o comando de inicialização:
   ```bash
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
4. Se a plataforma usar Procfile (ex.: Render, Railway), adicione na raiz:
   ```Procfile
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
5. Confirme as variáveis de ambiente e a versão do Python (>=3.9 é suficiente).
6. Faça o deploy; a plataforma cria o contêiner, expõe HTTPS e mantém o processo ativo.

**Observações:**  
- Essas plataformas cobram por horas de uso quando extrapolam a camada gratuita.  
- Certifique-se de escolher região próxima aos usuários para menor latência.

---

## 4. Opção Completa – VPS (DigitalOcean, Linode, AWS Lightsail, Contabo)
1. Provisionar uma máquina virtual Linux (Ubuntu 22.04, por exemplo).
2. Acessar via SSH e instalar dependências:
   ```bash
   sudo apt update && sudo apt install -y python3 python3-venv python3-pip fonts-dejavu-core
   python3 -m venv ~/appenv
   source ~/appenv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Rodar o Streamlit em modo servidor:
   ```bash
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   ```
4. Configurar um serviço para manter o processo ativo (ex.: `systemd`):
   ```ini
   # /etc/systemd/system/processador.service
   [Unit]
   Description=Processador de Imagens Streamlit
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/PROGRAMA_WEB
   Environment="PATH=/home/ubuntu/appenv/bin"
   ExecStart=/home/ubuntu/appenv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now processador.service
   ```
5. Configurar Nginx como proxy reverso (porta 80/443) apontando para `localhost:8501`.
6. Emitir certificado TLS (Let’s Encrypt) para servir via HTTPS.

**Observações:**  
- Maior liberdade e controle; ideal se precisar de customizações avançadas.  
- Exige manutenção do servidor (updates, backups, monitoramento).

---

## 5. Hospedagem Compartilhada Tradicional (cPanel/LAMP) – Por que evitar?
- Geralmente apenas **PHP** é suportado; Python roda apenas em scripts rápidos (CGI) e sem acesso a long-running processes.
- Portas arbitrárias (ex.: 8501) são bloqueadas; não é possível deixar o Streamlit escutando.
- Mesmo quando há “Python App (Passenger)”, ele espera um aplicativo WSGI (Flask/Django). Streamlit não é WSGI.
- Para usar esse tipo de hospedagem, seria preciso reescrever a interface em Flask/Django + frontend, o que implica refatoração pesada.

---

## 6. Checklist Antes do Deploy
- [ ] Git repo organizado sem arquivos temporários.
- [ ] `requirements.txt` inclui todas as dependências reais (`streamlit`, `Pillow`).
- [ ] Fonte TTF disponível no servidor (instale `fonts-dejavu-core` ou similar).
- [ ] Teste local com:
  ```bash
  streamlit run app.py --server.port 8501 --server.address 0.0.0.0
  ```
- [ ] Se precisar de outro formato de saída além de ZIP, adapte o código antes do deploy.

---

## 7. Próximos Passos
1. Escolha a opção que mais atende ao orçamento e tempo (Streamlit Cloud para rápida publicação, Render/Railway para planos escaláveis, VPS para controle total).
2. Ajuste o repositório e arquivos conforme a opção selecionada.
3. Realize o deploy e compartilhe o link com a equipe/usuários.
4. Se precisar migrar para uma arquitetura WSGI futuramente, planeje a refatoração da interface sem Streamlit.
