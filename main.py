from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

app = FastAPI()

# Libera o CORS para qualquer origem (ajuste se necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou substitua por ["https://seudominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Escopo para leitura da planilha
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Lê as credenciais do ambiente
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

# Informações da planilha
SHEET_ID = "1Y435No_51cn5_3gFiDxB0ESu5G1DGgM17yZGi7xBpq8"
RANGE_NAME = "Página1"

@app.get("/cursistas")
def get_cursistas():
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    # Lê todos os dados da planilha (tabela de cursistas)
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    # Lê o valor da célula AB1
    ab1_result = sheet.values().get(spreadsheetId=SHEET_ID, range="AB1").execute()
    data_atualizacao = ab1_result.get("values", [[None]])[0][0]

    if not values:
        return {"data": [], "dataAtualizacao": data_atualizacao or "Data não disponível"}

    headers = values[0]
    dados = [dict(zip(headers, row)) for row in values[1:]]

    return {
        "data": dados,
        "dataAtualizacao": data_atualizacao or "Data não disponível"
    }
