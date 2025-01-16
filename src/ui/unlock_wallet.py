from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from src.crypto_manager import CryptoManager
from src.wallet_manager import WalletManager

class UnlockWalletDialog(QDialog):
    def __init__(self, wallet_name: str, parent=None):
        super().__init__(parent)
        self.wallet_name = wallet_name
        self.crypto_manager = None
        self.wallet_manager = WalletManager()
        self.setWindowTitle("Desbloquear Wallet")
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"Digite a senha para desbloquear a wallet: {self.wallet_name}"))
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        btn_unlock = QPushButton("Desbloquear")
        btn_unlock.clicked.connect(self._unlock)
        layout.addWidget(btn_unlock)
        
    def _unlock(self):
        try:
            password = self.password_input.text()
            if not password:
                QMessageBox.warning(self, "Erro", "Digite a senha!")
                return
                
            self.crypto_manager = CryptoManager()
            wallet_data = self.wallet_manager.get_wallets().get(self.wallet_name, {})
            btc_address = wallet_data.get('btc_address')
            if not btc_address:
                raise Exception("Dados da wallet não encontrados")
            
            wallet_name = f"btc_wallet_{btc_address[:8]}"
            self.crypto_manager.load_existing_wallet(wallet_name, password)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Senha incorreta ou erro ao carregar wallet: {str(e)}")