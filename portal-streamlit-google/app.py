"""Portal de consulta com autenticação Google OIDC (sem modo de bypass)."""

from __future__ import annotations

from datetime import date
import pandas as pd

import plotly.express as px
import streamlit as st

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

from portal_dados.client import REDCapClient

# Criar conexão
client = REDCapClient.from_env()

st.set_page_config(
    page_title="Portal de Indicadores | Demonstração",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1320px; padding-top: 2rem;}
    [data-testid="stMetric"] {background: #f3f7fb; padding: 20px; border-radius: 14px; border: 1px solid #e3eaf3;}
    [data-testid="stMetricLabel"] {color: #52647c;}
    [data-testid="stMetricValue"] {color: #132b4a;}
    .portal-hero {background: linear-gradient(105deg, #12284b, #176f83); color: white; padding: 28px 34px; border-radius: 18px; margin-bottom: 24px;}
    .portal-hero h1 {margin: 0; color: white; font-size: 2.1rem;}
    .portal-hero p {margin: 10px 0 0; opacity: .88; font-size: 1.02rem;}
    .portal-kicker {font-size: .72rem; letter-spacing: .13em; font-weight: 700; opacity: .8; margin-bottom: 8px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def cabecalho() -> None:
    st.markdown(
        """
        <section class="portal-hero">
          <div class="portal-kicker">PAINEL DE DADOS · DEMONSTRAÇÃO</div>
          <h1>Visão geral do monitoramento</h1>
          <p>Explore resultados, combine filtros e exporte os registros exibidos.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def autenticar() -> None:
    try:
        configuracao = st.secrets["auth"]
        emails = st.secrets["app"]["allowed_emails"]
        chaves = [
            "client_id",
            "client_secret",
            "cookie_secret",
            "redirect_uri",
            "server_metadata_url",
        ]
        if not all(configuracao.get(chave) for chave in chaves):
            raise ValueError("Configuração de autenticação incompleta")
        if not isinstance(emails, list) or not emails:
            raise ValueError("A lista de e-mails autorizados está vazia")
    except (KeyError, FileNotFoundError, ValueError, AttributeError):
        st.error("O login Google ainda não foi configurado pelo administrador.")
        st.info("Consulte o README.md e configure .streamlit/secrets.toml com OAuth e a lista de e-mails permitidos.")
        st.stop()

    if not st.user.is_logged_in:
        st.markdown("## Bem-vindo ao Portal de Indicadores")
        st.write("Entre com uma conta Google previamente autorizada para consultar o painel.")
        st.button("Entrar com Google", on_click=st.login, type="primary")
        st.caption("Seu login identifica você; nenhuma senha Google é armazenada nesta aplicação.")
        st.stop()

    if sessao_expirada(st.user):
        st.warning("Sua sessão expirou. Saia e faça login novamente.")
        st.button("Renovar login", on_click=st.logout)
        st.stop()

    if not usuario_autorizado(st.user, emails):
        st.error("Acesso negado: esta conta Google não está na lista de usuários autorizados.")
        st.button("Sair desta conta", on_click=st.logout)
        st.stop()


autenticar()

with st.sidebar:
    st.markdown("### 📊 Portal de Indicadores")
    st.success("Acesso autorizado")
    st.caption(str(st.user.get("email", "")))
    st.button("Sair", on_click=st.logout, width='stretch')
    st.divider()
    st.subheader("Filtros")

    @st.cache_data(show_spinner=False)
    def carregar_dados():
        # Exportar todos os registros
        return client.exportar_registros()

    base = carregar_dados()
    base["v_2"] = pd.to_datetime(base["v_2"], errors="coerce").dt.date
    nomes = st.multiselect("v_1", options=None, default=None)
    grupos = st.multiselect("v_3", options=GRUPOS, default=GRUPOS)
    visitas = st.multiselect("v_4", options=VISITAS, default=VISITAS)
    estados = st.multiselect("v_5", options=STATUS, default=STATUS)
    periodo = st.date_input(
        "v_2",
        value=(base["v_2"].min(), base["v_2"].max()),
        min_value=base["v_2"].min(),
        max_value=base["v_2"].max(),
        format="DD/MM/YYYY",
    )
    busca = st.text_input("Buscar código do registro", placeholder="Ex.: DEMO-00015")
    st.caption("Dados exclusivamente fictícios, gerados para demonstração.")

cabecalho()

if not isinstance(periodo, (list, tuple)) or len(periodo) != 2:
    st.info("Selecione uma data inicial e uma data final para visualizar os dados.")
    st.stop()

inicio, fim = periodo
if not isinstance(inicio, date) or not isinstance(fim, date):
    st.info("Selecione um período válido.")
    st.stop()

filtrado = filtrar_dados(
    base, 
    nomes, 
    grupos, 
    visitas, 
    estados, 
    inicio, 
    fim, 
    busca
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", f"{len(filtrado):,}".replace(",", "."))
col2.metric("Nomes", filtrado["v_1"].nunique())
# percentual = 100 * filtrado["Status"].eq("Realizado").mean() if len(filtrado) else 0
# col3.metric("Realizados", f"{percentual:.1f}%".replace(".", ","))
# pendencias = filtrado["Status"].isin(["Não realizado", "Verificar"]).sum()
# col4.metric("Requerem atenção", int(pendencias))

st.write("")
graficos_esquerda, graficos_direita = st.columns([1.3, 1], gap="large")

with graficos_esquerda:
    st.subheader("Status por visita")
    if filtrado.empty:
        st.info("Nenhum registro encontrado para os filtros selecionados.")
    else:
        contagens = filtrado.groupby(["Visita", "Status"]).size().reset_index(name="Registros")
        fig = px.bar(
            contagens,
            x="Visita",
            y="Registros",
            color="Status",
            barmode="stack",
            category_orders={"Visita": VISITAS, "Status": STATUS},
            color_discrete_map={
                "Realizado": "#128875",
                "Aguardando": "#e9a83b",
                "Não realizado": "#d65b5b",
                "Verificar": "#6c7db3",
            },
        )
        fig.update_layout(
            legend_title_text="",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=14, b=10),
            height=350,
        )
        st.plotly_chart(fig, width='stretch')

with graficos_direita:
    st.subheader("Registros por grupo")
    if not filtrado.empty:
        grupos_contagem = filtrado.groupby("Grupo").size().reset_index(name="Registros")
        fig_grupo = px.pie(
            grupos_contagem,
            names="Grupo",
            values="Registros",
            hole=0.64,
            color="Grupo",
            color_discrete_map={
                "Proven": "#176f83",
                "TeleProven": "#34a4a0",
                "Controle": "#a6d5d3",
            },
        )
        fig_grupo.update_traces(textinfo="percent", textposition="outside")
        fig_grupo.update_layout(
            showlegend=True,
            legend_title_text="",
            margin=dict(l=10, r=10, t=14, b=10),
            height=350,
        )
        st.plotly_chart(fig_grupo, width='stretch')

st.subheader("Explore os dados")
aba_registros, aba_resumo = st.tabs(["Tabela de registros", "Resumo por centro"])

with aba_registros:
    st.caption(f"{len(filtrado)} registro(s) após aplicação dos filtros")
    st.dataframe(
        filtrado.sort_values("v_2", ascending=False),
        hide_index=True,
        width='stretch',
        height=420,
        column_config={
            "v_2": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Completude (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%"),
        },
    )
    st.download_button(
        "⬇️ Exportar registros filtrados (.csv)",
        data=filtrado.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="registros_filtrados_demo.csv",
        mime="text/csv",
        disabled=filtrado.empty,
    )

with aba_resumo:
    resumo = resumo_por_centro(filtrado)
    st.dataframe(
        resumo,
        hide_index=True,
        width='stretch',
        column_config={
            "Taxa de realização (%)": st.column_config.ProgressColumn(
                min_value=0, max_value=100, format="%.1f%%"
            )
        },
    )
    st.download_button(
        "⬇️ Exportar resumo (.csv)",
        data=resumo.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="resumo_centros_demo.csv",
        mime="text/csv",
        disabled=resumo.empty,
    )

st.caption(
    "⚠️ Protótipo com dados fictícios. Para dados sensíveis reais, avalie LGPD, "
    "regras de acesso por linha e auditoria antes de publicar."
)

