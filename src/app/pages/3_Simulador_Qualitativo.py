import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title='Simulador Qualitativo (Momentum)', layout='centered')
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
# st.session_state = Cache
if 'acoes' not in st.session_state:
    st.session_state.acoes = ['PETR4.SA', 'VALE3.SA', 
                              'ITUB4.SA', 'WEGE3.SA', 
                              'BBDC3.SA', 'ABEV3.SA',
                              'BBAS3.SA', 'BPAC11.SA',
                              'SANB11.SA', 'ITSA4.SA']
                            
# Campo para adicionar nova ação
if "novo_ativo" not in st.session_state:
    st.session_state.novo_ativo = ''
# Callback para limpar campor de texto
def submit():
    st.session_state.novo_ativo = st.session_state.input
    st.session_state.input = ''

st.text_input("Adicionar novo ativo:", key="input", on_change=submit, placeholder='Novo ativo')

# Atualiza a lista se o usuário teclar Enter
novo_ativo = st.session_state.novo_ativo
if novo_ativo and novo_ativo.upper() not in st.session_state.acoes:
    st.session_state.acoes.append(novo_ativo.upper())
    st.success('{} adicionado a lista'.format(novo_ativo.upper()))
    novo_ativo = st.session_state.novo_ativo = '' 
elif novo_ativo and novo_ativo.upper() in st.session_state.acoes:
    st.warning('{} já existe na lista'.format(novo_ativo.upper()))
    novo_ativo = st.session_state.novo_ativo = '' 


# Ativos
# TODO: Fazer com que ao adicionar um novo ativo, os ativos selecionados não sumam
ativos = st.multiselect(
    'Selecione os ativos para a simulação (ex: PETR4.SA, VALE3.SA, ITUB4.SA)',
    options=st.session_state.acoes, placeholder='Escolha seus ativos'
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

capital_inicial = st.number_input('Aporte Mensal', value=500, step=500)

# Função de simulação
@st.cache_data
def baixar_dados(tickers, periodo):
    data = {}
    moedas = []
    
    for ticker in tickers:
        try:
            ticker = ticker.upper()
            dados = yf.Ticker(ticker)
            moedas.append(dados.get_info()['currency'])
            df_dados_historicos = dados.history(periodo)['Close'].resample('ME').last()
            data[ticker] = df_dados_historicos.iloc[:-1]
        except:
            raise ValueError("Erro ao procurar o ativo {}. Confira o nome ou substitua por outro.".format(ticker))
    return pd.DataFrame(data), moedas

def simular_momentum(df, capital_inicial):
    saldo = capital_inicial
    historico = []

    for i in range(2, len(df)):
        retornos = df.iloc[i-2:i].pct_change().dropna().add(1).prod() - 1
        top2 = retornos.sort_values(ascending=False).head(2).index.tolist()

        if i+1 < len(df):
            saldo = capital_inicial
            investimento_total = saldo

            saldo = 0
            saldo_venda = 0

            for ativo in top2:
                alocacao = investimento_total / 2
                preco_compra = df[ativo].iloc[i]
                qtd = alocacao // preco_compra
                restante = alocacao - (qtd * preco_compra)
                preco_venda = df[ativo].iloc[i+1]
                saldo_venda = qtd * preco_venda
                saldo_final = restante + saldo_venda
                
                historico.append({
                    'Data': df.index[i],
                    'Ativo': ativo,
                    'Alocação': round(investimento_total / 2, 2),
                    'Preço Compra': round(preco_compra, 2),
                    'Investimento Real': round(qtd * preco_compra, 2),
                    'Qtd': qtd,
                    'Restante Alocação': round(restante, 2),
                    'Preço Venda': round(preco_venda, 2),
                    'Saldo Venda': round(qtd * preco_venda, 2),
                    'Rendimento (em %)':round((preco_venda - preco_compra)/preco_compra * 100, 2),
                    'Saldo Final': round(saldo_final, 2)
                })
        else:
            data = df.index[i].strftime('%d/%m/%Y')
            st.success('A recomendação para o dia {} foram: {}'.format(data, top2))

    df_historico = pd.DataFrame(historico)
    return df_historico

# Executar simulação
if st.button('Simular Estratégia'):
    if len(ativos) < 3:
        st.warning('Escolha pelo menos 3 ativos para a simulação.')
    else:
        with st.spinner('Baixando dados e executando simulação...'):
            try:
                df_precos, moedas = baixar_dados(ativos, opcoes_dic[periodo])

                if len(set(moedas)) == 1: # Significando que a unidade monetaria entre as empresass são as mesmas:
                    moeda = moedas[0]
                    df_resultado = simular_momentum(df_precos, capital_inicial)

                    # Tabela de Alocações
                    st.subheader('Histórico de Alocações')
                    # Converte a coluna 'Data' para datetime e formata
                    df_resultado['Data'] = pd.to_datetime(df_resultado['Data']).dt.strftime('%d/%m/%Y')
                    # Renomeando colunas para impressão da tabela

                    df_resultado = df_resultado.rename(columns={
                        'Alocação': 'Alocação ({})'.format(moeda),
                        'Preço Compra': 'Preço de Compra ({})'.format(moeda),
                        'Investimento Real': 'Investimento Real ({})'.format(moeda),
                        'Qtd': 'Quantidade',
                        'Restante Alocação': 'Restante da Alocação ({})'.format(moeda),
                        'Preço Venda': 'Preço de Venda ({})'.format(moeda),
                        'Saldo Venda': 'Saldo Venda ({})'.format(moeda),
                        'Saldo Final': 'Saldo Final ({})'.format(moeda),
                    })
                    
                    st.dataframe(df_resultado)

                    # Cálculo dos dados agregados para explicação
                    num_meses = df_resultado['Data'].nunique()
                    ativos_usados = df_resultado['Ativo'].nunique()
                    saldo_final_total = df_resultado['Saldo Final ({})'.format(moeda)].sum()
                    aporte_total = capital_inicial * (num_meses - 1)
                    ganho_total = saldo_final_total - aporte_total
                    retorno_percentual = (ganho_total / aporte_total) * 100

                    st.markdown("---")
                    st.subheader("Explicação dos Resultados")

                    st.markdown(f"""
                    **Parâmetros definidos:**
                    - Capital inicial: **{moeda} {capital_inicial:,.2f}**
                    - Período analisado: **{periodo}**
                    - Ativos utilizados: **{ativos_usados}** ativos
                    - Alocações mensais realizadas: **{num_meses}** (**{num_meses*2}** alocações inviduais)
                    """)

                    try:
                        # Garantindo que as colunas numéricas estão no formato correto
                        df_resultado["Rendimento (em %)"] = pd.to_numeric(df_resultado["Rendimento (em %)"], errors="coerce")
                        df_resultado["Saldo Final ({})".format(moeda)] = pd.to_numeric(df_resultado["Saldo Final ({})".format(moeda)], errors="coerce")
                        df_resultado["Alocação ({})".format(moeda)] = pd.to_numeric(df_resultado["Alocação ({})".format(moeda)], errors="coerce")

                        resumo_ativos = df_resultado.groupby("Ativo").agg(
                            vezes_escolhido=("Ativo", "count"),
                            rendimentos_positivos=("Rendimento (em %)", lambda x: (x > 0).sum()),
                            rendimentos_negativos=("Rendimento (em %)", lambda x: (x < 0).sum()),
                            media_retorno=("Rendimento (em %)", "mean"),
                            retorno_maximo=("Rendimento (em %)", "max"),
                            retorno_minimo=("Rendimento (em %)", "min"),
                        ).sort_values(by="vezes_escolhido", ascending=False)

                        resumo_ativos = resumo_ativos.rename(columns={
                            'vezes_escolhido': '# Escolhido',
                            'rendimentos_positivos': 'Rendimentos Positivos',
                            'rendimentos_negativos': 'Rendimentos Negativos',
                            'media_retorno': 'Retorno Médio',
                            'retorno_maximo': 'Retorno Máximo',
                            'retorno_minimo': 'Retorno Minimo'
                        })

                        st.dataframe(resumo_ativos.round(2))

                        total_ciclos = df_resultado.shape[0] // 2
                        valor_final = df_resultado["Saldo Final ({})".format(moeda)].sum()
                        aporte_total_df = df_resultado["Alocação ({})".format(moeda)].sum()
                        rentabilidade_total = (valor_final - aporte_total_df) / aporte_total_df * 100

                        melhor = df_resultado.loc[df_resultado["Rendimento (em %)"].idxmax()]
                        pior = df_resultado.loc[df_resultado["Rendimento (em %)"].idxmin()]

                        st.markdown(f"""
                    - **Total de ciclos de investimento:** {total_ciclos} ({total_ciclos*2} alocações individuais)  
                    - **Aporte total (somado da alocação):** {moeda} {aporte_total_df:,.2f}  
                    - **Valor final acumulado:** {moeda} {valor_final:,.2f}  
                    - **Rentabilidade acumulada:** {rentabilidade_total:.2f}%  

                    **Melhor rendimento individual:**  
                    - Ativo: **{melhor['Ativo']}**  
                    - Data: {melhor['Data']}  
                    - Retorno: **{melhor['Rendimento (em %)']}%**

                    **Pior rendimento individual:**  
                    - Ativo: **{pior['Ativo']}**  
                    - Data: {pior['Data']}  
                    - Retorno: **{pior['Rendimento (em %)']}%**

                     **Análise:**
                    A estratégia de momentum favorece ativos com desempenho recente superior, 
                    realocando o capital mensalmente nos dois com melhor desempenho nos últimos 
                    dois meses. Neste cenário, o resultado mostra um ganho líquido expressivo, reforçando
                    a eficácia da abordagem em tendências positivas. No entanto, a estratégia pode apresentar
                    maior rotatividade e maior exposição a reversões repentinas de mercado.
                    """)

                    except Exception as e:
                        st.warning(f"Erro ao gerar estatísticas: {e}")

                    # Gráfico de evolução
                    st.subheader('Gráfico de Evolução')

                    # Converter a coluna de datas para datetime
                    df_resultado['Data'] = pd.to_datetime(df_resultado['Data'], dayfirst=True)

                    # Agrupar por mês e somar os saldos finais
                    df_mensal = df_resultado.groupby(df_resultado['Data'].dt.to_period('M'))['Saldo Final ({})'.format(moeda)].sum().reset_index()
                    df_mensal['Data'] = df_mensal['Data'].dt.to_timestamp()

                    # Plotar o gráfico
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(df_mensal['Data'], df_mensal['Saldo Final ({})'.format(moeda)], marker='o', linestyle='-', color='royalblue')
                    ax.set_title('Evolução do Capital - Estratégia de Momentum')
                    ax.set_ylabel('Saldo Final ({})'.format(moeda))
                    ax.grid(True)         

                    st.pyplot(fig)


                    st.markdown("""
                                ---
                            **Legenda da tabela:**

                            - **Data** – Data da operação de compra do ativo ou da simulação correspondente ao período analisado.
                            - **Ativo** – Código do ativo negociado (ex: PETR4.SA, ITUB4.SA).
                            - **Alocação ({moeda})** – Valor total disponível para investir naquele ativo naquele mês.
                            - **Preço de Compra ({moeda})** – Cotação da ação no momento da compra.
                            - **Investimento Real ({moeda})** – Valor efetivamente utilizado para comprar ações: `Preço de Compra × Quantidade`.
                            - **Quantidade** – Número de ações compradas com base no valor do investimento real.
                            - **Restante da Alocação ({moeda})** – Valor que sobrou da alocação original após a compra, geralmente por não ser possível comprar frações de ações.
                            - **Preço de Venda ({moeda})** – Cotação da ação no mês seguinte (simulação de saída).
                            - **Saldo Venda ({moeda})** – Valor obtido com a venda das ações: `Quantidade × Preço de Venda`.
                            - **Rendimento (em %)** – Variação percentual entre o preço de venda e o preço de compra: `((Preço de Venda - Preço de Compra)/ Preço de Compra × 100`.
                            - **Saldo Final ({moeda})** – Soma do saldo da venda com o valor restante da alocação: `Saldo Venda + Restante da Alocação`.
                    """.format(moeda = moeda))
                else:
                    raise ValueError("Unidades Monetárias diferentes: {}. Devem ser iguais.".format(moedas))
            except Exception as e:
                st.error(f'Erro na simulação: {e}')
else:
    st.info('Configure os parâmetros acima e clique em "Simular Estratégia" para começar.')
