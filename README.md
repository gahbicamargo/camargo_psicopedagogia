# Sistema Psicopedagógico (FastAPI)

Sistema web simplificado com:
- Backend em FastAPI
- Front-end em HTML + CSS
- Arquitetura modular orientada a objetos (`models`, `services`, `routes`)
- Geração de CSV (compatível com Excel)

## Funcionalidades
- Cadastro de atendimento com notas (0 a 5)
- Validação de preenchimento obrigatório
- Validação de faixa das notas (0 a 5)
- Regras de negócio:
  - Se `atenção > 4`: sugerir acompanhamento
  - Se `média geral > 3,5`: sugerir revisão do plano
- Geração de arquivo CSV em pasta nomeada com aluno + data

## Estrutura
- `app/models/atendimento.py`: modelo e validações
- `app/services/avaliacao_service.py`: regras de negócio
- `app/services/arquivo_service.py`: criação de pasta e CSV
- `app/routes/atendimento_routes.py`: rotas HTTP
- `app/templates/index.html`: interface web
- `app/static/styles.css`: estilos
- `app/main.py`: inicialização do FastAPI

## Como executar
1. Instale dependências:
   - `pip install -r requirements.txt`
2. Execute o servidor:
   - `uvicorn app.main:app --reload`
3. Acesse:
   - `http://127.0.0.1:8000`

## Saída de arquivos
Os arquivos gerados ficam em `dados_atendimentos/`.
Cada atendimento cria uma pasta no formato:
- `nome_do_aluno_aaaa-mm-dd/`

Dentro dela, o CSV:
- `nome_do_aluno_aaaa-mm-dd.csv`

## Alternativa sem custo: salvar direto no Google Drive Desktop
Se você não quiser usar API do Google Drive, pode instalar o Google Drive para Desktop e apontar a pasta de saída para uma pasta sincronizada.

Use a variável de ambiente:
- `PASTA_ATENDIMENTOS_DIR`

Exemplo no Windows PowerShell (na sessão atual):
- `$env:PASTA_ATENDIMENTOS_DIR = "G:\Meu Drive\Camargo\atendimentos"`

Depois inicie o servidor normalmente. O sistema salvará os arquivos nessa pasta, e o Google Drive Desktop fará o upload automático para a nuvem.
