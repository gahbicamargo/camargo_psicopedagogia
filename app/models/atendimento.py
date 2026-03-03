from datetime import date

from pydantic import BaseModel, Field, field_validator


class Atendimento(BaseModel):
    # 1. Identificação
    nome: str = Field(min_length=2, max_length=120)
    data_nascimento: date | None = None
    idade: int | None = Field(default=None, ge=0, le=120)
    escolar: str = ""
    ano_escolar: str = ""
    responsavel_presente: str = ""
    cep: str = ""
    endereco_logradouro: str = ""
    endereco_numero: str = ""
    endereco_complemento: str = ""
    endereco_bairro: str = ""
    endereco_cidade: str = ""
    endereco_estado: str = ""
    data_avaliacao: date
    avaliadora: str = ""

    # 2. Motivo da Avaliação
    motivo_familia: str = ""
    queixa_escolar: str = ""
    historico_dificuldades: str = ""

    # 3. Histórico do Desenvolvimento
    intercorrencias_gravidez: str = ""
    tipo_parto: str = ""
    prematuridade: bool = False
    prematuridade_semanas: str = ""
    tempo_uti: bool = False
    tempo_uti_detalhes: str = ""
    engatinhou: str = ""
    sentou: str = ""
    andou: str = ""
    primeiras_palavras: str = ""
    frases: str = ""
    controle_esfincter: str = ""
    observacoes_marcos: str = ""

    # 4. Observação Comportamental
    atitude_inicial: str = ""
    contato_visual: str = ""
    resposta_instrucoes: str = ""
    foco_atencao_observacao: str = ""
    persistencia_tarefa: str = ""
    controle_emocional: str = ""
    interacao_avaliadora: str = ""
    atividade_motora: str = ""
    observacoes_gerais: str = ""

    # 5. Instrumentos Utilizados
    instrumento_entrevista_responsaveis: bool = False
    instrumento_observacao_ludica: bool = False
    instrumento_desenhos: bool = False
    instrumento_piaget: bool = False
    instrumento_conservacao: bool = False
    instrumento_classificacao: bool = False
    instrumento_seriacao: bool = False
    instrumento_linguagem: bool = False
    instrumento_consciencia_fonologica: bool = False
    instrumento_leitura_escrita: bool = False
    instrumento_matematica: bool = False
    instrumento_testes_projetivos: bool = False
    instrumento_protocolos_especificos: bool = False
    instrumento_outros: str = ""

    # 6. Funções Cognitivas
    atencao_sustentacao: str = ""
    atencao_seletividade: str = ""
    atencao_alternancia: str = ""
    atencao_dispersa: str = ""
    atencao_comentarios: str = ""

    memoria_auditiva_imediata: str = ""
    memoria_visual_imediata: str = ""
    memoria_operacional: str = ""

    linguagem_compreensao_oral: str = ""
    linguagem_expressao_verbal: str = ""
    linguagem_vocabulario: str = ""
    linguagem_articulacao: str = ""
    linguagem_fluencia: str = ""

    raciocinio_sequencia_logica: str = ""
    raciocinio_categorizacao: str = ""
    raciocinio_comparacao: str = ""
    raciocinio_causa_efeito: str = ""

    # 7. Habilidades Acadêmicas
    hipoteses_escrita: str = ""
    leitura_fluencia: str = ""
    leitura_compreensao: str = ""
    leitura_velocidade: str = ""

    escrita_letra: str = ""
    escrita_ortografia: str = ""
    escrita_construcao_frases: str = ""
    escrita_coerencia_textual: str = ""

    matematica_reconhecimento_numeros: str = ""
    matematica_contagem: str = ""
    matematica_operacoes_basicas: str = ""
    matematica_resolucao_problemas: str = ""
    matematica_raciocinio_logico: str = ""

    # 8. Aspectos Emocionais e Sociais
    relacionamento_avaliadora: str = ""
    relacionamento_pares: str = ""
    autoestima: str = ""
    autonomia: str = ""
    sinais_ansiedade_tristeza_dependencia: str = ""

    # 9. Interação e Brincadeira
    brincadeira_tipo_preferida: str = ""
    brincadeira_imaginacao_simbolismo: str = ""
    brincadeira_interacao_social: str = ""
    brincadeira_organizacao_espaco: str = ""
    brincadeira_persistencia_jogo: str = ""

    # 10. Impressões Diagnósticas
    hipotese_dificuldade_aprendizagem: str = ""
    indicios_tea: str = ""
    indicios_tdah: str = ""
    dificuldades_pedagogicas_especificas: str = ""
    aspectos_emocionais_envolvidos: str = ""
    fatores_ambientais_familiares: str = ""

    # 11. Recomendações
    recomendacao_familia: str = ""
    recomendacao_escola: str = ""
    encaminhamento_fonoaudiologia: bool = False
    encaminhamento_terapia_ocupacional: bool = False
    encaminhamento_psicoterapia: bool = False
    encaminhamento_neuropediatra: bool = False
    encaminhamento_psiquiatria: bool = False
    encaminhamento_outros: str = ""
    frequencia_recomendada: str = ""
    focos_intervencao: str = ""
    metas_iniciais: str = ""

    # 12. Parecer Final
    parecer_final: str = ""

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise ValueError("O nome é obrigatório.")
        return nome

    def linha_csv(self) -> dict[str, str]:
        dados = self.model_dump(mode="json")
        linha: dict[str, str] = {}
        for chave, valor in dados.items():
            titulo = chave.replace("_", " ").title()
            if isinstance(valor, bool):
                linha[titulo] = "Sim" if valor else "Não"
            else:
                linha[titulo] = "" if valor is None else str(valor)
        return linha
