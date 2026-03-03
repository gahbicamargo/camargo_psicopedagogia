from app.models.atendimento import Atendimento


class AvaliacaoService:
    def gerar_recomendacoes(self, atendimento: Atendimento) -> list[str]:
        recomendacoes: list[str] = []

        encaminhamentos = []
        if atendimento.encaminhamento_fonoaudiologia:
            encaminhamentos.append("Fonoaudiologia")
        if atendimento.encaminhamento_terapia_ocupacional:
            encaminhamentos.append("Terapia Ocupacional")
        if atendimento.encaminhamento_psicoterapia:
            encaminhamentos.append("Psicoterapia")
        if atendimento.encaminhamento_neuropediatra:
            encaminhamentos.append("Neuropediatra")
        if atendimento.encaminhamento_psiquiatria:
            encaminhamentos.append("Psiquiatria")

        if encaminhamentos:
            recomendacoes.append(f"Encaminhamentos sugeridos: {', '.join(encaminhamentos)}.")

        if atendimento.frequencia_recomendada:
            recomendacoes.append(f"Frequência recomendada: {atendimento.frequencia_recomendada}.")

        if not recomendacoes:
            recomendacoes.append("Ficha registrada sem encaminhamentos automáticos marcados.")

        return recomendacoes
