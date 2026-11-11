"""Entrada do simulador da colonia Aurora Siger (Python 3, sem pacotes)."""
from copy import deepcopy

from dados import criar_cenarios, criar_colonia
from decisoes import avaliar_colonia
from energia import buscar_sistema


def mostrar_resultado(titulo, resultado):
    print("\n" + "=" * 64)
    print(titulo.upper())
    print("=" * 64)
    print(f"Geracao atual: {resultado['geracao_atual_kwh']:.1f} kWh")
    print(f"Consumo inicial: {resultado['consumo_inicial_kwh']:.1f} kWh")
    print(f"Consumo apos eventuais cortes: {resultado['consumo_apos_cortes_kwh']:.1f} kWh")
    print(f"Reserva inicial: {resultado['reserva_inicial_kwh']:.1f} kWh")
    print(f"Reserva ao fim da hora atual: {resultado['reserva_apos_hora_kwh']:.1f} kWh")
    print(f"Eolica prevista: {resultado['geracao_eolica_prevista_kwh']:.1f} kWh")
    print(f"Geracao total prevista: {resultado['geracao_total_prevista_kwh']:.1f} kWh")
    print(f"Consumo planejado da proxima hora: {resultado['consumo_proxima_hora_kwh']:.1f} kWh")
    print(f"Reserva prevista apos decisoes: {resultado['reserva_proxima_hora_kwh']:.1f} kWh")
    modelo = resultado["modelo"]
    print(f"Modelo eolico: energia = {modelo['a']:.2f} * vento {modelo['b']:+.2f}")
    print(f"Erro medio absoluto nos dados: {modelo['erro_medio_absoluto']:.2f} kWh")
    print(f"Coeficiente de determinacao R2: {modelo['r2']:.4f}")
    print("\nDECISOES (por gravidade):")
    for acao in resultado["acoes"]:
        print(f"  [{acao['nivel']}] {acao['mensagem']}")


def ler_numero(pergunta, atual):
    while True:
        valor = input(f"{pergunta} [{atual}]: ").strip().replace(",", ".")
        if not valor:
            return float(atual)
        try:
            numero = float(valor)
            if numero < 0:
                print("O valor nao pode ser negativo.")
            else:
                return numero
        except ValueError:
            print("Digite um numero valido.")


def executar_personalizado():
    colonia = deepcopy(criar_colonia())
    fontes = colonia["energia"]["fontes"]
    solar = fontes["solar"]
    eolica = fontes["eolica"]
    print("\nEdite apenas o que desejar. ENTER mantem o valor de exemplo.")
    solar["geracao_atual_kwh"] = ler_numero("Solar agora (kWh)", solar["geracao_atual_kwh"])
    eolica["geracao_atual_kwh"] = ler_numero("Eolica agora (kWh)", eolica["geracao_atual_kwh"])
    solar["previsao_proxima_hora_kwh"] = ler_numero("Solar na proxima hora (kWh)", solar["previsao_proxima_hora_kwh"])
    eolica["vento_previsto_ms"] = ler_numero("Vento previsto (m/s)", eolica["vento_previsto_ms"])
    colonia["energia"]["reserva_kwh"] = ler_numero("Reserva atual (kWh)", colonia["energia"]["reserva_kwh"])
    colonia["clima"]["tempestade"] = input("Ha tempestade? (s/N): ").strip().lower() == "s"
    print("\nDica: altere consumo de um subsistema pelo nome, ou ENTER para manter.")
    nome = input("Sistema (ex.: Laboratorio): ").strip()
    if nome:
        sistema = buscar_sistema(colonia, nome)
        if sistema is None:
            print("Sistema nao encontrado; consumos mantidos.")
        else:
            sistema["consumo_kwh"] = ler_numero("Novo consumo (kWh)", sistema["consumo_kwh"])
    try:
        mostrar_resultado("Simulacao personalizada", avaliar_colonia(colonia))
    except ValueError as erro:
        print("Nao foi possivel simular:", erro)


def executar_menu():
    cenarios = criar_cenarios()
    while True:
        print("\nSIC-AURORA | Simulador de energia da colonia Aurora Siger")
        print("1 - Rodar um cenario")
        print("2 - Rodar os seis cenarios")
        print("3 - Informar meus proprios dados")
        print("0 - Sair")
        escolha = input("Opcao: ").strip()
        if escolha == "0":
            print("Encerrado.")
            break
        if escolha == "1":
            nomes = list(cenarios.keys())
            for nome in nomes:
                print(nome)
            numero = input("Numero do cenario: ").strip()
            if numero.isdigit() and 1 <= int(numero) <= len(nomes):
                titulo = nomes[int(numero) - 1]
                mostrar_resultado(titulo, avaliar_colonia(cenarios[titulo]))
            else:
                print("Cenario invalido.")
        elif escolha == "2":
            for titulo, colonia in cenarios.items():
                mostrar_resultado(titulo, avaliar_colonia(colonia))
        elif escolha == "3":
            executar_personalizado()
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    executar_menu()
