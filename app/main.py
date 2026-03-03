import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.atendimento_routes import router as atendimento_router


BASE_DIR = Path(__file__).resolve().parent.parent
dados_dir_env = os.getenv("PASTA_ATENDIMENTOS_DIR", "").strip()
DADOS_DIR = Path(dados_dir_env) if dados_dir_env else BASE_DIR / "dados_atendimentos"
DADOS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Sistema Psicopedagógico")

app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
app.mount("/arquivos", StaticFiles(directory=DADOS_DIR), name="arquivos")

app.include_router(atendimento_router)
