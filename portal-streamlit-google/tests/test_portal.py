"""Validação das regras de filtro e de autorização com unittest padrão."""

import unittest
from datetime import date

from portal_dados.dados import (
    CENTROS,
    GRUPOS,
    STATUS,
    VISITAS,
    filtrar_dados,
    gerar_dados_ficticios,
    resumo_por_centro,
)
from portal_dados.seguranca import sessao_expirada, usuario_autorizado


class TestPortal(unittest.TestCase):
    def setUp(self):
        self.dados = gerar_dados_ficticios(180)

    def test_dados_demonstrativos_reprodutiveis(self):
        outra_base = gerar_dados_ficticios(180)
        self.assertTrue(self.dados.equals(outra_base))
        self.assertEqual(self.dados["Registro"].nunique(), 180)

    def test_filtro_multiplos_campos(self):
        resultado = filtrar_dados(
            self.dados,
            centros=[CENTROS[0]],
            grupos=GRUPOS,
            visitas=["V1"],
            status=STATUS,
            data_inicio=date(2025, 1, 1),
            data_fim=date(2027, 1, 1),
        )
        self.assertTrue((resultado["Centro"] == CENTROS[0]).all())
        self.assertTrue((resultado["Visita"] == "V1").all())

    def test_lista_vazia_nao_retorna_tudo(self):
        resultado = filtrar_dados(
            self.dados, [], GRUPOS, VISITAS, STATUS, date(2025, 1, 1), date(2027, 1, 1)
        )
        self.assertTrue(resultado.empty)

    def test_taxa_realizacao_entre_zero_e_cem(self):
        resumo = resumo_por_centro(self.dados)
        self.assertEqual(resumo["Registros"].sum(), len(self.dados))
        self.assertTrue(resumo["Taxa de realização (%)"].between(0, 100).all())

    def test_email_autorizado_precisa_ser_verificado(self):
        permitidos = ["Pessoa@exemplo.com"]
        self.assertTrue(
            usuario_autorizado({"email": "pessoa@EXEMPLO.com", "email_verified": True}, permitidos)
        )
        self.assertFalse(
            usuario_autorizado({"email": "pessoa@exemplo.com", "email_verified": False}, permitidos)
        )
        self.assertFalse(
            usuario_autorizado({"email": "outra@exemplo.com", "email_verified": True}, permitidos)
        )
        self.assertFalse(usuario_autorizado({"email_verified": True}, permitidos))

    def test_sessao_sem_expiracao_e_rejeitada(self):
        self.assertTrue(sessao_expirada({}))
        self.assertTrue(sessao_expirada({"exp": 100}, agora=100))
        self.assertFalse(sessao_expirada({"exp": 101}, agora=100))


if __name__ == "__main__":
    unittest.main()

