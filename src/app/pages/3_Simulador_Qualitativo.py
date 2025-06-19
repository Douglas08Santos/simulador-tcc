import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title='Simulador Qualitativo (Momentum)', layout='wide')
st.title('Simulador - Estratégia de Momentum (Qualitativa)')

st.markdown('''
Este simulador aplica uma estratégia de **momentum**, onde o algoritmo seleciona, a cada mês,
os dois ativos com **maior retorno acumulado nos últimos 2 meses**. O investidor então 
**aloca seu aporte igualmente entre os dois ativos**, mantendo por 30 dias e repetindo 
o processo no mês seguinte.

**Personalizações disponíveis:**
- Escolha dos ativos (tickers)
- Aporte inicial e mensal
- Período de simulação
''')


# Iniciar a lista no session_state
if 'acoes' not in st.session_state:
    st.session_state.acoes = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'WEGE3.SA', 'BBDC3.SA', 'ABEV3.SA']


# Campo para adicionar nova ação
nova_acao = st.text_input("Adicionar nova sigla:", key="input_acao")

# Atualiza a lista se o usuário digitar algo novo
if nova_acao and nova_acao.upper() not in st.session_state.acoes:
    st.success('{} adicionado a lista'.format(nova_acao.upper()))
    st.session_state.acoes.append(nova_acao.upper())
elif nova_acao:
    st.warning('{} já existe na lista'.format(nova_acao.upper()))
    
# Inputs
ativos = st.multiselect(
    'Selecione os ativos para a simulação (ex: PETR4.SA, VALE3.SA, ITUB4.SA)',
    options=st.session_state.acoes
)

# Lista de périodo predefinidas
opcao = ['6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
legenda = ['6 meses', '2 anos', '5 anos', '10 anos', 'máximo']
opcoes_dic = dict(zip(legenda, opcao))

# Criando o select_slider
periodo = st.select_slider(
    'Selecione o período, dos últimos:',
    options=opcoes_dic.keys(),
    value='2 anos' # Valor Inicial
)

aporte_inicial = st.number_input('Aporte Inicial', value=500, step=1000)
aporte_mensal = st.number_input('Aporte Mensal', value=500, step=100)

# Função de simulação
@st.cache_data

def baixar_dados(tickers, periodo):
    data = {}
    moedas = []
    for ticker in tickers:
        dados = yf.Ticker(ticker)
        moedas.append(dados.get_info()['currency'])
        df_dados_historicos = dados.history(periodo)['Close'].resample('ME').last()
        data[ticker] = df_dados_historicos.iloc[:-1]
    return pd.DataFrame(data), moedas

def simular_momentum(df, aporte_inicial, aporte_mensal):
    saldo = aporte_inicial
    historico = []

    for i in range(2, len(df)):
        retornos = df.iloc[i-2:i].pct_change().dropna().add(1).prod() - 1
        top2 = retornos.sort_values(ascending=False).head(2).index.tolist()

        if i+1 < len(df):
            # No primeiro mês ele não faz o aporte mensal, só trabalha com o aporte inicial
            investimento_total = saldo + aporte_mensal if i != 2 else saldo

            saldo = 0
            saldo_venda = 0

            for ativo in top2:
                alocacao = investimento_total / 2
                preco_compra = df[ativo].iloc[i]
                qtd = alocacao // preco_compra
                alocacao -= qtd * preco_compra
                preco_venda = df[ativo].iloc[i+1]
                saldo_venda += qtd * preco_venda
                saldo_final = alocacao + saldo_venda
                saldo += saldo_final
                
                historico.append({
                    'Data': df.index[i],
                    'Ativo': ativo,
                    'Alocação': round(investimento_total / 2, 2),
                    'Preço Compra': round(preco_compra, 2),
                    'Investimento Real': round(qtd * preco_compra, 2),
                    'Qtd': qtd,
                    'Restante Alocação': round(alocacao, 2),
                    'Preço Venda': round(preco_venda, 2),
                    'Rendimento (em %)':round((preco_venda - preco_compra)/preco_compra * 100, 2),
                    'Saldo Venda': round(qtd * preco_venda, 2),
                    'Saldo Final': round(saldo_final, 2)
                })
        else:
            data = df.index[i].strftime('%d/%m/%Y')
            st.success('A recomendação para o dia {} foram: {}'.format(data, top2))

    df_historico = pd.DataFrame(historico)
    return df_historico, saldo

# Executar simulação
if st.button('Simular Estratégia'):
    if len(ativos) < 3:
        st.warning('Escolha pelo menos 3 ativos para a simulação.')
    else:
        with st.spinner('Baixando dados e executando simulação...'):
            try:
                df_precos, moedas = baixar_dados(ativos, opcoes_dic[periodo])

                if len(set(moedas)) == 1: # Significando que a unidade monetaria entre as empresass são as mesmas:
                    df_resultado, saldo_final = simular_momentum(df_precos, aporte_inicial, aporte_mensal)
                    st.metric('Saldo Final Estimado', '{} {:,.2f}'.format(moedas[0], saldo_final))
                    
                    # Gráfico de evolução
                    saldo_por_mes = df_resultado.groupby('Data')['Saldo Final'].sum()
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(saldo_por_mes.index, saldo_por_mes.values, marker='o', label='Saldo Acumulado')
                    ax.set_title('Evolução do Capital - Estratégia de Momentum')
                    for i in range(len(saldo_por_mes.index)):
                        ax.text(
                            x=saldo_por_mes.index[i],
                            y=saldo_por_mes.values[i],
                            s='({}){:,.2f}'.format(moedas[0],saldo_por_mes.values[i]),  
                            va='top',
                            ha='left'

                        )
                    ax.set_ylabel('R$')
                    ax.grid(True)
                    ax.legend()
                    st.pyplot(fig)

                    # Tabela de Alocações
                    st.subheader('Histórico de Alocações')
                    # Converte a coluna 'Data' para datetime e formata
                    df_resultado['Data'] = pd.to_datetime(df_resultado['Data']).dt.strftime('%d/%m/%Y')
                    st.dataframe(df_resultado)
                else:
                    raise ValueError("Unidades Monetárias diferentes: {}. Devem ser iguais.".format(moedas))
            except Exception as e:
                st.error(f'Erro na simulação: {e}')
else:
    st.info('Configure os parâmetros acima e clique em "Simular Estratégia" para começar.')
