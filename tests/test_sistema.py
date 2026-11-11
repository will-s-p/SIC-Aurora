"""Testes executaveis com o unittest da biblioteca padrao."""
import unittest

from dados import criar_colonia, criar_cenarios
from matematica import regressao_linear, prever_energia, erro_medio_absoluto, residuos_e_r2
from energia import buscar_sistema, calcular_consumo, ordenar_desligamento
from decisoes import avaliar_colonia


class TestesMatematica(unittest.TestCase):
    def test_regressao_e_previsao(self):
        x = [8, 10, 12, 14, 16]
        y = [19, 24, 31, 34, 40]
        a, b = regressao_linear(x, y)
        self.assertAlmostEqual(a, 2.6)
        self.assertAlmostEqual(b, -1.6)
        self.assertAlmostEqual(prever_energia(11, a, b), 27.0)
        self.assertAlmostEqual(erro_medio_absoluto(x, y, a, b), 0.56)

    def test_residuos_e_r2(self):
        x = [8, 10, 12, 14, 16]
        y = [19, 24, 31, 34, 40]
        a, b = regressao_linear(x, y)
        residuos, r2 = residuos_e_r2(x, y, a, b)
        self.assertEqual(len(residuos), 5)
        self.assertAlmostEqual(residuos[2], 1.4)
        self.assertAlmostEqual(r2, 0.98975, places=4)

    def test_rejeita_lista_invalida(self):
        with self.assertRaises(ValueError):
            regressao_linear([8, 10, 12], [19, 24])
        with self.assertRaises(ValueError):
            regressao_linear([8, 8, 8], [19, 24, 31])


class TestesEstruturaEDecisoes(unittest.TestCase):
    def setUp(self):
        self.cenarios = criar_cenarios()

    def test_hierarquia_busca_e_consumo(self):
        colonia = criar_colonia()
        self.assertEqual(calcular_consumo(colonia), 70)
        self.assertEqual(buscar_sistema(colonia, "enfermaria")["prioridade"], 1)
        self.assertIsNone(buscar_sistema(colonia, "sistema inexistente"))

    def test_selection_sort_desliga_menos_importante_primeiro(self):
        ordem = [s["nome"] for s in ordenar_desligamento(criar_colonia())]
        self.assertEqual(ordem, ["Iluminacao externa", "Conforto", "Laboratorio"])

    def test_cenario_estavel_guarda_excedente(self):
        r = avaliar_colonia(self.cenarios["1 - Operacao estavel"])
        self.assertEqual(r["consumo_inicial_kwh"], 70)
        self.assertAlmostEqual(r["reserva_apos_hora_kwh"], 95)
        self.assertEqual(r["desligados"], [])
        self.assertTrue(any("Armazenar" in a["mensagem"] for a in r["acoes"]))

    def test_queda_prevista_causa_corte_preventivo(self):
        r = avaliar_colonia(self.cenarios["2 - Queda de geracao"])
        self.assertAlmostEqual(r["reserva_prevista_sem_prevencao_kwh"], 46.4)
        self.assertEqual(r["desligados"], ["Iluminacao externa"])
        self.assertGreaterEqual(r["reserva_proxima_hora_kwh"], 50)

    def test_emergencia_nao_desliga_essenciais(self):
        dados = self.cenarios["3 - Emergencia energetica"]
        r = avaliar_colonia(dados)
        self.assertEqual(r["consumo_apos_cortes_kwh"], 40)
        self.assertEqual(len(r["desligados"]), 3)
        self.assertTrue(any(a["nivel"] == "CRITICO" for a in r["acoes"]))
        self.assertTrue(all(s["ligado"] for s in dados["consumidores"]["essenciais"]))

    def test_falta_mesmo_apos_cortes_gera_alerta_manual(self):
        r = avaliar_colonia(self.cenarios["4 - Risco ao suporte a vida"])
        self.assertTrue(any("Mesmo apos os cortes" in a["mensagem"] for a in r["acoes"]))

    def test_tempestade_e_frio_sao_riscos_independentes(self):
        r = avaliar_colonia(self.cenarios["5 - Tempestade e frio extremo"])
        mensagens = " | ".join(a["mensagem"] for a in r["acoes"])
        self.assertIn("Tempestade", mensagens)
        self.assertIn("Frio extremo", mensagens)

    def test_bateria_cheia_perde_excedente(self):
        r = avaliar_colonia(self.cenarios["6 - Excesso de geracao"])
        self.assertAlmostEqual(r["reserva_apos_hora_kwh"], 200)
        self.assertAlmostEqual(r["energia_sem_armazenamento_kwh"], 38)

    def test_regra_booleana_de_risco_combinado(self):
        r = avaliar_colonia(self.cenarios["2 - Queda de geracao"])
        self.assertTrue(any("Geracao insuficiente e reserva prevista baixa" in a["mensagem"]
                            for a in r["acoes"]))

    def test_vento_extremo_para_turbina(self):
        dados = criar_colonia()
        dados["energia"]["fontes"]["eolica"]["vento_previsto_ms"] = 25
        r = avaliar_colonia(dados)
        self.assertEqual(r["geracao_eolica_prevista_kwh"], 0)
        self.assertTrue(any("turbina parada" in a["mensagem"] for a in r["acoes"]))

    def test_nao_modifica_cenario_original(self):
        dados = self.cenarios["2 - Queda de geracao"]
        avaliar_colonia(dados)
        self.assertTrue(all(s["ligado"] for s in dados["consumidores"]["nao_essenciais"]))

    def test_rejeita_reserva_maior_que_capacidade(self):
        dados = criar_colonia()
        dados["energia"]["reserva_kwh"] = 999
        with self.assertRaises(ValueError):
            avaliar_colonia(dados)

    def test_previsao_fora_do_historico_gera_aviso(self):
        dados = criar_colonia()
        dados["energia"]["fontes"]["eolica"]["vento_previsto_ms"] = 20
        r = avaliar_colonia(dados)
        self.assertTrue(any("extrapolacao" in a["mensagem"] for a in r["acoes"]))


if __name__ == "__main__":
    unittest.main()
