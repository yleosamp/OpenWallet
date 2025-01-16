import os
import shutil
from pathlib import Path

def clean_wallet_data():
    """Limpa todos os dados de wallet salvos"""
    try:
        # Limpa dados do bitcoinlib
        btc_path = Path.home() / '.bitcoinlib'
        if btc_path.exists():
            shutil.rmtree(btc_path)
            
        # Limpa arquivos locais da wallet (se existirem)
        local_files = ['wallet_data', 'wallet_salt']
        for file in local_files:
            if os.path.exists(file):
                os.remove(file)
                
        return True, "Dados limpos com sucesso!"
    except Exception as e:
        return False, f"Erro ao limpar dados: {str(e)}" 