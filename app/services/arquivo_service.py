import csv
import re
from pathlib import Path

from app.models.atendimento import Atendimento


class ArquivoService:
    def __init__(self, pasta_base: Path) -> None:
        self.pasta_base = pasta_base

    def gerar_csv_atendimento(self, atendimento: Atendimento, recomendacoes: list[str]) -> Path:
        aluno_slug = self._normalizar_nome(atendimento.nome)

        pasta_atendimento = self.pasta_base / aluno_slug
        pasta_atendimento.mkdir(parents=True, exist_ok=True)

        caminho_csv = pasta_atendimento / f"{aluno_slug}_csv.csv"

        with caminho_csv.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            linha = atendimento.linha_csv()
            linha["Recomendacoes Automaticas"] = " | ".join(recomendacoes)

            writer.writerow(list(linha.keys()))
            writer.writerow(list(linha.values()))

        return caminho_csv

    @staticmethod
    def _normalizar_nome(nome: str) -> str:
        normalizado = re.sub(r"[^a-zA-Z0-9]+", "_", nome.strip().lower())
        return normalizado.strip("_") or "aluno"
