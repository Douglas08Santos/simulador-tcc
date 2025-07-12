import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Lista de périodo predefinidas
opcao = ['6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
legenda = ['6 meses', '2 anos', '5 anos', '10 anos', 'máximo']
opcoes_dic = dict(zip(legenda, opcao))

# Função para aplicar estratégia
def estrategia_cruzamento(df):
    df['MM20'] = df['Close'].rolling(window=20).mean()
    df['MM50'] = df['Close'].rolling(window=50).mean()
    df.dropna(inplace=True)
    
    comprado = False
    capital = capital_inicial
    qtd_acoes = 0
    historico = []

    for i in range(1, len(df)):
        if not comprado and df['MM20'].iloc[i] > df['MM50'].iloc[i] and df['MM20'].iloc[i-1] <= df['MM50'].iloc[i-1]:
            preco = df['Close'].iloc[i]
            qtd_acoes = capital // preco
            capital -= qtd_acoes * preco
            historico.append((df.index[i], "Compra", preco, qtd_acoes, capital))
            comprado = True
        elif comprado and df['MM20'].iloc[i] < df['MM50'].iloc[i] and df['MM20'].iloc[i-1] >= df['MM50'].iloc[i-1]:
            preco = df['Close'].iloc[i]
            capital += qtd_acoes * preco
            historico.append((df.index[i], "Venda", preco, qtd_acoes, capital))
            qtd_acoes = 0
            comprado = False

    if comprado:
        preco = df['Close'].iloc[-1]
        capital += qtd_acoes * preco
        historico.append((df.index[-1], "Venda Final", preco, qtd_acoes, capital))

    return df, historico, capital

def baixar_dados(ticker):
    try:
        dados = yf.Ticker(ticker)
        moeda = dados.get_info()['currency']
    except:
        raise ValueError("Erro ao procurar o ativo {}. Confira o nome ou substitua por outro.".format(ticker))
    
    return dados


# ---- Streamlit
st.set_page_config(page_title="Simulador Técnico", layout="centered")
st.title("Simulador - Investidor Técnico (Médias Móveis)")

st.markdown("""
Esta simulação utiliza a estratégia de cruzamento de médias móveis:
- Compra quando a média móvel curta (20 dias) cruza acima da média longa (50 dias)
- Venda quando a média curta cruza abaixo da média longa

**Personalizações disponíveis:**
- Escolha de ativo (ticker)
- Aporte inicial
- Período de simulação
""")

# Entradas do usuário
ticker = st.text_input("Ticker da Ação (ex: PETR4.SA, VALE3.SA, AAPL)", value="PETR4.SA")

# Criando o select_slider
periodo = st.select_slider(
    'Selecione o período, dos últimos:',
    options=opcoes_dic.keys(),
    value='2 anos' # Valor Inicial
)

capital_inicial = st.number_input("Aporte Mensal", min_value=500, value=500, step=500)

# Simulação
if st.button("Simular Estratégia"):
    with st.spinner("Carregando dados e executando simulação..."):
        try:
            dados = baixar_dados(ticker) 

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
                historico = dados.history('5d')
                preco = historico['Close'].iloc[-1]
                moeda = dados.get_info()['currency']   
                st.write('**Cotação Atual ({}):** {}'.format(moeda, round(preco, 2)))

            df_dados_historicos = dados.history(opcoes_dic[periodo])
            df, operacoes, capital_final = estrategia_cruzamento(df_dados_historicos)
           
            # Formatar a data como "dd/mm/aaaa"
            operacoes = [
                (op[0].strftime('%d/%m/%Y'), *op[1:]) for op in operacoes
            ]
            df_op = pd.DataFrame(operacoes, columns=["Data", "Operação", "Preço ({})".format(moeda), 
                                                     "Quantidade de Ações", "Capital Atual ({})".format(moeda)])

            # Resumo explicativo
            st.subheader("Explicação dos Resultados")

            # Cálculos
            num_operacoes = len(df_op)
            capital_final = df_op.iloc[-1, -1]
            ganho_total = capital_final - capital_inicial
            retorno_percentual = (ganho_total / capital_inicial) * 100

            # Contar operações lucrativas vs negativas
            lucros = df_op[df_op["Capital Atual ({})".format(moeda)].diff() > 0].shape[0]
            prejuizos = num_operacoes - lucros

            st.markdown(f"""
            **Parâmetros definidos:**
            - Ativo analisado: `{ticker}`
            - Capital inicial: **{moeda} {capital_inicial:,.2f}**
            - Período da simulação: **{periodo}**
            - Estratégia: Cruzamento de Médias Móveis (MM20 x MM50)

            **Resultados obtidos:**
            - Número total de operações: **{num_operacoes}**
            - Operações com lucro: **{lucros}**
            - Operações com prejuízo: **{prejuizos}**
            - Capital final estimado: **{moeda} {capital_final:,.2f}**
            - Ganho líquido: **{moeda} {ganho_total:,.2f}**
            - Rentabilidade: **{retorno_percentual:.2f}%**

            **Análise:**
            A estratégia de cruzamento de médias móveis é uma técnica amplamente 
            usada para capturar tendências no mercado. Apesar de algumas operações 
            não resultarem em lucro, uma avaliação completa deve sempre considerar 
            também os períodos de prejuízo para medir a **robustez e consistência** 
            da técnica ao longo do tempo..

            """)
             # Resultados
            st.subheader("Histórico de Operações")
            st.dataframe(df_op)

            # Geração de gráfico
            st.subheader("A seguir, temos um gráfico ilustrando o progresso dessa estratégia:")
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df.index, df['Close'], label='Preço')
            ax.plot(df.index, df['MM20'], label='MM20', linestyle='--')
            ax.plot(df.index, df['MM50'], label='MM50', linestyle=':')
            ax.set_title(f"{ticker} - Estratégia Técnica (MM20 x MM50)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

            st.markdown("""
                ---
                **Legenda da tabela:**
                - **Data** – Data em que a operação (compra ou venda) foi realizada.
                - **Operação** – Tipo de operação executada: geralmente **Compra** ou **Venda**.
                - **Preço (BRL)** – Cotação da ação no momento da operação.
                - **Quantidade de Ações** – Número de ações compradas ou vendidas na operação.
                - **Capital Atual (BRL)** – Valor total acumulado após a operação, considerando o capital disponível ou o saldo resultante.

                """.format(moeda = moeda))
        except Exception as e:
            st.error(f"Erro ao executar simulação: {e}")
else:
    st.info("Preencha os parâmetros e clique em 'Simular Estratégia' para ver os resultados.")
