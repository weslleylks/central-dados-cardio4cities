# Portal de Indicadores — Streamlit + Google Login

Protótipo de consulta a **dados 100% fictícios**, com autenticação Google OIDC,
lista fechada de e-mails autorizados, filtros combinados, gráficos e exportação CSV.

## Funcionalidades

- Login Google real via `st.login()` e logout com `st.logout()`.
- Lista de e-mails autorizados, validando `email_verified` e expiração da sessão.
- Filtros de centro, grupo, visita, status, intervalo de datas e código do registro.
- Indicadores, gráficos Plotly, tabela pesquisável/ordenável e downloads CSV.
- Sem API externa, banco de dados real ou informações pessoais nos dados de demonstração.

## Estrutura

```text
portal-streamlit-google/
├── app.py
├── portal_dados/
│   ├── __init__.py
│   ├── dados.py
│   └── seguranca.py
├── tests/test_portal.py
├── .streamlit/secrets.toml.example
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

## 1. Configurar login no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/) e crie/selecione um projeto.
2. Em **Google Auth Platform → Branding/Audience**, configure nome, suporte e público.
3. Enquanto o aplicativo estiver em **Testing**, inclua seu e-mail em **Test users**.
4. Em **Clients**, crie uma credencial OAuth do tipo **Web application**.
5. Adicione o redirecionamento autorizado exatamente como abaixo:

   ```text
   http://localhost:8501/oauth2callback
   ```

6. Guarde o **Client ID** e o **Client secret**. O login utiliza somente escopos
   de identificação (`openid profile email`), sem ler Google Drive ou Gmail.

## 2. Configurar segredos sem publicar credenciais

Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha:

- `auth.client_id`: ID do cliente OAuth.
- `auth.client_secret`: segredo do cliente OAuth.
- `auth.cookie_secret`: valor aleatório, por exemplo gerado por
  `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- `app.allowed_emails`: seus endereços autorizados, em lista TOML.
- `auth.redirect_uri`: a URL de callback do ambiente.

**Importante:** `.streamlit/secrets.toml` está em `.gitignore`. Nunca coloque
credenciais no repositório nem no README. Se não houver configuração ou lista
autorizada, o app bloqueia o acesso e exibe uma instrução de configuração.

## 3. Instalar e iniciar via uv

```bash
uv sync
uv run streamlit run app.py
```

Acesse `http://localhost:8501` e clique em **Entrar com Google**.

Para executar os testes:

```bash
uv run python -m unittest discover -s tests -v
```

## 4. Hospedar gratuitamente no Streamlit Community Cloud

1. Coloque estes arquivos em um repositório GitHub **sem** `secrets.toml`.
2. Acesse [Streamlit Community Cloud](https://share.streamlit.io) e crie a aplicação
   escolhendo `app.py` como arquivo inicial.
3. Após obter a URL, adicione no cliente OAuth do Google o callback exato:

   ```text
   https://SUA-APLICACAO.streamlit.app/oauth2callback
   ```

4. Nas configurações da aplicação, em **Secrets**, cole o conteúdo preenchido de
   `secrets.toml`, alterando `redirect_uri` para o endereço HTTPS publicado.
5. Teste com uma conta Google incluída tanto em **Test users** (enquanto o OAuth
   estiver em Testing) quanto em `allowed_emails`.
6. Para abrir a autenticação a mais usuários, ajuste a configuração **Audience**
   no Google Cloud e mantenha a lista de e-mails do sistema restrita.

> A versão gratuita pode ter cotas e suspensões de instância. A configuração OIDC
> representa uma aplicação autenticada, sujeita às regras atuais do serviço.

## 5. Substituir dados fictícios por dados reais

Os dados são criados por `portal_dados/dados.py`. Para utilizar PostgreSQL, REDCap
ou arquivos Parquet, substitua `gerar_dados_ficticios()` por uma função de leitura
**no servidor**, que entregue apenas as colunas autorizadas. Preserve as colunas
e a lógica de `filtrar_dados` ou atualize-as para sua tabela.

**Segurança:** autenticação Google + allowlist só controlam **quem entra**;
não há perfis distintos nem limitação de linhas por instituição neste protótipo.
Se usuários diferentes só puderem ver seus próprios centros, implemente essa
permissão no backend/banco (por exemplo, RLS em PostgreSQL) antes da consulta,
inclusive nos downloads. Não use apenas filtros visuais como controle de acesso.
Não conecte bases clínicas identificáveis sem avaliação de LGPD, controle de
acesso, logs adequados e proteção dos segredos do servidor.

## Referências técnicas

- [Tutorial oficial de autenticação Google com Streamlit](https://docs.streamlit.io/develop/tutorials/authentication/google)
- [Referência do `st.login`](https://docs.streamlit.io/develop/api-reference/user/st.login)
- [Google OpenID Connect](https://developers.google.com/identity/openid-connect/openid-connect)
