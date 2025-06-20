from bs4 import BeautifulSoup
from datetime import datetime
import requests
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from earnings.earnings import empresas

st.set_page_config(page_title='Simulador', layout='centered')

# Parâmetros de entrada do usuário
#st.sidebar.header('Parâmetros da Simulação')

# Título
titulo = 'Pagina Inicial'
st.title(titulo)

st.markdown("""
Esta página permite visualizar o calendário de divulgação de resultados (earnings) para ações, pesquisar ações e consultar cotações atuais.
""")

hoje = datetime.now().strftime('%d/%m/%Y')
st.subheader('Próximas Divulgações dos Resultados (Earnings)'.format(hoje))
st.dataframe(empresas)

st.markdown("""
### Pesquisa de Ações
Digite o ticker (ex: AAPL, MSFT, AMZN, PETR4.SA, VALE3.SA) e veja o preço atual e o calendário de resultados.
""")

#Entrada de ticker
ticker = st.text_input(
    'Digite o ticker da ação (ex: AAPL, MSFT, PETR4.SA):',
    value="PETR4.SA" # Valor Inicial
)

if ticker:
    try:
        dados = yf.Ticker(ticker)

        # Informações Gerais
        info = dados.get_info()

        st.write('**Nome da Empresa:**', info.get('longName', 'N/A'))
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write('**Setor:**', info.get('sector', 'N/A'))
        with col2:
            st.write('**Site:**', info.get('website', 'N/A'))
        with col3:
            #Preço atual
            historico = dados.history('1d')
            preco = historico['Close'].iloc[-1]
            moeda = dados.get_info()['currency']   

            st.write('**Cotação Atual ({}):** {}'.format(moeda, round(preco, 2)))         
        
        # Earnings
        try:
            calendario = dados.calendar
            data = calendario['Earnings Date']
            data = data[0].strftime('%d/%m/%Y')

            st.write('**Data próximo balanço da {}:** {}'.format(ticker, data))
        except:
            st.warning('Não foi possivel obter o calendário de earnings')

        st.subheader('Últimas Cotações da {}'.format(ticker))
        
        # Lista de périodo predefinidas
        opcao = ['1d', '5d', '1mo', '3mo', '6mo', '1y',
                    '2y', '5y', '10y', 'ytd', 'max']
        legenda = ['1 dia', '5 dias', '1 mês', '3 meses', '6 meses',
                    '2 anos', '5 anos', '10 anos', 'máximo']
        opcoes_dic = dict(zip(legenda, opcao))
        
        # Criando o select_slider
        periodo = st.select_slider(
            'Selecione o período',
            options=opcoes_dic.keys(),
            value='5 dias' # Valor Inicial
        )

        #Obtendo dados historicos das cotações       
        df_dados_historicos = dados.history(opcoes_dic[periodo])
        df_dados_historicos.index.names = ['Data'] # Renomeando 'Date' por 'Data'
        # Formatando data para dd/mm/yyyy
        df_dados_historicos.index = df_dados_historicos.index.strftime('%d/%m/%Y')
        df_dados_historicos = df_dados_historicos.rename(columns={
            'Open': 'Abertura',
            'High': 'Alta',
            'Low': 'Baixa',
            'Close': 'Fechamento'
        })

        #Impressão do Dataframe
        st.dataframe(df_dados_historicos[
            ['Abertura', 'Alta', 'Baixa', 'Fechamento']
        ])

        # Geração do gráfico do preço das ações
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_dados_historicos.index, df_dados_historicos[['Fechamento']], label="Saldo Acumulado", color='green')
        ax.set_title("Evolução das Cotações")
        ax.set_ylabel("Valor ({})".format(moeda))
        ax.grid(True)
        plt.xticks(rotation=270)
        #plt.gca().set_xticks([])
        st.pyplot(fig)

    except Exception as e:
        st.warning('Erro ao buscar dados para {}'.format(e))
else:
    st.info('Digite um ticker para iniciar a pesquisa.')

st.markdown("""
---
**Observação:**  
A consulta de ações utiliza dados da biblioteca [yfinance](https://pypi.org/project/yfinance/), que oferece bom suporte para ativos dos Estados Unidos. No entanto, os resultados para ações brasileiras podem ser limitados.

Já os dados de balanços (earnings) são obtidos a partir do [TradingView](https://www.tradingview.com/markets/stocks-usa/earnings/).
        
""")
