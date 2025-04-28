import requests
import json

def obter_dados_sensores(api_key):
    url = 'https://api.purpleair.com/v1/sensors'
    headers = {
        'X-API-Key': api_key
    }
    # Tentando uma requisição com poucos parâmetros
    params = {
        'fields': 'name,latitude,longitude'  # Apenas campos básicos
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar a API: {response.status_code}, {response.text}")

def main():
    api_key = "44F53933-68D5-11EF-95CB-42010A80000E"
    
    try:
        dados_sensores = obter_dados_sensores(api_key)
        print("Dados dos sensores:")
        print(dados_sensores)
        
        with open('sensores_básicos.json', 'w') as f:
            json.dump(dados_sensores, f, indent=4)
        
        print("Dados dos sensores salvos em sensores_básicos.json")
    
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
