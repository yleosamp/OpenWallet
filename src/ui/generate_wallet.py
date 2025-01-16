from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.crypto_manager import CryptoManager
from src.utils.network import check_internet

class GenerateWalletDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.crypto_manager = CryptoManager()
        self.setWindowTitle("Gerar Nova Wallet")
        self.setMinimumWidth(600)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Opções de seed
        seed_group = QGroupBox("Tipo de Seed")
        seed_layout = QHBoxLayout()
        self.rb_12_words = QRadioButton("12 palavras")
        self.rb_24_words = QRadioButton("24 palavras")
        self.rb_12_words.setChecked(True)
        seed_layout.addWidget(self.rb_12_words)
        seed_layout.addWidget(self.rb_24_words)
        seed_group.setLayout(seed_layout)
        layout.addWidget(seed_group)
        
        # Área da seed
        self.seed_text = QTextEdit()
        self.seed_text.setReadOnly(True)
        self.seed_text.setPlaceholderText("Suas palavras seed aparecerão aqui")
        layout.addWidget(self.seed_text)
        
        # Senha
        password_group = QGroupBox("Defina uma senha forte")
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
        
        # Botões
        btn_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Gerar Seed")
        self.btn_continue = QPushButton("Continuar")
        self.btn_continue.setEnabled(False)
        
        self.btn_generate.clicked.connect(self._generate_seed)
        self.btn_continue.clicked.connect(self._setup_wallet)
        
        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(self.btn_continue)
        layout.addLayout(btn_layout)
        
    def _generate_seed(self):
        if check_internet():
            QMessageBox.warning(self, "Aviso", "Por favor, desconecte da internet antes de gerar as seeds!")
            return
            
        strength = 256 if self.rb_24_words.isChecked() else 128
        try:
            mnemonic = self.crypto_manager.generate_seed(strength)
            self.seed_text.setText(mnemonic)
            self.btn_continue.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
            
    def _setup_wallet(self):
        password = self.password_input.text()
        confirm = self.password_confirm.text()
        
        if not password or password != confirm:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem!")
            return
            
        if len(password) < 8:
            QMessageBox.warning(self, "Erro", "A senha deve ter pelo menos 8 caracteres!")
            return
            
        try:
            self.crypto_manager.setup_wallet(password)
            QMessageBox.information(self, "Sucesso", 
                "Wallet criada com sucesso!\n\n"
                "Você pode conectar à internet e fazer login na sua wallet.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e)) 