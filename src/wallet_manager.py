from pathlib import Path
import json
import os
from datetime import datetime

class WalletManager:
    def __init__(self):
        self.wallets_file = Path.home() / '.crypto_wallet' / 'wallets.json'
        self._ensure_dir_exists()
        
    def _ensure_dir_exists(self):
        self.wallets_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.wallets_file.exists():
            self.save_wallets({})
            
    def get_wallets(self) -> dict:
        try:
            if not self.wallets_file.exists():
                return {}
            
            with open(self.wallets_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar wallets: {str(e)}")  # Debug
            return {}
            
    def save_wallets(self, wallets: dict):
        with open(self.wallets_file, 'w') as f:
            json.dump(wallets, f, indent=4)
            
    def add_wallet(self, name: str, btc_address: str, eth_address: str):
        wallets = self.get_wallets()
        wallets[name] = {
            'btc_address': btc_address,
            'eth_address': eth_address,
            'date_added': str(datetime.now())
        }
        self.save_wallets(wallets)
        
    def remove_wallet(self, name: str):
        wallets = self.get_wallets()
        if name in wallets:
            del wallets[name]
            self.save_wallets(wallets) 