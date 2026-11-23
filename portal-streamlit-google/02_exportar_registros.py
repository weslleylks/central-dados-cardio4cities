#%%
from portal_dados.client import REDCapClient

# Criar conexão
client = REDCapClient.from_env()

# Exportar todos os registros
df = client.exportar_registros()

# Exportar variáveis específicas
df_campos = client.exportar_registros()

# Exportar registros específicos
df_registros = client.exportar_registros(
    registros=["1628-124", "1628-167"]
)

# Exportar uma visita específica
df_visita = client.exportar_registros(
    eventos=["coleta_de_dados_1_arm_1"]
)

# Exportar dicionário
dicionario = client.exportar_metadados()

#%%
df