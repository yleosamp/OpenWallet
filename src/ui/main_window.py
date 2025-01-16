from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from src.ui.generate_wallet import GenerateWalletDialog
from src.ui.import_wallet import ImportWalletDialog
from src.ui.dashboard import DashboardWindow
from src.ui.unlock_wallet import UnlockWalletDialog
import os
from src.wallet_manager import WalletManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.wallet_manager = WalletManager()
        self.setWindowTitle("Crypto Wallet Segura")
        self.setMinimumSize(800, 600)
        
        # Carregar estilo
        with open('assets/style.qss', 'r') as f:
            self.setStyleSheet(f.read())
            
        self._setup_ui()
        
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Lista de wallets
        wallets_group = QGroupBox("Suas Wallets")
        wallets_layout = QVBoxLayout()
        
        # Carrega wallets salvas
        for name, data in self.wallet_manager.get_wallets().items():
            wallet_widget = QWidget()
            wallet_layout = QHBoxLayout(wallet_widget)
            
            wallet_btn = QPushButton(f"Wallet: {name}")
            wallet_btn.clicked.connect(lambda checked, n=name: self._unlock_wallet(n))
            
            remove_btn = QPushButton("Remover")
            remove_btn.clicked.connect(lambda checked, n=name: self._remove_wallet(n))
            
            wallet_layout.addWidget(wallet_btn)
            wallet_layout.addWidget(remove_btn)
            wallets_layout.addWidget(wallet_widget)
            
        wallets_group.setLayout(wallets_layout)
        layout.addWidget(wallets_group)
        
        # Botões de ação
        btn_new_wallet = QPushButton("Criar Nova Wallet")
        btn_import_wallet = QPushButton("Importar Wallet")
        
        btn_new_wallet.clicked.connect(self._show_generate_dialog)
        btn_import_wallet.clicked.connect(self._show_import_dialog)
        
        layout.addWidget(btn_new_wallet)
        layout.addWidget(btn_import_wallet)
        
    def _show_generate_dialog(self):
        self.dialog = GenerateWalletDialog(self)
        if self.dialog.exec_():
            self._show_dashboard(self.dialog.crypto_manager)
            
    def _show_import_dialog(self):
        print("Abrindo diálogo de importação...")  # Debug
        self.dialog = ImportWalletDialog(self)
        result = self.dialog.exec_()
        print(f"Resultado do diálogo: {result}")  # Debug
        
        if result == QDialog.Accepted:
            print("Diálogo aceito, abrindo dashboard...")  # Debug
            self._show_dashboard(self.dialog.crypto_manager)
        else:
            print("Diálogo cancelado ou fechado")  # Debug
            
    def _show_dashboard(self, crypto_manager):
        try:
            print("Verificando estado para abrir dashboard...")  # Debug
            
            if not crypto_manager:
                raise Exception("Wallet não foi configurada corretamente")
                
            print("Criando janela do dashboard...")  # Debug
            self.dashboard = DashboardWindow(crypto_manager)
            print("Mostrando dashboard...")  # Debug
            self.dashboard.show()
            print("Escondendo janela principal...")  # Debug
            self.hide()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir dashboard: {str(e)}")
            print(f"Erro ao abrir dashboard: {str(e)}")  # Debug
            
    def _unlock_wallet(self, name):
        dialog = UnlockWalletDialog(name, self)
        if dialog.exec_():
            self._show_dashboard(dialog.crypto_manager)
            
    def _remove_wallet(self, name):
        reply = QMessageBox.question(
            self, 'Confirmar Remoção',
            f'Tem certeza que deseja remover a wallet {name}?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.wallet_manager.remove_wallet(name)
            self._setup_ui()  # Atualiza a interface