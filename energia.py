"""Calculos de consumo, fontes geradoras e armazenamento."""


def listar_sistemas(colonia):
    """Percorre os dois grupos da arvore de consumidores."""
    todos = []
    for grupo in ("essenciais", "nao_essenciais"):
        for sistema in colonia["consumidores"][grupo]:
            todos.append(sistema)
    return todos


def buscar_sistema(colonia, nome):
    """Busca sequencial simples na estrutura hierarquica."""
    for sistema in listar_sistemas(colonia):
        if sistema["nome"].lower() == nome.lower():
            return sistema
    return None


def calcular_consumo(colonia):
    total = 0.0
    for sistema in listar_sistemas(colonia):
        if sistema["ligado"]:
            total += sistema["consumo_kwh"]
    return total


def consumo_essencial(colonia):
    total = 0.0
    for sistema in colonia["consumidores"]["essenciais"]:
        if sistema["ligado"]:
            total += sistema["consumo_kwh"]
    return total


def geracao_atual(colonia):
    fontes = colonia["energia"]["fontes"]
    return fontes["solar"]["geracao_atual_kwh"] + fontes["eolica"]["geracao_atual_kwh"]


def ordenar_desligamento(colonia):
    """Selection Sort: maior numero de prioridade = menor importancia."""
    sistemas = []
    for sistema in colonia["consumidores"]["nao_essenciais"]:
        if sistema["ligado"]:
            sistemas.append(sistema)

    for i in range(len(sistemas) - 1):
        indice_menor_importancia = i
        for j in range(i + 1, len(sistemas)):
            if sistemas[j]["prioridade"] > sistemas[indice_menor_importancia]["prioridade"]:
                indice_menor_importancia = j
        sistemas[i], sistemas[indice_menor_importancia] = (
            sistemas[indice_menor_importancia], sistemas[i]
        )
    return sistemas


def validar_colonia(colonia):
    """Evita resultados impossiveis causados por dados negativos ou reserva invalida."""
    energia = colonia["energia"]
    fontes = energia["fontes"]
    valores = [
        energia["reserva_kwh"],
        energia["capacidade_reserva_kwh"],
        fontes["solar"]["geracao_atual_kwh"],
        fontes["solar"]["previsao_proxima_hora_kwh"],
        fontes["eolica"]["geracao_atual_kwh"],
        fontes["eolica"]["vento_previsto_ms"],
    ]
    for sistema in listar_sistemas(colonia):
        valores.append(sistema["consumo_kwh"])

    if any(valor < 0 for valor in valores):
        raise ValueError("Energia, consumo, reserva e vento nao podem ser negativos.")
    if energia["capacidade_reserva_kwh"] <= 0:
        raise ValueError("A capacidade da bateria deve ser maior que zero.")
    if energia["reserva_kwh"] > energia["capacidade_reserva_kwh"]:
        raise ValueError("A reserva inicial nao pode superar a capacidade da bateria.")
    if not all(sistema["ligado"] for sistema in colonia["consumidores"]["essenciais"]):
        raise ValueError("Os sistemas essenciais devem iniciar ligados.")
