from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = FastAPI()

# Liberar acesso do frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou use seu domínio específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega credenciais
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Lê a chave do ambiente e converte para dict
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
    
)

# Dados da planilha
SHEET_ID = "1Y435No_51cn5_3gFiDxB0ESu5G1DGgM17yZGi7xBpq8"
RANGE_NAME = "Página1"

@app.get("/cursistas")
def get_cursistas():
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    
    if not values:
        return {"data": []}

    headers = values[0]
    dados = [dict(zip(headers, row)) for row in values[1:]]

    return {"data": dados}
