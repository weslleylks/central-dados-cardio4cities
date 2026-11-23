from collections.abc import Sequence

import pandas as pd
from redcap import Project, RedcapError

from portal_dados.config import obter_credenciais


class REDCapAPIError(RuntimeError):
    """Erro de acesso ou exportação de dados REDCap."""


class REDCapClient:

    def __init__(self, url: str, token: str):

        if not url.startswith("https://"):
            raise ValueError("A URL da API deve usar HTTPS")

        self._projeto = Project(url, token)

    @classmethod
    def from_env(cls):
        """Cria a conexão utilizando o arquivo .env."""

        url, token = obter_credenciais()

        return cls(url, token)

    def exportar_registros(
        self,
        campos: Sequence[str] | None = None,
        registros: Sequence[str] | None = None,
        eventos: Sequence[str] | None = None
    ) -> pd.DataFrame:

        try:
            dados = self._projeto.export_records(
                format_type="json",
                fields=list(campos) if campos is not None else None,
                records=list(registros) if registros is not None else None,
                events=list(eventos) if eventos is not None else None,
                raw_or_label="raw",
                raw_or_label_headers="raw",
                event_name="unique",
                record_type="flat",
                export_survey_fields=False,
                export_data_access_groups=True,
                export_checkbox_labels=False
            )

        except RedcapError:
            raise REDCapAPIError(
                "Falha ao exportar registros. "
                "Verifique o token, permissões e campos."
            ) from None

        if not isinstance(dados, list):
            raise REDCapAPIError(
                "Resposta inesperada da API."
            )

        return pd.DataFrame(dados, dtype="string")

    def exportar_metadados(self) -> pd.DataFrame:

        try:
            metadados = self._projeto.export_metadata(
                format_type="json"
            )

        except RedcapError:
            raise REDCapAPIError(
                "Falha ao exportar o dicionário."
            ) from None

        if not isinstance(metadados, list):
            raise REDCapAPIError(
                "Resposta inesperada da API."
            )

        return pd.DataFrame(
            metadados,
            dtype="string"
        )