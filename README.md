# SIC-Aurora - Sistema Integrado da Colônia Aurora Siger

O SIC-Aurora é um simulador em Python para acompanhar o funcionamento energético da colônia fictícia Aurora Siger. O projeto reúne dados de geração solar e eólica, consumo dos setores, reserva da bateria e condições climáticas. Com essas informações, calcula o balanço de energia, estima a geração eólica da próxima hora e emite avisos conforme a situação identificada.

O programa funciona no terminal e utiliza dados simulados. Não se conecta a sensores nem controla equipamentos reais.

## Funcionalidades

- Registro de energia, clima, consumidores e observações históricas em listas e dicionários.
- Consulta de setores por busca sequencial e ordenação dos setores não essenciais por prioridade.
- Cálculo do consumo, da geração atual, do saldo energético e da reserva disponível.
- Previsão de geração eólica por regressão linear simples (mínimos quadrados).
- Avaliação do ajuste da regressão por resíduos, erro médio absoluto e R².
- Simulação de cortes imediatos ou preventivos, sem desligamento automático dos serviços essenciais.
- Avisos de tempestade, frio extremo, excesso de energia e possível falta de abastecimento.
- Execução de seis cenários de teste ou de um cenário com valores informados no menu.

## Execução

**Requisito:** Python 3. O simulador não depende de bibliotecas externas.

Na pasta principal do projeto, execute:

```bash
python main.py
```

O menu apresenta três opções: executar um dos cenários disponíveis, comparar todos os cenários ou informar valores personalizados de geração, reserva, vento e consumo de um setor.

Para executar os testes automatizados:

```bash
python -m unittest discover -s tests -v
```

A suíte tem 16 testes e cobre os cálculos, as decisões, a integridade dos dados e os diferentes níveis de risco.

## Organização do código

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Menu, leitura de valores e apresentação dos resultados. |
| `dados.py` | Estrutura da colônia, dados históricos e seis cenários simulados. |
| `matematica.py` | Regressão linear, cálculo da previsão, resíduos, R² e erro médio absoluto. |
| `energia.py` | Consumo, geração, busca sequencial, ordenação por prioridade e validações. |
| `decisoes.py` | Regras de segurança, balanço energético e simulação das ações. |
| `tests/test_sistema.py` | Testes automatizados com `unittest`. |
| `docs/relatorio.docx` | Relatório do projeto, incluindo modelagem e resultados. |
| `docs/exemplos_execucao.txt` | Registro da saída dos seis cenários. |
| `docs/resultado_testes.txt` | Registro de uma execução dos testes. |
| `docs/teste_entrada_manual.txt` | Exemplo de utilização com entrada personalizada. |

Os dados são representados por um dicionário principal com quatro grupos: `energia`, `clima`, `consumidores` e `historico_eolico`. A energia é subdividida em fontes solar e eólica, reserva e capacidade da bateria. Os consumidores são separados em duas listas, uma de serviços essenciais e outra de serviços não essenciais. Cada setor registra nome, consumo em kWh por ciclo, prioridade e estado ligado/desligado.

A busca de setores é sequencial. Para decidir a ordem dos cortes, o programa utiliza Selection Sort sobre os setores não essenciais ligados. Nesse conjunto, prioridade 4 significa menor importância e é considerada antes de 3 e 2. Os serviços essenciais têm prioridade 1 e permanecem ligados no modelo de decisão.

## Modelo de previsão

As observações de vento e geração são fictícias e correspondem a ciclos de uma hora:

| Vento (m/s) | Energia eólica (kWh) |
| ---: | ---: |
| 8 | 19 |
| 10 | 24 |
| 12 | 31 |
| 14 | 34 |
| 16 | 40 |

Com o método dos mínimos quadrados, a relação estimada é:

```text
Energia eolica prevista (kWh) = 2,6 * vento (m/s) - 1,6
```

Para vento de 11 m/s, a estimativa é de 27 kWh. Nos cinco registros usados no ajuste, o erro médio absoluto é 0,56 kWh e o coeficiente R² é aproximadamente 0,9898. Esses indicadores descrevem o ajuste aos exemplos apresentados, não garantem precisão em outras condições.

A previsão por regressão é considerada uma aproximação didática. Quando a velocidade prevista está fora do intervalo observado (8 a 16 m/s), o sistema emite um aviso sobre extrapolação. A partir de 25 m/s, considera-se uma parada preventiva da turbina, com geração eólica prevista igual a zero. Esse limite foi adotado para a simulação.

## Análise de energia e decisões

Cada ciclo da simulação corresponde a uma hora. O consumo é obtido pela soma dos setores ligados; a geração atual é a soma das fontes solar e eólica. O saldo da hora é a diferença entre geração e consumo. A reserva é atualizada sem ultrapassar a capacidade da bateria e sem assumir valores negativos.

O programa compara a energia disponível com a demanda e também calcula uma projeção para a hora seguinte. Para essa previsão, soma a geração eólica estimada à previsão solar fornecida como entrada. Uma reserva projetada abaixo de 25% da capacidade desencadeia a avaliação de economia preventiva. O percentual é uma escolha para o exercício, não um parâmetro operacional real.

As principais regras são:

| Condição | Resposta do simulador |
| --- | --- |
| Geração e reserva atuais não cobrem o consumo. | Propõe desligar setores não essenciais, por ordem de prioridade. |
| A energia ainda é insuficiente após os cortes. | Emite alerta crítico e solicita intervenção humana e fonte adicional. |
| O consumo atual supera a geração. | Indica o déficit coberto pela bateria. |
| A reserva prevista fica abaixo da meta de 25%. | Propõe redução preventiva do consumo na próxima hora. |
| Há déficit atual de geração **e** reserva prevista abaixo da meta. | Emite um alerta combinado de risco. |
| O vento previsto é igual ou superior a 25 m/s. | Considera a turbina parada na previsão. |
| A geração supera o consumo. | Sugere armazenar o excedente e sinaliza energia sem espaço na bateria. |
| Há tempestade ou temperatura de -65 °C ou menor. | Recomenda suspender atividades externas ou verificar o aquecimento. |

As ações são apresentadas por gravidade: CRÍTICO, ALERTA, ATENÇÃO, SUGESTÃO e INFO. O algoritmo não desliga suporte à vida, enfermaria ou comunicações. Caso a energia disponível não seja suficiente nem para esses serviços, informa a falta em vez de tratar a situação como resolvida.

## Exemplo de execução

No cenário de queda de geração, os valores iniciais são 20 kWh de energia solar, 22 kWh de energia eólica, 70 kWh de consumo e 105 kWh de reserva.

```text
Geracao atual: 42.0 kWh
Consumo inicial: 70.0 kWh
Reserva ao fim da hora atual: 77.0 kWh
Eolica prevista: 24.4 kWh
Geracao total prevista: 39.4 kWh
Reserva prevista apos decisoes: 50.4 kWh

[ALERTA] Consumo atual supera geracao em 28.0 kWh; uso da reserva.
[ATENCAO] Desligar na proxima hora: Iluminacao externa.
```

Sem redução do consumo, a previsão seria de 46,4 kWh de reserva, abaixo da meta de 50 kWh. Ao prever o desligamento da iluminação externa, que utiliza 4 kWh no ciclo, o programa eleva a reserva projetada para 50,4 kWh.

Os demais exemplos estão registrados em `docs/exemplos_execucao.txt` e abrangem operação estável, emergência energética, risco ao suporte à vida, tempestade com frio extremo e excesso de geração.

## Limitações

O SIC-Aurora utiliza valores fictícios, ciclos de uma hora e consumo constante durante cada ciclo. A geração solar futura é informada como entrada; somente a geração eólica é estimada por regressão. A relação entre vento e energia de uma turbina real depende de fatores que não estão representados no modelo linear. Os alertas são orientações dentro da simulação, não comandos de operação de uma instalação física.
