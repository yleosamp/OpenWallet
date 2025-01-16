from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet, BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from web3 import Web3
from bitcoinlib.wallets import Wallet, WalletError
import json
from typing import Tuple, Optional
from .security import SecurityManager
from .utils.network import check_internet
import os
from pathlib import Path
from .wallet_manager import WalletManager

class CryptoManager:
    def __init__(self):
        self.security = SecurityManager()
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/SEU_ID_INFURA'))
        self.mnemonic = None
        self.eth_address = None
        self.btc_address = None
        
    def wallet_exists(self) -> bool:
        try:
            Wallet('btc_wallet')
            return True
        except WalletError:
            return False
            
    def load_existing_wallet(self, wallet_name: str, password: str) -> None:
        try:
            # Primeiro carrega os dados criptografados
            self._load_wallet(password)
            
            if not self.mnemonic:
                raise Exception("Mnemônico não encontrado")
            
            # Tenta abrir a wallet existente, se não existir, cria uma nova
            try:
                btc_wallet = Wallet(wallet_name)
            except WalletError:
                btc_wallet = Wallet.create(
                    wallet_name,
                    keys=self.mnemonic,
                    network='bitcoin',
                    witness_type='segwit'
                )
            
            self.btc_address = btc_wallet.get_key().address
            
        except Exception as e:
            raise Exception(f"Erro ao carregar wallet: {str(e)}")
        
    def generate_seed(self, strength: int = 128) -> str:
        if check_internet():
            raise Exception("Desconecte a internet antes de gerar as seeds!")
            
        self.mnemonic = generate_mnemonic(language="english", strength=strength)
        
        # Gera os endereços imediatamente
        self._generate_addresses()
        
        # Adiciona a wallet ao gerenciador
        wallet_name = f"btc_wallet_{self.btc_address[:8]}"
        wallet_manager = WalletManager()
        wallet_manager.add_wallet(wallet_name, self.btc_address, self.eth_address)
        
        return self.mnemonic
        
    def setup_wallet(self, password: str, mnemonic: Optional[str] = None) -> None:
        try:
            print("Iniciando setup da wallet...")  # Debug
            if mnemonic:
                self.mnemonic = mnemonic
                print("Mnemônico definido com sucesso")  # Debug
            
            print("Gerando endereços...")  # Debug
            self._generate_addresses()
            print("Endereços gerados com sucesso")  # Debug
            
            print("Gerando chave de segurança...")  # Debug
            self.security.generate_key(password)
            print("Chave gerada com sucesso")  # Debug
            
            print("Salvando dados da wallet...")  # Debug
            self._save_wallet(password)
            
            # Adiciona a wallet ao gerenciador com o mesmo nome usado no bitcoinlib
            wallet_name = f"btc_wallet_{self.btc_address[:8]}"
            wallet_manager = WalletManager()
            wallet_manager.add_wallet(wallet_name, self.btc_address, self.eth_address)
            
            # Garante que a wallet BTC está criada e pronta
            btc_wallet = Wallet.create(
                wallet_name,
                keys=self.mnemonic,
                network='bitcoin',
                witness_type='segwit'
            )
            
            print("Wallet salva com sucesso")  # Debug
            
        except Exception as e:
            print(f"Erro no setup da wallet: {str(e)}")  # Debug
            raise Exception(f"Falha no setup da wallet: {str(e)}")
        
    def _generate_addresses(self) -> None:
        try:
            print("Gerando endereços...")  # Debug
            # Gerar endereço ETH
            eth_wallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
            eth_wallet.from_mnemonic(mnemonic=self.mnemonic)
            eth_wallet.clean_derivation()
            eth_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=EthereumMainnet, account=0, change=False, address=0
            )
            eth_wallet.from_path(path=eth_derivation)
            self.eth_address = eth_wallet.address()
            print(f"Endereço ETH gerado: {self.eth_address}")  # Debug
            
            # Gerar endereço BTC
            try:
                # Cria wallet temporária apenas para gerar endereço
                import time
                temp_name = f"temp_wallet_{int(time.time())}"
                btc_wallet = Wallet.create(
                    temp_name,
                    keys=self.mnemonic,
                    network='bitcoin',
                    witness_type='segwit'
                )
                
                # Obtém o endereço
                self.btc_address = btc_wallet.get_key().address
                print(f"Endereço BTC gerado: {self.btc_address}")  # Debug
                
            except Exception as btc_error:
                print(f"Erro específico na geração do endereço BTC: {str(btc_error)}")  # Debug
                raise Exception(f"Erro na geração do endereço BTC: {str(btc_error)}")
            
        except Exception as e:
            print(f"Erro ao gerar endereços: {str(e)}")  # Debug
            raise Exception(f"Erro ao gerar endereços: {str(e)}")
        
    def _save_wallet(self, password: str) -> None:
        wallet_data = {
            'mnemonic': self.mnemonic,
            'eth_address': self.eth_address,
            'btc_address': self.btc_address
        }
        self.security.encrypt_data(wallet_data) 

    def validate_btc_address(self, address: str) -> bool:
        try:
            # Validar formato do endereço BTC
            if not address.startswith(('1', '3', 'bc1')):
                return False
            
            # Adicionar mais validações conforme necessário
            return True
        except:
            return False

    def get_wallet_path(self) -> str:
        return os.path.join(str(Path.home()), '.bitcoinlib', 'database') 

    def _load_wallet(self, password: str) -> None:
        try:
            # Descriptografa os dados salvos
            wallet_data = self.security.decrypt_data(password)
            
            # Carrega os dados na instância
            self.mnemonic = wallet_data.get('mnemonic')
            self.eth_address = wallet_data.get('eth_address')
            self.btc_address = wallet_data.get('btc_address')
            
            if not all([self.mnemonic, self.eth_address, self.btc_address]):
                raise Exception("Dados da wallet incompletos")
            
        except Exception as e:
            raise Exception(f"Erro ao carregar dados da wallet: {str(e)}") 