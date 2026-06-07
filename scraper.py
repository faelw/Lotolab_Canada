import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def scrape_wclc_lotto_max():
    """
    Tenta extrair do site da Western Canada Lottery Corporation.
    Eles costumam ter menos proteções anti-bot do que agregadores globais.
    """
    url = "https://www.wclc.com/home.htm"
    
    # Headers mais completos para simular um navegador real e enganar proteções básicas
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O HTML do WCLC tem uma div específica para os números do Lotto Max
        # Vamos procurar pelo bloco que contém o Lotto Max
        lotto_max_block = soup.find(string=lambda text: text and "LOTTO MAX Winning Numbers" in text)
        
        if not lotto_max_block:
            print("Não foi possível encontrar a seção do Lotto Max na página.")
            return []

        # Pega a ul (lista) logo após o título do Lotto Max
        numbers_list = lotto_max_block.find_next('ul')
        list_items = numbers_list.find_all('li')
        
        numbers = []
        bonus = None
        
        for item in list_items:
            text = item.text.strip()
            # Verifica se é a bola bônus (Geralmente está escrita como "Bonus26" ou "Bonus 26")
            if 'Bonus' in text or 'bonus' in text.lower():
                bonus = int(''.join(filter(str.isdigit, text)))
            else:
                numbers.append(int(''.join(filter(str.isdigit, text))))
                
        # Como esse site mostra apenas o último sorteio na home, retornamos uma lista com 1 item
        return [{
            "draw_date": datetime.utcnow().strftime("%Y-%m-%d"), # Data do scraping
            "numbers": numbers,
            "bonus": bonus
        }]
        
    except Exception as e:
        print(f"Erro ao acessar WCLC: {e}")
        return []

if __name__ == "__main__":
    print("Iniciando extração do Lotto Max...")
    
    # Fazemos a extração
    lotto_max_results = scrape_wclc_lotto_max()
    
    # Montamos a estrutura do JSON
    data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "lotto_max": lotto_max_results
    }
    
    # Criar pasta data se não existir
    os.makedirs('data', exist_ok=True)
    
    # Salvar o arquivo apenas se houver resultados para evitar sobrescrever com arquivo vazio
    file_path = 'data/resultados.json'
    
    if lotto_max_results:
        # Verifica se o arquivo já existe para não perder histórico (opcional, mas recomendado)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    old_data = json.load(f)
                    # Verifica se o resultado já existe no histórico
                    if old_data.get("lotto_max") and lotto_max_results[0] not in old_data["lotto_max"]:
                        # Adiciona o novo resultado ao topo da lista histórica
                        old_data["lotto_max"].insert(0, lotto_max_results[0])
                        data["lotto_max"] = old_data["lotto_max"]
                    else:
                        data["lotto_max"] = old_data.get("lotto_max", lotto_max_results)
                except json.JSONDecodeError:
                    pass

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Scraping concluído com sucesso! Salvo em {file_path}")
    else:
        print("Scraping falhou. O arquivo JSON não foi atualizado.")
