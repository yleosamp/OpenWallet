from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.crypto_manager import CryptoManager

class ImportWalletDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.crypto_manager = CryptoManager()
        self.setWindowTitle("Importar Wallet")
        self.setMinimumWidth(600)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Área para seed
        seed_group = QGroupBox("Digite suas palavras seed")
        seed_layout = QVBoxLayout()
        self.seed_input = QTextEdit()
        self.seed_input.setPlaceholderText("Digite suas 12 ou 24 palavras seed, separadas por espaço")
        seed_layout.addWidget(self.seed_input)
        seed_group.setLayout(seed_layout)
        layout.addWidget(seed_group)
        
        # Senha
        password_group = QGroupBox("Defina uma senha")
        password_layout = QVBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(QLabel("Senha:"))
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(QLabel("Confirme a senha:"))
        password_layout.addWidget(self.password_confirm)
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # Botão importar
        self.btn_import = QPushButton("Importar Wallet")
        self.btn_import.clicked.connect(self._import_wallet)
        layout.addWidget(self.btn_import)
        
    def _import_wallet(self):
        try:
            mnemonic = self.seed_input.toPlainText().strip()
            if not mnemonic:
                QMessageBox.warning(self, "Erro", "Digite suas palavras seed!")
                return
                
            # Validar número de palavras
            words = mnemonic.split()
            if len(words) not in [12, 24]:
                QMessageBox.warning(self, "Erro", "A seed deve ter 12 ou 24 palavras!")
                return
                
            password = self.password_input.text()
            confirm = self.password_confirm.text()
            
            if not password or password != confirm:
                QMessageBox.warning(self, "Erro", "As senhas não coincidem!")
                return
                
            if len(password) < 8:
                QMessageBox.warning(self, "Erro", "A senha deve ter pelo menos 8 caracteres!")
                return
                
            try:
                self.crypto_manager.setup_wallet(password, mnemonic)
                QMessageBox.information(self, "Sucesso", "Wallet importada com sucesso!")
                self.accept()
            except Exception as setup_error:
                QMessageBox.critical(self, "Erro na Configuração", 
                    f"Erro ao configurar a wallet: {str(setup_error)}\n\n"
                    "Verifique se suas palavras seed estão corretas.")
                return
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", 
                f"Erro inesperado: {str(e)}\n\n"
                "Por favor, tente novamente ou contate o suporte.") 