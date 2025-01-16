from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qrcode
from io import BytesIO
import PIL.ImageQt
from bitcoinlib.wallets import Wallet, WalletError
from src.crypto_manager import CryptoManager
from src.utils.network import check_internet

class DashboardWindow(QMainWindow):
    def __init__(self, crypto_manager=None):
        super().__init__()
        print("Iniciando DashboardWindow...")
        
        if crypto_manager is None:
            raise Exception("CryptoManager não fornecido!")
            
        self.crypto_manager = crypto_manager
        print(f"CryptoManager recebido com endereços - BTC: {self.crypto_manager.btc_address}, ETH: {self.crypto_manager.eth_address}")
        
        self.setWindowTitle("Crypto Wallet - Dashboard")
        self.setMinimumSize(1000, 700)
        
        # Configura a UI primeiro
        self._setup_ui()
        
        # Carrega os dados básicos
        self.btc_address_label.setText(f"Endereço: {self.crypto_manager.btc_address}")
        self.eth_address_label.setText(f"Endereço: {self.crypto_manager.eth_address}")
        
        # Gera QR codes
        self.generate_qr(self.crypto_manager.btc_address, self.btc_qr)
        self.generate_qr(self.crypto_manager.eth_address, self.eth_qr)
        
        # Atualiza saldos
        self._update_balances()
        
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
        self.btc_address_label = QLabel("Carregando...")
        self.btc_balance_label = QLabel("Saldo: Carregando...")
        self.btc_qr = QLabel()
        
        btc_layout.addWidget(self.btc_address_label)
        btc_layout.addWidget(self.btc_balance_label)
        btc_layout.addWidget(self.btc_qr)
        btc_group.setLayout(btc_layout)
        
        # Ethereum Widget
        eth_group = QGroupBox("Ethereum")
        eth_layout = QVBoxLayout()
        self.eth_address_label = QLabel("Carregando...")
        self.eth_balance_label = QLabel("Saldo: Carregando...")
        self.eth_qr = QLabel()
        
        eth_layout.addWidget(self.eth_address_label)
        eth_layout.addWidget(self.eth_balance_label)
        eth_layout.addWidget(self.eth_qr)
        eth_group.setLayout(eth_layout)
        
        left_layout.addWidget(btc_group)
        left_layout.addWidget(eth_group)
        
        # Painel direito simplificado
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Área de envio
        send_group = QGroupBox("Enviar")
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
        
        # Adiciona os painéis ao layout principal
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def _update_balances(self):
        if not check_internet():
            self.status_bar.showMessage("Sem conexão com internet")
            return
            
        try:
            # Usa a API blockchain.info para consultar o saldo
            btc_address = self.crypto_manager.btc_address
            print(f"Consultando saldo do endereço: {btc_address}")  # Debug
            
            url = f"https://blockchain.info/balance?active={btc_address}"
            import requests
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if btc_address in data:
                    balance_satoshis = data[btc_address]['final_balance']
                    btc_balance = float(balance_satoshis) / 100000000.0
                    
                    print(f"Resposta da API: {data}")  # Debug
                    print(f"Saldo em satoshis: {balance_satoshis}")
                    print(f"Saldo em BTC: {btc_balance}")
                    
                    self.btc_balance_label.setText(f"Saldo: {btc_balance:.8f} BTC")
                    self.status_bar.showMessage("Saldos atualizados")
                else:
                    raise Exception("Endereço não encontrado na resposta")
                    
            else:
                raise Exception(f"Erro na API: {response.status_code}")
                
        except Exception as e:
            print(f"Erro ao atualizar saldo: {str(e)}")
            self.status_bar.showMessage(f"Erro ao atualizar saldos: {str(e)}")
            
    def _send_transaction(self):
        if not check_internet():
            QMessageBox.warning(self, "Erro", "Sem conexão com internet!")
            return
            
        try:
            coin = self.coin_selector.currentText()
            address = self.address_input.text()
            amount = self.amount_input.value()
            
            if coin == "Bitcoin":
                # Verifica se o endereço é válido
                if not self.crypto_manager.validate_btc_address(address):
                    QMessageBox.warning(self, "Erro", "Endereço Bitcoin inválido!")
                    return
                    
                # Carrega a wallet
                wallet_name = f"btc_wallet_{self.crypto_manager.btc_address[:8]}"
                wallet = Wallet(wallet_name)
                
                # Configura a rede (mainnet)
                wallet.network = 'bitcoin'
                
                # Calcula taxa estimada (em satoshis/byte)
                fee_rate = 5  # Você pode ajustar isso ou usar uma API para taxa dinâmica
                estimated_size = 225  # Tamanho médio de uma transação P2WPKH
                fee = (fee_rate * estimated_size) / 100000000  # Converte para BTC
                
                total_amount = amount + fee
                
                # Verifica saldo
                if wallet.balance() < total_amount:
                    QMessageBox.warning(self, "Erro", f"Saldo insuficiente! (incluindo taxa de {fee:.8f} BTC)")
                    return
                    
                reply = QMessageBox.question(
                    self,
                    'Confirmar Transação',
                    f'Enviar {amount:.8f} BTC para {address}\n'
                    f'Taxa de mineração: {fee:.8f} BTC\n'
                    f'Total: {total_amount:.8f} BTC',
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    QMessageBox.information(self, "Aviso", 
                        "No momento, envio de transações está desativado por segurança.\n"
                        "Esta é uma versão educacional do software.")
                    return
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na transação: {str(e)}") 

    def closeEvent(self, event):
        # Mostra a janela principal novamente
        self.parent().show()
        # Fecha o dashboard
        event.accept() 

    def generate_qr(self, data: str, label: QLabel):
        """Gera QR code para o endereço"""
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        qim = PIL.ImageQt.ImageQt(img)
        pixmap = QPixmap.fromImage(qim)
        label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio)) 