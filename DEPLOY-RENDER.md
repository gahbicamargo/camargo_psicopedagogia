# Deploy no Render – Camargo Psicopedagogia

Passo a passo para publicar o **Sistema Psicopedagógico** (FastAPI + site) no Render, usando a **Opção 1** (tudo no mesmo serviço).

---

## Pré-requisitos

- Conta no **GitHub** com o repositório do projeto (`camargo_psicopedagogia`) já criado e código commitado.
- Conta no **Render** (gratuita): [https://dashboard.render.com/register](https://dashboard.render.com/register).

---

## Parte 1: Deixar o repositório pronto

1. **Confirme que estes arquivos estão na raiz do projeto e commitados:**
   - `requirements.txt`
   - `runtime.txt` (define Python 3.11)
   - `render.yaml` (configuração do serviço no Render)
   - Pasta `app/` com todo o código (main, routes, services, templates, static, models).

2. **Não suba para o Git:**
   - Pasta `.venv/`
   - Pasta `dados_atendimentos/` (dados locais)
   - Arquivo de credenciais do Google (ex.: `credentials-drive.json`)
   - Pasta `app_data/` (configuração local da pasta de saída)

   Se ainda não existir, crie um `.gitignore` na raiz com algo como:

   ```
   .venv/
   __pycache__/
   *.pyc
   .env
   app_data/
   dados_atendimentos/
   *credentials*.json
   ```

3. **Faça push para o GitHub** (ex.: branch `main` ou `master`).

---

## Parte 2: Criar o serviço no Render

### Passo 1 – Acessar o Render

1. Acesse [https://dashboard.render.com](https://dashboard.render.com) e faça login.
2. No menu lateral, clique em **Blueprint** ou em **New +** e depois em **Web Service**.

### Passo 2 – Conectar o repositório

1. Em **Connect a repository**, clique em **Connect account** (ou **Connect GitHub**) se ainda não tiver conectado.
2. Autorize o Render a acessar sua conta do GitHub.
3. Selecione a **organização** (sua conta ou a da Gabi) e o repositório **camargo_psicopedagogia**.
4. Clique em **Connect**.

### Passo 3 – Configurar o Web Service

Se o Render detectou o `render.yaml` (Blueprint):

- O nome do serviço e os comandos de build/start já vêm preenchidos.
- Revise:
  - **Name:** `camargo-psicopedagogia` (ou o nome que preferir).
  - **Region:** escolha a mais próxima (ex.: **Oregon (US West)** ou **Frankfurt**).
  - **Branch:** `main` (ou a branch que você usa).

Se você criou o serviço **manual** (sem Blueprint):

- **Name:** `camargo-psicopedagogia`
- **Region:** a que preferir.
- **Branch:** `main`
- **Root Directory:** deixe em branco (raiz do repositório).
- **Runtime:** **Python 3**.
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- **Instance Type:** **Free** (para começar).

### Passo 4 – Variáveis de ambiente (Environment)

1. Na mesma tela (ou depois em **Environment** no menu do serviço), vá em **Environment Variables** / **Add Environment Variable**.
2. Para rodar **sem Google Drive** (só gerar PDF/CSV no servidor, lembrando que no plano Free o disco é efêmero):

   | Key                     | Value | Observação                          |
   |-------------------------|-------|-------------------------------------|
   | `PASTA_ATENDIMENTOS_DIR`| (vazio ou deixe sem criar) | Usa pasta padrão no servidor |

   Não é obrigatório criar nenhuma variável para o primeiro deploy.

3. **Se for usar Google Drive** (recomendado para persistir os relatórios):

   | Key                             | Value        | Observação |
   |---------------------------------|-------------|------------|
   | `GOOGLE_DRIVE_ENABLED`          | `true`      | Ativa o envio ao Drive |
   | `GOOGLE_DRIVE_PARENT_FOLDER_ID` | ID da pasta | Pasta no Drive onde criar as subpastas por atendimento |
   | `GOOGLE_DRIVE_PUBLIC_LINKS`     | `true` ou `false` | Links públicos ou não |
   | `GOOGLE_DRIVE_CREDENTIALS_FILE` | Ver abaixo  | Caminho ou conteúdo do JSON |

   **Credenciais do Google (service account):**

   - No Render, **não** use um arquivo que esteja só na sua máquina. Duas opções:
     - **Opção A – Variável com JSON:** crie uma variável **Secret File** (ex.: `GOOGLE_DRIVE_CREDENTIALS_FILE`) e cole o conteúdo do JSON da service account (o Render salva como arquivo e injeta o caminho na variável, se configurado assim), **ou**
     - **Opção B – Build:** incluir o JSON no repositório com outro nome (ex.: `drive-credentials.json`) e adicionar ao `.gitignore` em produção não é ideal; o mais seguro é usar **Secret File** no Render com o conteúdo do JSON.
   - Na documentação do Render, para “Secret File” você define o nome da variável e cola o conteúdo; o Render monta o arquivo e pode expor o caminho via outra variável. Consulte: [Render – Secret Files](https://render.com/docs/configure-environment-variables#secret-files).
   - No nosso código, `GOOGLE_DRIVE_CREDENTIALS_FILE` espera o **caminho** do arquivo. No Render, ao usar Secret File, o valor da variável é esse caminho; use-o em `GOOGLE_DRIVE_CREDENTIALS_FILE`.

   Para o primeiro deploy, você pode deixar o Drive desligado (`GOOGLE_DRIVE_ENABLED` não definido ou `false`) e configurar depois.

### Passo 5 – Criar o serviço

1. Clique em **Create Web Service** (ou **Apply** se usou Blueprint).
2. O Render vai clonar o repositório, rodar o **Build** e depois o **Start**. Acompanhe os **Logs** na aba **Logs** do serviço.

---

## Parte 3: Verificar o deploy

1. Quando o deploy terminar, o status ficará **Live** (verde) e aparecerá uma URL do tipo:
   ```text
   https://camargo-psicopedagogia.onrender.com
   ```
   (o nome pode mudar conforme o que você definiu em **Name**).

2. **Teste no navegador:**
   - Abra essa URL: deve carregar a **Ficha de Avaliação Psicopedagógica** (página inicial do sistema).
   - Teste **Ambiente de teste** e **Gerar relatório de teste instantâneo** para validar geração de PDF/CSV e download.

3. **Se algo falhar:**
   - Aba **Logs:** veja erros de import, de variável de ambiente ou de permissão.
   - Aba **Shell** (se disponível no seu plano): entre no container e confira se `app/main.py` e a estrutura `app/` existem.
   - Confirme que **Build Command** e **Start Command** estão exatamente como acima e que a **branch** é a correta.

---

## Parte 4: Resumo dos comandos (referência)

| Etapa   | Comando |
|--------|---------|
| Build  | `pip install -r requirements.txt` |
| Start  | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

O `$PORT` é definido pelo Render; não troque por número fixo.

---

## Observações importantes

- **Plano Free:** o servidor “dorme” após alguns minutos sem acesso; a primeira requisição pode demorar alguns segundos (cold start).
- **Disco efêmero:** arquivos gerados (PDF/CSV) em `dados_atendimentos/` ou na pasta configurada **não persistem** entre deploys ou reinícios. Para guardar relatórios, use **Google Drive** (variáveis acima).
- **Pasta de saída:** a configuração salva pela interface (em `app_data/config.json`) também é efêmera. Em produção, usar `PASTA_ATENDIMENTOS_DIR` ou confiar na pasta padrão e no Drive.
- **HTTPS:** o Render já fornece HTTPS na URL do serviço.
- **Domínio próprio:** no Render, em **Settings → Custom Domain**, você pode apontar um domínio seu para essa URL.

Com isso, o projeto fica 100% configurado para o Render conforme a Opção 1 (site + API no mesmo serviço).
