from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.atendimento import Atendimento


class PDFService:
    ROTULOS: dict[str, str] = {
        "nome": "Nome",
        "data_nascimento": "Data de nascimento",
        "idade": "Idade",
        "escolar": "Escola",
        "ano_escolar": "Ano escolar",
        "responsavel_presente": "Responsável presente na avaliação",
        "cep": "CEP",
        "endereco_logradouro": "Logradouro",
        "endereco_numero": "Número",
        "endereco_complemento": "Complemento",
        "endereco_bairro": "Bairro",
        "endereco_cidade": "Cidade",
        "endereco_estado": "UF",
        "data_avaliacao": "Data da avaliação",
        "avaliadora": "Avaliadora",
        "motivo_familia": "Queixa relatada pela família",
        "queixa_escolar": "Queixa escolar",
        "historico_dificuldades": "Histórico do surgimento das dificuldades",
        "intercorrencias_gravidez": "Intercorrências na gravidez",
        "tipo_parto": "Tipo de parto",
        "prematuridade": "Prematuridade",
        "prematuridade_semanas": "Prematuridade - semanas de nascimento",
        "tempo_uti": "Tempo de UTI / cuidados especiais",
        "tempo_uti_detalhes": "UTI/cuidados - detalhamento",
        "engatinhou": "Engatinhou (meses)",
        "sentou": "Sentou (meses)",
        "andou": "Andou (meses)",
        "primeiras_palavras": "Primeiras palavras (meses)",
        "frases": "Frases (meses)",
        "controle_esfincter": "Controle esfincteriano",
        "observacoes_marcos": "Observações",
        "atitude_inicial": "Atitude inicial",
        "contato_visual": "Contato visual",
        "resposta_instrucoes": "Resposta a instruções",
        "foco_atencao_observacao": "Foco e atenção",
        "persistencia_tarefa": "Persistência na tarefa",
        "controle_emocional": "Controle emocional",
        "interacao_avaliadora": "Interação com a avaliadora",
        "atividade_motora": "Atividade motora",
        "observacoes_gerais": "Observações gerais",
        "instrumento_entrevista_responsaveis": "Entrevista com os responsáveis",
        "instrumento_observacao_ludica": "Observação lúdica",
        "instrumento_desenhos": "Desenhos",
        "instrumento_piaget": "Provas operatórias de Piaget",
        "instrumento_conservacao": "Conservação",
        "instrumento_classificacao": "Classificação",
        "instrumento_seriacao": "Seriação",
        "instrumento_linguagem": "Avaliação de linguagem",
        "instrumento_consciencia_fonologica": "Avaliação de consciência fonológica",
        "instrumento_leitura_escrita": "Avaliação de leitura e escrita",
        "instrumento_matematica": "Avaliação matemática",
        "instrumento_testes_projetivos": "Testes projetivos",
        "instrumento_protocolos_especificos": "Protocolos específicos (TEA, TDAH etc.)",
        "instrumento_outros": "Outros instrumentos",
        "atencao_sustentacao": "Atenção - sustentação",
        "atencao_seletividade": "Atenção - seletividade",
        "atencao_alternancia": "Atenção - alternância",
        "atencao_dispersa": "Atenção dispersa?",
        "atencao_comentarios": "Atenção - comentários",
        "memoria_auditiva_imediata": "Memória auditiva imediata",
        "memoria_visual_imediata": "Memória visual imediata",
        "memoria_operacional": "Memória operacional",
        "linguagem_compreensao_oral": "Linguagem - compreensão oral",
        "linguagem_expressao_verbal": "Linguagem - expressão verbal",
        "linguagem_vocabulario": "Linguagem - vocabulário",
        "linguagem_articulacao": "Linguagem - articulação",
        "linguagem_fluencia": "Linguagem - fluência",
        "raciocinio_sequencia_logica": "Raciocínio lógico - sequência",
        "raciocinio_categorizacao": "Raciocínio lógico - categorização",
        "raciocinio_comparacao": "Raciocínio lógico - comparação",
        "raciocinio_causa_efeito": "Raciocínio lógico - causa e efeito",
        "hipoteses_escrita": "Hipóteses de escrita",
        "leitura_fluencia": "Leitura - fluência",
        "leitura_compreensao": "Leitura - compreensão",
        "leitura_velocidade": "Leitura - velocidade",
        "escrita_letra": "Escrita - letra",
        "escrita_ortografia": "Escrita - ortografia",
        "escrita_construcao_frases": "Escrita - construção de frases",
        "escrita_coerencia_textual": "Escrita - coerência textual",
        "matematica_reconhecimento_numeros": "Matemática - reconhecimento de números",
        "matematica_contagem": "Matemática - contagem",
        "matematica_operacoes_basicas": "Matemática - operações básicas",
        "matematica_resolucao_problemas": "Matemática - resolução de problemas",
        "matematica_raciocinio_logico": "Matemática - raciocínio lógico",
        "relacionamento_avaliadora": "Relacionamento com a avaliadora",
        "relacionamento_pares": "Relacionamento com pares",
        "autoestima": "Autoestima",
        "autonomia": "Autonomia",
        "sinais_ansiedade_tristeza_dependencia": "Sinais de ansiedade / tristeza / dependência excessiva",
        "brincadeira_tipo_preferida": "Tipo de brincadeira preferida",
        "brincadeira_imaginacao_simbolismo": "Imaginação / simbolismo",
        "brincadeira_interacao_social": "Interação social no brincar",
        "brincadeira_organizacao_espaco": "Organização do espaço",
        "brincadeira_persistencia_jogo": "Persistência no jogo",
        "hipotese_dificuldade_aprendizagem": "Possível dificuldade/transtorno de aprendizagem",
        "indicios_tea": "Indícios de TEA",
        "indicios_tdah": "Indícios de TDAH",
        "dificuldades_pedagogicas_especificas": "Dificuldades pedagógicas específicas",
        "aspectos_emocionais_envolvidos": "Aspectos emocionais envolvidos",
        "fatores_ambientais_familiares": "Fatores ambientais/familiares relevantes",
        "recomendacao_familia": "Recomendações para a família",
        "recomendacao_escola": "Recomendações para a escola",
        "encaminhamento_fonoaudiologia": "Encaminhamento - Fonoaudiologia",
        "encaminhamento_terapia_ocupacional": "Encaminhamento - Terapia Ocupacional",
        "encaminhamento_psicoterapia": "Encaminhamento - Psicoterapia",
        "encaminhamento_neuropediatra": "Encaminhamento - Neuropediatra",
        "encaminhamento_psiquiatria": "Encaminhamento - Psiquiatria",
        "encaminhamento_outros": "Encaminhamento - Outros",
        "frequencia_recomendada": "Frequência recomendada",
        "focos_intervencao": "Focos de intervenção",
        "metas_iniciais": "Metas iniciais",
        "parecer_final": "Parecer final",
    }

    def __init__(self, pasta_base: Path) -> None:
        self.pasta_base = pasta_base
        app_dir = Path(__file__).resolve().parents[1]
        self.logo_path = app_dir / "static" / "logo-camargo.png"

        self.cor_primaria = colors.HexColor("#008d9f")
        self.cor_primaria_escura = colors.HexColor("#006c79")
        self.cor_rosa = colors.HexColor("#e82d72")
        self.cor_fundo = colors.HexColor("#f7f3ee")
        self.cor_grade = colors.HexColor("#b7d8dc")

    def gerar_pdf_atendimento(self, atendimento: Atendimento, recomendacoes: list[str]) -> Path:
        nome_slug = self._normalizar_nome(atendimento.nome)

        pasta_atendimento = self.pasta_base / nome_slug
        pasta_atendimento.mkdir(parents=True, exist_ok=True)

        caminho_pdf = pasta_atendimento / f"{nome_slug}_pdf.pdf"

        doc = SimpleDocTemplate(
            str(caminho_pdf),
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=3.1 * cm,
            bottomMargin=2.0 * cm,
            title="Relatório de Devolutiva Psicopedagógica",
        )

        estilos = getSampleStyleSheet()
        titulo = ParagraphStyle(
            "Titulo",
            parent=estilos["Heading1"],
            fontSize=16,
            leading=20,
            textColor=self.cor_primaria_escura,
            spaceAfter=2,
        )
        subtitulo = ParagraphStyle(
            "Subtitulo",
            parent=estilos["BodyText"],
            fontSize=10.2,
            leading=13,
            textColor=colors.HexColor("#1f4a53"),
            spaceAfter=8,
        )
        secao = ParagraphStyle(
            "Secao",
            parent=estilos["Heading2"],
            fontSize=11,
            leading=13,
            textColor=colors.white,
        )
        corpo = ParagraphStyle(
            "Corpo",
            parent=estilos["BodyText"],
            fontSize=9.2,
            leading=12,
        )
        valor_style = ParagraphStyle(
            "Valor",
            parent=corpo,
            fontSize=9.2,
            leading=12,
            textColor=colors.HexColor("#173b43"),
        )

        dados = atendimento.model_dump(mode="json")

        conteudo = [
            Paragraph("Relatório de Devolutiva Psicopedagógica", titulo),
            Paragraph("Camargo Psicopedagogia • Clínica & Inclusão", subtitulo),
            self._tabela_resumo_inicial(dados, valor_style),
            Spacer(1, 0.35 * cm),
        ]

        secoes = [
            (
                "1. Identificação",
                [
                    "nome",
                    "data_nascimento",
                    "idade",
                    "escolar",
                    "ano_escolar",
                    "responsavel_presente",
                    "cep",
                    "endereco_logradouro",
                    "endereco_numero",
                    "endereco_complemento",
                    "endereco_bairro",
                    "endereco_cidade",
                    "endereco_estado",
                    "data_avaliacao",
                    "avaliadora",
                ],
            ),
            ("2. Queixa da Avaliação", ["motivo_familia", "queixa_escolar", "historico_dificuldades"]),
            (
                "3. Histórico do Desenvolvimento",
                [
                    "intercorrencias_gravidez",
                    "tipo_parto",
                    "prematuridade",
                    "prematuridade_semanas",
                    "tempo_uti",
                    "tempo_uti_detalhes",
                    "engatinhou",
                    "sentou",
                    "andou",
                    "primeiras_palavras",
                    "frases",
                    "controle_esfincter",
                    "observacoes_marcos",
                ],
            ),
            (
                "4. Observação Comportamental",
                [
                    "atitude_inicial",
                    "contato_visual",
                    "resposta_instrucoes",
                    "foco_atencao_observacao",
                    "persistencia_tarefa",
                    "controle_emocional",
                    "interacao_avaliadora",
                    "atividade_motora",
                    "observacoes_gerais",
                ],
            ),
            (
                "5. Instrumentos Utilizados",
                [
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
                    "instrumento_outros",
                ],
            ),
            (
                "6. Funções Cognitivas",
                [
                    "atencao_sustentacao",
                    "atencao_seletividade",
                    "atencao_alternancia",
                    "atencao_dispersa",
                    "atencao_comentarios",
                    "memoria_auditiva_imediata",
                    "memoria_visual_imediata",
                    "memoria_operacional",
                    "linguagem_compreensao_oral",
                    "linguagem_expressao_verbal",
                    "linguagem_vocabulario",
                    "linguagem_articulacao",
                    "linguagem_fluencia",
                    "raciocinio_sequencia_logica",
                    "raciocinio_categorizacao",
                    "raciocinio_comparacao",
                    "raciocinio_causa_efeito",
                ],
            ),
            (
                "7. Habilidades Acadêmicas",
                [
                    "hipoteses_escrita",
                    "leitura_fluencia",
                    "leitura_compreensao",
                    "leitura_velocidade",
                    "escrita_letra",
                    "escrita_ortografia",
                    "escrita_construcao_frases",
                    "escrita_coerencia_textual",
                    "matematica_reconhecimento_numeros",
                    "matematica_contagem",
                    "matematica_operacoes_basicas",
                    "matematica_resolucao_problemas",
                    "matematica_raciocinio_logico",
                ],
            ),
            (
                "8. Aspectos Emocionais e Sociais",
                [
                    "relacionamento_avaliadora",
                    "relacionamento_pares",
                    "autoestima",
                    "autonomia",
                    "sinais_ansiedade_tristeza_dependencia",
                ],
            ),
            (
                "9. Interação e Brincadeira",
                [
                    "brincadeira_tipo_preferida",
                    "brincadeira_imaginacao_simbolismo",
                    "brincadeira_interacao_social",
                    "brincadeira_organizacao_espaco",
                    "brincadeira_persistencia_jogo",
                ],
            ),
            (
                "10. Impressões Diagnósticas (Hipóteses)",
                [
                    "hipotese_dificuldade_aprendizagem",
                    "indicios_tea",
                    "indicios_tdah",
                    "dificuldades_pedagogicas_especificas",
                    "aspectos_emocionais_envolvidos",
                    "fatores_ambientais_familiares",
                ],
            ),
            (
                "11. Recomendações",
                [
                    "recomendacao_familia",
                    "recomendacao_escola",
                    "encaminhamento_fonoaudiologia",
                    "encaminhamento_terapia_ocupacional",
                    "encaminhamento_psicoterapia",
                    "encaminhamento_neuropediatra",
                    "encaminhamento_psiquiatria",
                    "encaminhamento_outros",
                    "frequencia_recomendada",
                    "focos_intervencao",
                    "metas_iniciais",
                ],
            ),
            ("12. Parecer Final", ["parecer_final"]),
        ]

        for titulo_secao, campos in secoes:
            conteudo.append(self._bloco_titulo_secao(titulo_secao, secao))
            conteudo.append(Spacer(1, 0.06 * cm))
            tabela_dados = [
                [
                    Paragraph(f"<b>{escape(self._label(campo))}</b>", corpo),
                    Paragraph(escape(self._valor(dados.get(campo))), valor_style),
                ]
                for campo in campos
            ]
            tabela = Table(tabela_dados, colWidths=[6.2 * cm, 11.1 * cm])
            tabela.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.35, self.cor_grade),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#edf9fb")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            conteudo.append(tabela)
            conteudo.append(Spacer(1, 0.18 * cm))

        conteudo.append(Spacer(1, 0.1 * cm))
        conteudo.append(self._bloco_titulo_secao("Recomendações automáticas do sistema", secao))
        conteudo.append(Spacer(1, 0.06 * cm))
        for rec in recomendacoes:
            conteudo.append(Paragraph(f"• {escape(rec)}", corpo))

        doc.build(conteudo, onFirstPage=self._desenhar_moldura, onLaterPages=self._desenhar_moldura)
        return caminho_pdf

    def _desenhar_moldura(self, canvas: Canvas, doc: SimpleDocTemplate) -> None:
        largura, altura = A4
        canvas.saveState()

        # Faixa superior da marca
        canvas.setFillColor(self.cor_primaria_escura)
        canvas.rect(0, altura - 2.4 * cm, largura, 2.4 * cm, stroke=0, fill=1)

        canvas.setFillColor(self.cor_primaria)
        canvas.rect(0, altura - 2.5 * cm, largura, 0.1 * cm, stroke=0, fill=1)

        # Linha de destaque magenta
        canvas.setFillColor(self.cor_rosa)
        canvas.rect(0, altura - 2.55 * cm, largura, 0.05 * cm, stroke=0, fill=1)

        # Logo (se existir)
        if self.logo_path.exists():
            canvas.drawImage(
                str(self.logo_path),
                doc.leftMargin,
                altura - 2.15 * cm,
                width=1.6 * cm,
                height=1.6 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Cabeçalho textual
        x_texto = doc.leftMargin + (1.9 * cm if self.logo_path.exists() else 0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(x_texto, altura - 1.25 * cm, "CAMARGO PSICOPEDAGOGIA")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(x_texto, altura - 1.65 * cm, "Relatório de Devolutiva Psicopedagógica")

        # Rodapé
        canvas.setFillColor(self.cor_fundo)
        canvas.rect(0, 0, largura, 1.1 * cm, stroke=0, fill=1)
        canvas.setStrokeColor(self.cor_grade)
        canvas.setLineWidth(0.6)
        canvas.line(doc.leftMargin, 1.08 * cm, largura - doc.rightMargin, 1.08 * cm)

        canvas.setFillColor(colors.HexColor("#4a686f"))
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(doc.leftMargin, 0.58 * cm, "Camargo Psicopedagogia • Avaliar • Compreender • Intervir")
        canvas.drawRightString(largura - doc.rightMargin, 0.58 * cm, f"Página {canvas.getPageNumber()}")

        canvas.restoreState()

    def _bloco_titulo_secao(self, titulo_secao: str, secao_style: ParagraphStyle) -> Table:
        texto = Paragraph(escape(titulo_secao), secao_style)
        tabela = Table([[texto]], colWidths=[17.3 * cm])
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), self.cor_primaria),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("BOX", (0, 0), (-1, -1), 0.35, self.cor_primaria_escura),
                ]
            )
        )
        return tabela

    def _tabela_resumo_inicial(self, dados: dict[str, object], style: ParagraphStyle) -> Table:
        linhas = [
            [Paragraph("<b>Nome</b>", style), Paragraph(escape(self._valor(dados.get("nome"))), style)],
            [
                Paragraph("<b>Data da avaliação</b>", style),
                Paragraph(escape(self._formatar_data(self._valor(dados.get("data_avaliacao")))), style),
            ],
            [Paragraph("<b>Avaliadora</b>", style), Paragraph(escape(self._valor(dados.get("avaliadora"))), style)],
        ]

        tabela = Table(linhas, colWidths=[5.2 * cm, 12.1 * cm])
        tabela.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.35, self.cor_grade),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#edf9fb")),
                    ("BACKGROUND", (1, 0), (1, -1), colors.white),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return tabela

    @staticmethod
    def _normalizar_nome(nome: str) -> str:
        import re

        normalizado = re.sub(r"[^a-zA-Z0-9]+", "_", nome.strip().lower())
        return normalizado.strip("_") or "paciente"

    @staticmethod
    def _label(chave: str) -> str:
        return PDFService.ROTULOS.get(chave, chave.replace("_", " ").strip().capitalize())

    @staticmethod
    def _valor(valor: object) -> str:
        if isinstance(valor, bool):
            return "Sim" if valor else "Não"
        if valor is None:
            return "-"
        texto = str(valor).strip()
        return texto if texto else "-"

    @staticmethod
    def _formatar_data(valor: str) -> str:
        if len(valor) == 10 and valor[4] == "-" and valor[7] == "-":
            ano, mes, dia = valor.split("-")
            return f"{dia}/{mes}/{ano}"
        return valor
