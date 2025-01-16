from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qrcode
from io import BytesIO
import PIL.ImageQt
from bitcoinlib.wallets import Wallet
from src.crypto_manager import CryptoManager
from src.utils.network import check_internet

class DashboardWindow(QMainWindow):
    def __init__(self, crypto_manager=None):
        super().__init__()
        print("Iniciando DashboardWindow...")  # Debug
        
        if crypto_manager is None:
            raise Exception("CryptoManager não fornecido!")
            
        self.crypto_manager = crypto_manager
        print(f"CryptoManager recebido com endereços - BTC: {self.crypto_manager.btc_address}, ETH: {self.crypto_manager.eth_address}")
        
        self.setWindowTitle("Crypto Wallet - Dashboard")
        self.setMinimumSize(1000, 700)
        
        print("Configurando interface do dashboard...")  # Debug
        self._setup_ui()
        print("Interface do dashboard configurada")  # Debug
        
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Painel esquerdo (carteiras)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Bitcoin Widget
        btc_group = QGroupBox("Bitcoin")
        btc_layout = QVBoxLayout()
        self.btc_address_label = QLabel()
        self.btc_balance_label = QLabel("Saldo: Carregando...")
        self.btc_qr = QLabel()
        
        btc_layout.addWidget(self.btc_address_label)
        btc_layout.addWidget(self.btc_balance_label)
        btc_layout.addWidget(self.btc_qr)
        btc_group.setLayout(btc_layout)
        
        # Ethereum Widget
        eth_group = QGroupBox("Ethereum")
        eth_layout = QVBoxLayout()
        self.eth_address_label = QLabel()
        self.eth_balance_label = QLabel("Saldo: Carregando...")
        self.eth_qr = QLabel()
        
        eth_layout.addWidget(self.eth_address_label)
        eth_layout.addWidget(self.eth_balance_label)
        eth_layout.addWidget(self.eth_qr)
        eth_group.setLayout(eth_layout)
        
        left_layout.addWidget(btc_group)
        left_layout.addWidget(eth_group)
        
        # Painel direito (transações)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Área de envio
        send_group = QGroupBox("Enviar Criptomoedas")
        send_layout = QFormLayout()
        
        self.coin_selector = QComboBox()
        self.coin_selector.addItems(["Bitcoin", "Ethereum"])
        
        self.address_input = QLineEdit()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setDecimals(8)
        self.amount_input.setMaximum(1000000)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self._send_transaction)
        
        send_layout.addRow("Moeda:", self.coin_selector)
        send_layout.addRow("Endereço:", self.address_input)
        send_layout.addRow("Quantidade:", self.amount_input)
        send_layout.addRow(self.send_button)
        
        send_group.setLayout(send_layout)
        right_layout.addWidget(send_group)
        
        # Histórico de transações
        history_group = QGroupBox("Histórico de Transações")
        history_layout = QVBoxLayout()
        self.transaction_list = QTableWidget()
        self.transaction_list.setColumnCount(4)
        self.transaction_list.setHorizontalHeaderLabels(["Data", "Tipo", "Quantidade", "Status"])
        
        history_layout.addWidget(self.transaction_list)
        history_group.setLayout(history_layout)
        right_layout.addWidget(history_group)
        
        # Adiciona os painéis ao layout principal
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Timer para atualizar saldos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_balances)
        self.update_timer.start(30000)  # Atualiza a cada 30 segundos
        
        # Carrega dados iniciais
        self._load_wallet_data()
        
    def _load_wallet_data(self):
        try:
            # Carregar endereços
            self.btc_address_label.setText(f"Endereço: {self.crypto_manager.btc_address}")
            self.eth_address_label.setText(f"Endereço: {self.crypto_manager.eth_address}")
            
            # Gerar QR codes
            self._generate_qr_code(self.crypto_manager.btc_address, self.btc_qr)
            self._generate_qr_code(self.crypto_manager.eth_address, self.eth_qr)
            
            # Atualizar saldos
            self._update_balances()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {str(e)}")
            
    def _generate_qr_code(self, data: str, label: QLabel):
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        qim = PIL.ImageQt.ImageQt(img)
        pixmap = QPixmap.fromImage(qim)
        label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
        
    def _update_balances(self):
        if not check_internet():
            self.status_bar.showMessage("Sem conexão com internet")
            return
            
        try:
            # Atualizar saldo BTC usando wallet existente
            wallet_name = f"btc_wallet_{self.crypto_manager.btc_address[:8]}"
            try:
                btc_wallet = Wallet(wallet_name)
            except WalletError:
                btc_wallet = Wallet.create(
                    wallet_name,
                    keys=self.crypto_manager.mnemonic,
                    network='bitcoin',
                    witness_type='segwit'
                )
                
            btc_balance = btc_wallet.balance()
            self.btc_balance_label.setText(f"Saldo: {btc_balance} BTC")
            
            self.status_bar.showMessage("Saldos atualizados")
        except Exception as e:
            self.status_bar.showMessage(f"Erro ao atualizar saldos: {str(e)}")
            print(f"Erro ao atualizar saldo: {str(e)}")  # Debug
            
    def _send_transaction(self):
        if not check_internet():
            QMessageBox.warning(self, "Erro", "Sem conexão com internet!")
            return
            
        try:
            coin = self.coin_selector.currentText()
            address = self.address_input.text()
            amount = self.amount_input.value()
            
            if coin == "Bitcoin":
                # Carrega a wallet com o nome correto
                wallet_name = f"btc_wallet_{self.crypto_manager.btc_address[:8]}"
                wallet = Wallet(wallet_name)
                
                # Verifica saldo
                balance = wallet.balance()
                if balance < amount:
                    QMessageBox.warning(self, "Erro", f"Saldo insuficiente! Disponível: {balance} BTC")
                    return
                    
                # Pede confirmação
                reply = QMessageBox.question(
                    self,
                    'Confirmar Transação',
                    f'Enviar {amount} BTC para {address}?\nTaxa estimada: 0.0001 BTC',
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        # Cria e envia a transação
                        tx = wallet.send_to(address, amount)
                        QMessageBox.information(self, "Sucesso", f"Transação enviada!\nID: {tx.hash}")
                        self._update_balances()
                    except Exception as e:
                        QMessageBox.critical(self, "Erro", f"Erro ao enviar: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na transação: {str(e)}") 

    def closeEvent(self, event):
        # Mostra a janela principal novamente
        self.parent().show()
        # Fecha o dashboard
        event.accept() 