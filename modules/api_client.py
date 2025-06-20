# modules/api_client.py
import requests
import config

def check_customer_by_plate(plate):
    """Verifica se a placa pertence a um cliente cadastrado."""
    url = f"{config.API_BASE_URL}/customers/by-plate/{plate}"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_active_service(plate):
    """Busca por um serviço ativo para a placa. Retorna os dados do serviço ou None."""
    # Reutilizamos a rota de cálculo de taxa, pois ela retorna o registro ativo.
    url = f"{config.API_BASE_URL}/services/calculate-fee/{plate}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None # Retorna None se não houver serviço ativo (404) ou outros erros.
    except requests.exceptions.RequestException:
        return None

def record_entry(plate):
    """Registra uma nova entrada de veículo na API."""
    url = f"{config.API_BASE_URL}/services/entry"
    try:
        response = requests.post(url, json={"license_plate": plate}, timeout=5)
        return response.status_code == 201
    except requests.exceptions.RequestException:
        return False

def finalize_exit(plate):
    """Informa a API que o veículo saiu e que o serviço deve ser finalizado no banco."""
    url = f"{config.API_BASE_URL}/services/exit/{plate}"
    try:
        # Usamos o método PUT para esta operação
        response = requests.put(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"API: Erro de conexão ao finalizar saída - {e}")
        return False