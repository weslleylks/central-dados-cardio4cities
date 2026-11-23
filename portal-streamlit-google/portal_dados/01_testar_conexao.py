"""Verifica o acesso à API por meio da exportação do dicionário de dados."""

from client import REDCapClient


def main() -> None:
    cliente = REDCapClient.from_env()
    metadados = cliente.exportar_metadados()
    print(f"Consulta à API concluída: {len(metadados)} campos no dicionário.")


if __name__ == "__main__":
    main()
