#%%
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"

def obter_credenciais():
    url = os.getenv("REDCAP_API_URL")
    token = os.getenv("REDCAP_API_TOKEN_58671")

    if not url or not token:
        raise RuntimeError("Credenciais não configuradas")

    return url, token