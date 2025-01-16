# Crypto Wallet Segura - Projeto de Estudos

⚠️ **AVISO IMPORTANTE** ⚠️

Este é um projeto puramente educacional desenvolvido para estudos de criptografia, blockchain e desenvolvimento de software. 

**NÃO É RECOMENDADO PARA USO REAL OU ARMAZENAMENTO DE CRIPTOMOEDAS.**

O autor não assume nenhuma responsabilidade por perdas financeiras, roubo de fundos ou quaisquer outros danos que possam ocorrer pelo uso deste software.

## Sobre o Projeto

Uma carteira (wallet) de criptomoedas desenvolvida em Python com foco em:

- Geração segura de chaves offline
- Suporte a Bitcoin e Ethereum
- Interface gráfica com PyQt5
- Criptografia de dados locais
- Gerenciamento de múltiplas wallets

## Medidas de Segurança

- Geração de seeds offline obrigatória
- Criptografia local dos dados sensíveis
- Senha forte obrigatória (mín. 8 caracteres)
- Armazenamento apenas local
- Sem envio de dados para servidores externos
- Validação de endereços

## Como Usar

1. Instalação:
```bash
pip install -r requirements.txt
```

2. Executar:
```bash
python main.py
```

3. Funcionalidades:
- Criar nova wallet (offline)
- Importar wallet existente
- Visualizar saldos
- Enviar transações
- Gerar QR codes
- Gerenciar múltiplas wallets

## Recursos Técnicos

- Python 3.8+
- PyQt5 para interface
- bitcoinlib para operações BTC
- web3.py para operações ETH
- cryptography para criptografia local
- qrcode para geração de QR codes

## Limitações Conhecidas

- Sem suporte a hardware wallets
- Sem backup automático
- Interface básica
- Sem suporte a tokens ERC-20
- Sem integração com DEXs

## Contribuições

Este é um projeto de estudos e contribuições são bem-vindas, mas lembre-se:
- Mantenha o foco educacional
- Documente alterações
- Siga boas práticas de segurança
- Teste exaustivamente

## Disclaimer Legal

Este software é fornecido "como está", sem garantias de qualquer tipo. O uso é por conta e risco do usuário.

O autor expressamente se isenta de qualquer responsabilidade por:
- Perdas financeiras
- Roubo de fundos
- Falhas de segurança
- Bugs no código
- Qualquer outro dano direto ou indireto

**NÃO USE ESTE SOFTWARE PARA ARMAZENAR OU GERENCIAR CRIPTOMOEDAS REAIS**

## Licença

MIT License - Veja o arquivo LICENSE para detalhes.

