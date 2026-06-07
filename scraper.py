import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def scrape_lotto_max():
    # URL de um agregador estável de resultados canadenses
    url = "https://www.lottonumbers.com/lotto-max-results"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    # O site costuma usar uma tabela para os resultados
    table = soup.find('table', class_='lotteryTable')
    if not table:
        return results

    rows = table.find('tbody').find_all('tr')
    
    # Pega os 10 resultados mais recentes
    for row in rows[:10]: 
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
            
        date_text = cols[0].text.strip()
        
        # Extrair as bolas normais (ignorando o bônus)
        balls = cols[1].find_all('li', class_='ball')
        numbers = [int(ball.text.strip()) for ball in balls if 'bonus-ball' not in ball.get('class', [])]
        
        # Extrair a bola bônus
        bonus_ball = cols[1].find('li', class_='bonus-ball')
        bonus = int(bonus_ball.text.strip()) if bonus_ball else None
        
        results.append({
            "draw_date": date_text,
            "numbers": numbers,
            "bonus": bonus
        })
        
    return results

if __name__ == "__main__":
    print("Iniciando extração...")
    
    # Você pode adicionar outras loterias (6/49, Daily Grand) aqui
    data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "lotto_max": scrape_lotto_max()
    }
    
    # Criar pasta data se não existir
    os.makedirs('data', exist_ok=True)
    
    # Salvar o arquivo
    file_path = 'data/resultados.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Scraping concluído! Salvo em {file_path}")
