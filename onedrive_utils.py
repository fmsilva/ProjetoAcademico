# onedrive_utils.py (Exemplo - Adapte conforme a API do OneDrive)
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração (coloque as suas chaves em variáveis de ambiente .env)
CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID")
CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/onedrive_callback" # Exemplo
ONEDRIVE_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
ONEDRIVE_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

def get_onedrive_auth_url():
     #Gera URL de autorização do OneDrive
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "files.readwrite.all offline_access",  # Defina os escopos necessários
        "response_mode": "query",
    }
    auth_url = f"{ONEDRIVE_AUTH_URL}?{requests.compat.urlencode(params)}"
    return auth_url

def get_onedrive_token(auth_code):
     #Troca o código de autorização por um token de acesso
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(ONEDRIVE_TOKEN_URL, data=data)
    response.raise_for_status()  # Lança exceção se houver erro
    return response.json()

def refresh_onedrive_token(refresh_token):
    #Atualiza o token de acesso usando o token de atualização
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "redirect_uri": REDIRECT_URI, #Mesmo que o redirect_uri original
    }
    response = requests.post(ONEDRIVE_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()

def upload_file_to_onedrive(access_token, local_file_path, onedrive_folder_path):
    #Faz upload de um ficheiro para o OneDrive

    # 1. Obter o ID da pasta (ou criar a pasta se não existir)
    folder_id = get_or_create_onedrive_folder(access_token, onedrive_folder_path)


    # 2.  Upload do Ficheiro
    filename = os.path.basename(local_file_path)
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}:/{filename}:/content"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream", # ou o tipo MIME correto
    }

    with open(local_file_path, "rb") as f:
        response = requests.put(upload_url, headers=headers, data=f)

    response.raise_for_status() #Verifica se houve erros
    return response.json() # Retorna a resposta da API (metadados do ficheiro)



def get_or_create_onedrive_folder(access_token, folder_path):
    #Obtém o ID de uma pasta no OneDrive ou cria-a se não existir.

    # 1.  Verificar se a pasta já existe
    folder_path_encoded = requests.compat.quote(folder_path) #Codifica URL
    check_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path_encoded}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(check_url, headers=headers)

    if response.status_code == 200: #Pasta existe
        return response.json()["id"]
    elif response.status_code == 404:  # Pasta não existe, vamos criar
        parent_folder, folder_name = os.path.split(folder_path)

        # Se houver uma pasta pai, precisamos obter o ID dela recursivamente
        if parent_folder:
            parent_id = get_or_create_onedrive_folder(access_token, parent_folder)
            create_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{parent_id}/children"
        else: #Estamos na raiz
            create_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        
        headers["Content-Type"] = "application/json"
        data = {
            "name": folder_name,
            "folder": {},  # Indica que é uma pasta
            "@microsoft.graph.conflictBehavior": "rename", # Renomeia se já existir
        }
        response = requests.post(create_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["id"]  # Retorna o ID da pasta criada
    else:
        response.raise_for_status()  # Lança exceção para outros códigos de status
        return None
    