"""Política explícita de quem pode acessar o protótipo."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from time import time


def usuario_autorizado(usuario: Mapping, emails_permitidos: Iterable[str]) -> bool:
    """Requer e-mail Google confirmado e presente na lista de autorização."""
    email = str(usuario.get("email", "")).strip().casefold()
    emails = {str(item).strip().casefold() for item in emails_permitidos}

    return bool(email and usuario.get("email_verified") is True and email in emails)


def sessao_expirada(usuario: Mapping, agora: float | None = None) -> bool:
    """Rejeita tokens sem prazo de expiração ou com expiração vencida."""
    exp = usuario.get("exp")
    if exp is None:
        return True
    try:
        return float(exp) <= (time() if agora is None else agora)
    except (ValueError, TypeError):
        return True

