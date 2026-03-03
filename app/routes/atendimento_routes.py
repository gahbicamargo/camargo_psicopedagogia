import os
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models.atendimento import Atendimento
from app.services.arquivo_service import ArquivoService
from app.services.avaliacao_service import AvaliacaoService
from app.services.config_service import ConfigService
from app.services.drive_service import GoogleDriveService
from app.services.mock_data_service import MockDataService
from app.services.pdf_service import PDFService


BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES = Jinja2Templates(directory=BASE_DIR / "app" / "templates")
dados_dir_env = os.getenv("PASTA_ATENDIMENTOS_DIR", "").strip()
DEFAULT_DADOS_DIR = Path(dados_dir_env) if dados_dir_env else BASE_DIR / "dados_atendimentos"

router = APIRouter()

avaliacao_service = AvaliacaoService()
config_service = ConfigService(BASE_DIR)
drive_service = GoogleDriveService()
mock_data_service = MockDataService()
AVALIADORA_FIXA = "Rosangema Monteiro de Camargo"

CHECKBOX_FIELDS = {
    "instrumento_entrevista_responsaveis",
    "instrumento_observacao_ludica",
    "instrumento_desenhos",
    "instrumento_piaget",
    "instrumento_conservacao",
    "instrumento_classificacao",
    "instrumento_seriacao",
    "instrumento_linguagem",
    "instrumento_consciencia_fonologica",
    "instrumento_leitura_escrita",
    "instrumento_matematica",
    "instrumento_testes_projetivos",
    "instrumento_protocolos_especificos",
    "encaminhamento_fonoaudiologia",
    "encaminhamento_terapia_ocupacional",
    "encaminhamento_psicoterapia",
    "encaminhamento_neuropediatra",
    "encaminhamento_psiquiatria",
}

OUTRO_FIELDS_MAP = {
    "escolar": "escolar_outro",
    "ano_escolar": "ano_escolar_outro",
    "responsavel_presente": "responsavel_presente_outro",
    "tipo_parto": "tipo_parto_outro",
}


@router.get("/", response_class=HTMLResponse)
async def pagina_inicial(request: Request) -> HTMLResponse:
    return _render_formulario(request, dados={}, modo_teste=False)


@router.post("/configuracoes/pasta-saida", response_class=HTMLResponse)
async def configurar_pasta_saida(request: Request, pasta_saida: str = Form("")) -> HTMLResponse:
    pasta = pasta_saida.strip()

    if pasta:
        try:
            Path(pasta).mkdir(parents=True, exist_ok=True)
        except OSError:
            return _render_formulario(
                request,
                dados={},
                modo_teste=False,
                status="erro",
                mensagem="Não foi possível salvar a pasta informada. Verifique o caminho.",
                recomendacoes=[],
            )

    config_service.salvar_pasta_saida(pasta)
    mensagem = "Pasta de saída atualizada com sucesso." if pasta else "Pasta de saída restaurada para o padrão do sistema."
    return _render_formulario(
        request,
        dados={},
        modo_teste=False,
        status="sucesso",
        mensagem=mensagem,
        recomendacoes=[],
    )


@router.get("/download/{pasta_atendimento}/{nome_arquivo}")
async def baixar_arquivo(pasta_atendimento: str, nome_arquivo: str):
    pasta_base = _obter_pasta_saida()
    arquivo = (pasta_base / pasta_atendimento / nome_arquivo).resolve()
    base = pasta_base.resolve()

    if not str(arquivo).startswith(str(base)):
        raise HTTPException(status_code=400, detail="Caminho de arquivo inválido.")

    if not arquivo.exists() or not arquivo.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    return FileResponse(path=arquivo, filename=arquivo.name)


@router.get("/ambiente-teste", response_class=HTMLResponse)
async def ambiente_teste(request: Request) -> HTMLResponse:
    dados_teste = mock_data_service.gerar_dados_teste()
    return _render_formulario(request, dados=dados_teste, modo_teste=True)


@router.post("/atendimentos/gerar", response_class=HTMLResponse)
async def gerar_relatorio(request: Request) -> HTMLResponse:
    form_data = await request.form()
    dados_formulario = {k: (v.strip() if isinstance(v, str) else v) for k, v in form_data.items()}

    for campo in CHECKBOX_FIELDS:
        dados_formulario[campo] = campo in form_data

    _resolver_campos_outro(dados_formulario)
    dados_formulario["avaliadora"] = AVALIADORA_FIXA

    return _processar_atendimento(request, dados_formulario, modo_teste=False)


@router.post("/atendimentos/gerar-teste", response_class=HTMLResponse)
async def gerar_relatorio_teste(request: Request) -> HTMLResponse:
    dados_teste = mock_data_service.gerar_dados_teste()
    dados_teste["avaliadora"] = AVALIADORA_FIXA
    return _processar_atendimento(request, dados_teste, modo_teste=True)


def _render_formulario(
    request: Request,
    dados: dict[str, object],
    modo_teste: bool,
    status: str | None = None,
    mensagem: str | None = None,
    recomendacoes: list[str] | None = None,
    arquivo_url: str | None = None,
    pdf_url: str | None = None,
    drive_links: list[dict[str, str]] | None = None,
    resultado: dict[str, str] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    pasta_saida_atual = str(_obter_pasta_saida())
    return TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "status": status,
            "mensagem": mensagem,
            "recomendacoes": recomendacoes or [],
            "arquivo_url": arquivo_url,
            "pdf_url": pdf_url,
            "drive_links": drive_links or [],
            "drive_habilitado": drive_service.habilitado,
            "pasta_saida_atual": pasta_saida_atual,
            "resultado": resultado,
            "dados": dados,
            "modo_teste": modo_teste,
            "hoje": date.today().isoformat(),
        },
        status_code=status_code,
    )


def _processar_atendimento(request: Request, dados_formulario: dict[str, object], modo_teste: bool) -> HTMLResponse:
    try:
        atendimento = Atendimento(**dados_formulario)
        pasta_saida = _obter_pasta_saida()
        arquivo_service = ArquivoService(pasta_saida)
        pdf_service = PDFService(pasta_saida)

        recomendacoes = avaliacao_service.gerar_recomendacoes(atendimento)
        caminho_csv = arquivo_service.gerar_csv_atendimento(atendimento, recomendacoes)
        caminho_pdf = pdf_service.gerar_pdf_atendimento(atendimento, recomendacoes)
        drive_links: list[dict[str, str]] = []

        if drive_service.service:
            try:
                drive_links = drive_service.upload_arquivos(
                    caminho_csv.parent.name,
                    [caminho_csv, caminho_pdf],
                )
            except Exception:
                recomendacoes.append("Não foi possível enviar os arquivos para o Google Drive.")
        resultado = {
            "nome": atendimento.nome,
            "data_avaliacao": atendimento.data_avaliacao.strftime("%d/%m/%Y"),
            "avaliadora": atendimento.avaliadora or "Não informada",
            "hipotese_dificuldade": atendimento.hipotese_dificuldade_aprendizagem or "Não informada",
        }

        arquivo_url = f"/download/{caminho_csv.parent.name}/{caminho_csv.name}"
        pdf_url = f"/download/{caminho_pdf.parent.name}/{caminho_pdf.name}"
        mensagem = "Avaliação salva com sucesso. Arquivos CSV (compatível com Excel) e PDF gerados."

        return _render_formulario(
            request,
            dados=dados_formulario,
            modo_teste=modo_teste,
            status="sucesso",
            mensagem=mensagem,
            recomendacoes=recomendacoes,
            arquivo_url=arquivo_url,
            pdf_url=pdf_url,
            drive_links=drive_links,
            resultado=resultado,
        )

    except ValidationError as exc:
        erros = []
        for erro in exc.errors():
            campo = erro.get("loc", ["campo"])[-1]
            msg = erro.get("msg", "valor inválido")
            erros.append(f"{campo}: {msg}")

        return _render_formulario(
            request,
            dados=dados_formulario,
            modo_teste=modo_teste,
            status="erro",
            mensagem="Verifique os dados informados.",
            recomendacoes=erros,
            status_code=400,
        )


def _resolver_campos_outro(dados: dict[str, object]) -> None:
    for campo_principal, campo_outro in OUTRO_FIELDS_MAP.items():
        valor_principal = str(dados.get(campo_principal, "")).strip()
        valor_outro = str(dados.get(campo_outro, "")).strip()

        if valor_principal.lower() == "outro" and valor_outro:
            dados[campo_principal] = valor_outro


def _obter_pasta_saida() -> Path:
    pasta = config_service.obter_pasta_saida(DEFAULT_DADOS_DIR)
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta
