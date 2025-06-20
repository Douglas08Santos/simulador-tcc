import yfinance as yf
import matplotlib.pyplot as plt

# Baixando dados da PETR4.SA
dados = yf.Ticker('PETR4.SA')

# Valores possiveis: ['1d', '5d', '1mo', '3mo', '6mo', '1y', 
#                           '2y', '5y', '10y', 'ytd', 'max']
# Selecionando dados historicos até 1 mês atras
dados_historicos = dados.history('1mo')

dados_historicos.index = dados_historicos.index.strftime('%d/%m')
plt.plot(dados_historicos.index, dados_historicos['Close'])
plt.title('Evolução Cotação das Ações das PETR4.SA')
plt.xlabel('Data')
plt.ylabel('Valor da Ação')
plt.grid(True)
plt.xticks(rotation=45)
plt.show()