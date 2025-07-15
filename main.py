from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

app = FastAPI()

# Libera CORS para qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Escopo para leitura da planilha
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Lê as credenciais do ambiente apenas uma vez
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

# ID da planilha e intervalo
SHEET_ID = "1Y435No_51cn5_3gFiDxB0ESu5G1DGgM17yZGi7xBpq8"
RANGE_NAME = "Página1"

# Cache de dados
dados_cache = []
data_cache = "Carregando..."

def carregar_dados():
    global dados_cache, data_cache

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    # Lê a planilha completa
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    # Lê a célula AB1 (data de atualização)
    ab1_result = sheet.values().get(spreadsheetId=SHEET_ID, range="AB1").execute()
    data_atualizacao = ab1_result.get("values", [[None]])[0][0]

    if values:
        headers = values[0]
        dados_cache = [dict(zip(headers, row)) for row in values[1:]]
        data_cache = data_atualizacao or "Data não disponível"
    else:
        dados_cache = []
        data_cache = "Sem dados"

# Carrega ao iniciar
carregar_dados()

@app.get("/cursistas")
def get_cursistas():
    return {
        "data": dados_cache,
        "dataAtualizacao": data_cache
    }
