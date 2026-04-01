import cloudscraper
import json
import os
import time
from datetime import datetime

class SALottoScraper:
    def __init__(self):
        # Proteção contra Cloudflare e identificação de Browser Real
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.base_url = "https://www.nationallottery.co.za/index.php?option=com_weaver&controller=lotto-history"
        self.data_dir = "data"
        
        # Garante que a pasta existe para o Git
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_data(self, game_name):
        """Faz o POST simulando o AJAX do site oficial"""
        payload = {
            'gameName': game_name,
            'drawNumber': '', # Pega todo o histórico disponível
            'isAjax': 'true'
        }
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://www.nationallottery.co.za/results/{game_name.lower().replace(" ", "-")}'
        }

        try:
            print(f"[*] Varrendo: {game_name}...")
            response = self.scraper.post(self.base_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.json()
                if content.get('status') == 'success':
                    return content['data']['drawDetails']
            else:
                print(f"[!] Erro HTTP {response.status_code} em {game_name}")
        except Exception as e:
            print(f"[!] Erro ao processar {game_name}: {str(e)}")
        return None

    def save_data(self, name, data):
        """Salva o JSON formatado para consumo do App Flutter"""
        filename = f"{self.data_dir}/{name.lower().replace(' ', '_')}.json"
        
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": name,
            "results": data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(f"[OK] {filename} atualizado.")

    def run(self):
        # Lista filtrada apenas com as de números (Removido Sportstake)
        loterias = ["LOTTO", "POWERBALL", "DAILY LOTTO"]
        
        for lotto in loterias:
            result = self.fetch_data(lotto)
            if result:
                self.save_data(lotto, result)
            time.sleep(5) # Delay de segurança para não ser bloqueado

if __name__ == "__main__":
    bot = SALottoScraper()
    bot.run()
