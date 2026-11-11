"""Regressao linear calculada pelas formulas, sem bibliotecas externas."""


def regressao_linear(valores_x, valores_y):
    """Retorna coeficiente angular e termo independente de y = a*x + b."""
    if len(valores_x) != len(valores_y) or len(valores_x) < 2:
        raise ValueError("As listas precisam ter o mesmo tamanho e pelo menos 2 dados.")

    quantidade = len(valores_x)
    soma_x = sum(valores_x)
    soma_y = sum(valores_y)
    soma_xy = 0.0
    soma_x2 = 0.0

    for indice in range(quantidade):
        soma_xy += valores_x[indice] * valores_y[indice]
        soma_x2 += valores_x[indice] ** 2

    denominador = quantidade * soma_x2 - soma_x ** 2
    if denominador == 0:
        raise ValueError("Nao existe reta unica: todos os valores de vento sao iguais.")

    a = (quantidade * soma_xy - soma_x * soma_y) / denominador
    b = (soma_y - a * soma_x) / quantidade
    return a, b


def prever_energia(vento_ms, a, b):
    """Valores negativos de energia nao fazem sentido na simulacao."""
    return max(0.0, a * vento_ms + b)


def erro_medio_absoluto(valores_x, valores_y, a, b):
    """Media dos erros absolutos nos proprios dados historicos."""
    erros = []
    for indice in range(len(valores_x)):
        estimativa = prever_energia(valores_x[indice], a, b)
        erros.append(abs(valores_y[indice] - estimativa))
    return sum(erros) / len(erros)


def residuos_e_r2(valores_x, valores_y, a, b):
    """Calcula os residuos e o R² do ajuste nos dados historicos."""
    media = sum(valores_y) / len(valores_y)
    soma_residuos2 = 0.0
    soma_total2 = 0.0
    residuos = []
    for i in range(len(valores_x)):
        previsto = prever_energia(valores_x[i], a, b)
        residuo = valores_y[i] - previsto
        residuos.append(residuo)
        soma_residuos2 += residuo ** 2
        soma_total2 += (valores_y[i] - media) ** 2

    # Todos os valores observados iguais: nao ha variacao para explicar.
    if soma_total2 == 0:
        r2 = 1.0 if soma_residuos2 == 0 else 0.0
    else:
        r2 = 1 - soma_residuos2 / soma_total2
    return residuos, r2
