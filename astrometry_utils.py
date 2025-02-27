import os
import time
import requests
from dotenv import load_dotenv

from ProjetoAcademico.app import ASTROMETRY_API_KEY

load_dotenv()



def submit_to_astrometry(file_path, api_key=ASTROMETRY_API_KEY):
    """Envia uma imagem para Astrometry.net para resolução."""

    with open(file_path, "rb") as file:
        files = {"file": file}
        data = {
            "allow_commercial_use": "n",
            "allow_modifications": "n",
            "publicly_visible": "n",
            "apikey": api_key,
        }

        try:
            response = requests.post(
                ASTROMETRY_URL + "upload", files=files, data=data
            )
            response.raise_for_status()  # Verifica erros HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar para Astrometry.net: {e}")
            return None


def get_job_status(job_id, api_key=ASTROMETRY_API_KEY):
    """Verifica o status de um job no Astrometry.net."""

    url = ASTROMETRY_URL + f"jobs/{job_id}?apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter status do job: {e}")
        return None


def get_job_results(job_id, api_key=ASTROMETRY_API_KEY):
    """Obtém os resultados de um job concluído no Astrometry.net."""

    url = ASTROMETRY_URL + f"jobs/{job_id}/info?apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter resultados do job: {e}")
        return None
    
def poll_for_results(job_id, max_attempts=20, wait_time=30):
    """
    Espera até que um job do astrometry.net seja concluído, verificando periodicamente.
    Retorna os resultados ou None se falhar.
    """
    for attempt in range(max_attempts):
        status_data = get_job_status(job_id)
        if status_data and status_data.get("status") == "success":
             return get_job_results(job_id)
        elif status_data and status_data.get("status") == "failure":
            print(f"Astrometry.net job {job_id} falhou.")
            return None # Ou tratar o erro
        print(f"Astrometry.net: À espera do job {job_id}... (tentativa {attempt+1}/{max_attempts})")
        time.sleep(wait_time)
    print(f"Astrometry.net: Job {job_id} excedeu o tempo limite.")
    return None


