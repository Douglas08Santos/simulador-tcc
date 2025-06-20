import yfinance as yf
import pandas as pd

# Baixando dados financeiros históricos da PETR4 (Petrobras) entre 2020 a 2025
dados = yf.download('PETR4.SA', start='2020-01-01', end='2025-01-01')

# Selecionando apenas o preço de fechamento
precos = dados['Close']

# Calando a média móvel de 20 dias
mm20 = precos.rolling(window=20).mean()


