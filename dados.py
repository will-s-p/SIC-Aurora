"""Dados de exemplo da colonia. Um ciclo da simulacao equivale a uma hora."""
from copy import deepcopy


HISTORICO_EOLICO = {
    "vento_ms": [8, 10, 12, 14, 16],
    "energia_kwh": [19, 24, 31, 34, 40],
}


def criar_colonia():
    """Monta a hierarquia de sistemas com dados ficticios para a atividade."""
    return {
        "nome": "Aurora Siger",
        "energia": {
            "fontes": {
                "solar": {"geracao_atual_kwh": 45.0, "previsao_proxima_hora_kwh": 42.0},
                "eolica": {"geracao_atual_kwh": 30.0, "vento_previsto_ms": 12.0},
            },
            "reserva_kwh": 90.0,
            "capacidade_reserva_kwh": 200.0,
        },
        "clima": {"temperatura_c": -40.0, "tempestade": False},
        "consumidores": {
            "essenciais": [
                {"nome": "Suporte a vida", "consumo_kwh": 26.0, "prioridade": 1, "ligado": True},
                {"nome": "Enfermaria", "consumo_kwh": 9.0, "prioridade": 1, "ligado": True},
                {"nome": "Comunicacoes", "consumo_kwh": 5.0, "prioridade": 1, "ligado": True},
            ],
            "nao_essenciais": [
                {"nome": "Laboratorio", "consumo_kwh": 16.0, "prioridade": 2, "ligado": True},
                {"nome": "Conforto", "consumo_kwh": 10.0, "prioridade": 3, "ligado": True},
                {"nome": "Iluminacao externa", "consumo_kwh": 4.0, "prioridade": 4, "ligado": True},
            ],
        },
        "historico_eolico": deepcopy(HISTORICO_EOLICO),
    }


def criar_cenarios():
    """Variacoes do mesmo estado, para comparar as decisoes."""
    base = criar_colonia()
    cenarios = {}

    cenarios["1 - Operacao estavel"] = deepcopy(base)

    deficit = deepcopy(base)
    deficit["energia"]["fontes"]["solar"]["geracao_atual_kwh"] = 20
    deficit["energia"]["fontes"]["solar"]["previsao_proxima_hora_kwh"] = 15
    deficit["energia"]["fontes"]["eolica"]["geracao_atual_kwh"] = 22
    deficit["energia"]["fontes"]["eolica"]["vento_previsto_ms"] = 10
    deficit["energia"]["reserva_kwh"] = 105
    cenarios["2 - Queda de geracao"] = deficit

    emergencia = deepcopy(base)
    emergencia["energia"]["fontes"]["solar"]["geracao_atual_kwh"] = 10
    emergencia["energia"]["fontes"]["solar"]["previsao_proxima_hora_kwh"] = 8
    emergencia["energia"]["fontes"]["eolica"]["geracao_atual_kwh"] = 10
    emergencia["energia"]["fontes"]["eolica"]["vento_previsto_ms"] = 8
    emergencia["energia"]["reserva_kwh"] = 25
    cenarios["3 - Emergencia energetica"] = emergencia

    risco_vida = deepcopy(base)
    risco_vida["energia"]["fontes"]["solar"]["geracao_atual_kwh"] = 1
    risco_vida["energia"]["fontes"]["solar"]["previsao_proxima_hora_kwh"] = 1
    risco_vida["energia"]["fontes"]["eolica"]["geracao_atual_kwh"] = 1
    risco_vida["energia"]["fontes"]["eolica"]["vento_previsto_ms"] = 8
    risco_vida["energia"]["reserva_kwh"] = 12
    cenarios["4 - Risco ao suporte a vida"] = risco_vida

    tempestade = deepcopy(base)
    tempestade["energia"]["fontes"]["solar"]["geracao_atual_kwh"] = 40
    tempestade["energia"]["fontes"]["solar"]["previsao_proxima_hora_kwh"] = 35
    tempestade["energia"]["fontes"]["eolica"]["geracao_atual_kwh"] = 35
    tempestade["energia"]["fontes"]["eolica"]["vento_previsto_ms"] = 14
    tempestade["energia"]["reserva_kwh"] = 100
    tempestade["clima"]["tempestade"] = True
    tempestade["clima"]["temperatura_c"] = -68
    cenarios["5 - Tempestade e frio extremo"] = tempestade

    excesso = deepcopy(base)
    excesso["energia"]["fontes"]["solar"]["geracao_atual_kwh"] = 65
    excesso["energia"]["fontes"]["solar"]["previsao_proxima_hora_kwh"] = 58
    excesso["energia"]["fontes"]["eolica"]["geracao_atual_kwh"] = 45
    excesso["energia"]["fontes"]["eolica"]["vento_previsto_ms"] = 14
    excesso["energia"]["reserva_kwh"] = 198
    cenarios["6 - Excesso de geracao"] = excesso

    return cenarios
