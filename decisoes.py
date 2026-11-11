"""Regras da colonia: primeiro seguranca, depois economia de recursos."""
from copy import deepcopy

from energia import (
    calcular_consumo, consumo_essencial, geracao_atual,
    ordenar_desligamento, validar_colonia,
)
from matematica import regressao_linear, prever_energia, erro_medio_absoluto, residuos_e_r2


PESO_NIVEL = {"CRITICO": 1, "ALERTA": 2, "ATENCAO": 3, "SUGESTAO": 4, "INFO": 5}
LIMIAR_RESERVA = 0.25  # Meta de reserva para a proxima hora: 25% da bateria.
LIMITE_VENTO_MS = 25.0  # Limite de corte ficticio da turbina (capitulo de energia eolica).


def avaliar_colonia(dados):
    """Simula a hora atual e decide o que fazer na proxima hora.

    A copia evita modificar o cenario original entre as execucoes.
    """
    colonia = deepcopy(dados)
    validar_colonia(colonia)
    acoes = []

    def registrar(nivel, mensagem):
        acoes.append({"nivel": nivel, "mensagem": mensagem})

    historico = colonia["historico_eolico"]
    x = historico["vento_ms"]
    y = historico["energia_kwh"]
    a, b = regressao_linear(x, y)
    erro = erro_medio_absoluto(x, y, a, b)
    residuos, r2 = residuos_e_r2(x, y, a, b)

    energia = colonia["energia"]
    fontes = energia["fontes"]
    reserva_inicial = energia["reserva_kwh"]
    capacidade = energia["capacidade_reserva_kwh"]
    geracao = geracao_atual(colonia)
    consumo_inicial = calcular_consumo(colonia)
    demanda_essencial = consumo_essencial(colonia)

    vento_previsto = fontes["eolica"]["vento_previsto_ms"]
    # O ajuste linear vale na faixa do historico. Ventos extremos exigem seguranca.
    if vento_previsto >= LIMITE_VENTO_MS:
        eolica_prevista = 0.0
        registrar("ALERTA", "Vento extremo: turbina parada por seguranca (limite simulado de 25 m/s).")
    else:
        eolica_prevista = prever_energia(vento_previsto, a, b)
    solar_prevista = fontes["solar"]["previsao_proxima_hora_kwh"]
    geracao_prevista = eolica_prevista + solar_prevista

    if vento_previsto < min(x) or vento_previsto > max(x):
        registrar("ATENCAO", "Vento fora da faixa historica: a previsao e uma extrapolacao.")

    # Primeira preocupacao: existe energia suficiente para a hora em andamento?
    energia_disponivel = geracao + reserva_inicial
    if consumo_inicial > energia_disponivel:
        registrar("CRITICO", "Demanda atual maior que geracao + reserva; iniciar cortes emergenciais.")
        for sistema in ordenar_desligamento(colonia):
            if calcular_consumo(colonia) <= energia_disponivel:
                break
            sistema["ligado"] = False
            registrar("CRITICO", "Desligar agora: " + sistema["nome"] + " (nao essencial).")

    consumo_atual = calcular_consumo(colonia)
    falta_atual = max(0.0, consumo_atual - energia_disponivel)
    if falta_atual > 0:
        registrar(
            "CRITICO",
            f"Mesmo apos os cortes faltam {falta_atual:.1f} kWh para a hora atual. "
            "Acionar equipe e fonte de emergencia; nao desligar suporte a vida.",
        )

    saldo_atual = geracao - consumo_atual
    reserva_bruta = reserva_inicial + saldo_atual
    reserva_apos_hora = min(capacidade, max(0.0, reserva_bruta))
    energia_sem_armazenamento = max(0.0, reserva_bruta - capacidade)

    if saldo_atual < 0:
        registrar("ALERTA", f"Consumo atual supera geracao em {-saldo_atual:.1f} kWh; uso da reserva.")
    elif saldo_atual > 0:
        armazenado = min(saldo_atual, capacidade - reserva_inicial)
        if armazenado > 0:
            registrar("SUGESTAO", f"Armazenar {armazenado:.1f} kWh do excedente desta hora.")
        if energia_sem_armazenamento > 0:
            registrar("SUGESTAO", f"Excedente sem espaco na bateria: {energia_sem_armazenamento:.1f} kWh.")

    # Previsao: se mantivermos os equipamentos ligados, como ficara a reserva?
    consumo_antes_prevencao = calcular_consumo(colonia)
    reserva_prevista_antes = reserva_apos_hora + geracao_prevista - consumo_antes_prevencao
    meta_reserva = LIMIAR_RESERVA * capacidade

    # Logica booleana: duas condicoes precisam ser verdadeiras para o alerta combinado.
    consumo_supera_geracao = consumo_inicial > geracao
    reserva_baixa = reserva_prevista_antes < meta_reserva
    if consumo_supera_geracao and reserva_baixa:
        registrar("ALERTA", "Geracao insuficiente e reserva prevista baixa: priorizar economia.")

    if reserva_baixa:
        registrar(
            "ATENCAO",
            f"Reserva prevista de {max(0.0, reserva_prevista_antes):.1f} kWh "
            f"abaixo da meta de {meta_reserva:.1f} kWh; avaliar economia preventiva.",
        )
        for sistema in ordenar_desligamento(colonia):
            reserva_simulada = reserva_apos_hora + geracao_prevista - calcular_consumo(colonia)
            if reserva_simulada >= meta_reserva:
                break
            sistema["ligado"] = False
            registrar("ATENCAO", "Desligar na proxima hora: " + sistema["nome"] + ".")

    consumo_proxima_hora = calcular_consumo(colonia)
    reserva_proxima_bruta = reserva_apos_hora + geracao_prevista - consumo_proxima_hora
    reserva_prevista = min(capacidade, max(0.0, reserva_proxima_bruta))
    falta_proxima = max(0.0, -reserva_proxima_bruta)

    if falta_proxima > 0:
        registrar(
            "CRITICO",
            f"Projecao indica falta de {falta_proxima:.1f} kWh na proxima hora, "
            "mesmo apos os cortes; providenciar fonte extra.",
        )
    elif reserva_prevista < meta_reserva:
        registrar("ALERTA", "Reserva da proxima hora continua abaixo da meta; manter monitoramento.")

    # O clima e uma segunda fonte de risco, independente do saldo eletrico.
    clima = colonia["clima"]
    if clima["tempestade"]:
        registrar("ALERTA", "Tempestade registrada: suspender atividades externas.")
    if clima["temperatura_c"] <= -65:
        registrar("ALERTA", "Frio extremo: verificar aquecimento do suporte a vida.")

    if not acoes:
        registrar("INFO", "Sem alertas neste ciclo; continuar acompanhando os sensores.")

    # Acoes mais urgentes aparecem primeiro, mantendo a ordem dentro do nivel.
    acoes.sort(key=lambda item: PESO_NIVEL[item["nivel"]])
    desligados = [s["nome"] for s in colonia["consumidores"]["nao_essenciais"] if not s["ligado"]]

    return {
        "nome": colonia["nome"],
        "geracao_atual_kwh": geracao,
        "consumo_inicial_kwh": consumo_inicial,
        "consumo_apos_cortes_kwh": consumo_atual,
        "consumo_proxima_hora_kwh": consumo_proxima_hora,
        "reserva_inicial_kwh": reserva_inicial,
        "reserva_apos_hora_kwh": reserva_apos_hora,
        "reserva_proxima_hora_kwh": reserva_prevista,
        "geracao_eolica_prevista_kwh": eolica_prevista,
        "geracao_solar_prevista_kwh": solar_prevista,
        "geracao_total_prevista_kwh": geracao_prevista,
        "consumo_essencial_kwh": demanda_essencial,
        "energia_sem_armazenamento_kwh": energia_sem_armazenamento,
        "reserva_prevista_sem_prevencao_kwh": reserva_prevista_antes,
        "modelo": {"a": a, "b": b, "erro_medio_absoluto": erro, "residuos": residuos,
                   "r2": r2, "faixa_vento": (min(x), max(x))},
        "desligados": desligados,
        "acoes": acoes,
    }
