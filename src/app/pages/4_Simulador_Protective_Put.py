import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


# Simulação da estratégia Protective Put
def protective_put(df, aporte_mensal, moeda):
    df['Strike'] = df['Close'] * (100 - strikes_dic[valor_strike])/100
    df['Premio'] = df['Close'] * (premio_dic[valor_premio])/100
    df['Qtd_Acoes'] = aporte_mensal // df['Close']
    df['Custo_Acoes'] = df['Qtd_Acoes'] * df['Close']
    df['Custo_Put'] = df['Qtd_Acoes'] * df['Premio']
    df['Custo_Total'] = df['Custo_Acoes'] + df['Custo_Put']
    df['Preço de Venda ({})'.format(moeda)] = 1.0

    valor_final = []
    for i in range(len(df) - 2):
        preco_venda = df.loc[df.index[i+1], 'Close']
        df.loc[df.index[i], 'Preço de Venda ({})'.format(moeda)] = round(preco_venda, 2)
        strike = df.loc[df.index[i], 'Strike']
        qtd = df.loc[df.index[i], 'Qtd_Acoes']

        # Se ação caiu abaixo do strike, put gera lucro
        lucro_put = max(0, strike - preco_venda) * qtd
        valor_acoes = preco_venda * qtd
        valor_final.append(valor_acoes + lucro_put)

    df = df.iloc[:-2].copy()
    
    df['Valor_Final'] = valor_final
    df['Lucro_Liquido'] = df['Valor_Final'] - df['Custo_Total']
    
    return df

def baixar_dados(ticker):
    try:
        dados = yf.Ticker(ticker)
        moeda = dados.get_info()['currency']
    except:
        raise ValueError("Erro ao procurar o ativo {}. Confira o nome ou substitua por outro.".format(ticker))
    
    return dados


# --- Streamlit
st.set_page_config(page_title='Simulador Opções', layout='centered')
st.title('Simulador - Estratégia com Opções: Protective Put')

st.markdown('''
Esta simulação demonstra a estratégia **Protective Put**, onde o investidor compra ações e simultaneamente compra uma opção de venda (put) como forma de proteção.

**Premissas:**
- Aporte mensal constante em ações
- Compra de puts com vencimento de 30 dias
            
**Personalizações disponíveis:**
- Escolha de ativo (ticker)
- Aporte mensal
- Período de simulação
- Porcentagem do Strike da put (5% abaixo do preço da ação por padrão)
- Porcentagem do prêmio da put (2% do valor da ação por padrão)
''')

# Entradas do usuário
ticker = st.text_input('Ticker da Ação (ex: PETR4.SA, VALE3.SA, AAPL)', value='PETR4.SA')

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

aporte_mensal = st.number_input('Aporte Mensal', value=500, step=500)

# Criando o select_slider para o strike
strikes = list(range(1, 11))
legenda_strike = [str(i) for i in range(1, 11)]
strikes_dic = dict(zip(legenda_strike, strikes))
valor_strike = st.select_slider(
    'Selecione a porcentagem (%) do strike:',
    options=legenda_strike,
    value='5' # Valor Inicial
)

# Criando o select_slider para o strike
premios = list(range(1, 11))
legenda_premio = [str(i) for i in range(1, 11)]
premio_dic = dict(zip(legenda_premio, premios))
valor_premio = st.select_slider(
    'Selecione a porcentagem (%) do prêmio:',
    options=legenda_strike,
    value='2' # Valor Inicial
)



# Execução da simulação
if st.button('Simular Estratégia'):
    with st.spinner('Executando simulação da estratégia Protective Put...'):
        try:
            ticker = ticker.upper()
            dados = baixar_dados(ticker)
            df_dados_historicos = dados.history(opcoes_dic[periodo])['Close'].resample('ME').last()
            moeda = dados.get_info()['currency']   
            # Converter para Dataframe
            df_dados_historicos = pd.DataFrame(df_dados_historicos)
            df_resultado = protective_put(df_dados_historicos, aporte_mensal, moeda)

            # Tabela de resultados
            # Renomeando colunas para impressão da tabela
            df_resultado = df_resultado.rename(columns={
                'Close': 'Preço de Compra ({})'.format(moeda),
                'Strike': 'Strike de {}%'.format(strikes_dic[valor_strike]),
                'Premio': 'Prêmio de {}%'.format(premio_dic[valor_premio]),
                'Custo_Acoes': 'Custo das Ações',
                'Custo_Put': 'Custo da Put',
                'Custo_Total': 'Custo Total',
                'Valor_Final': 'Valor Final ({})'.format(moeda),
                'Lucro_Liquido': 'Lucro Liquido ({})'.format(moeda),
                'Qtd_Acoes': '# de Ações',
            })

            st.subheader('Resultado por Mês')
            df_resultado.index.names = ['Data']
            df_resultado.index = df_resultado.index.strftime('%d/%m/%Y')
            
            st.dataframe(df_resultado.round(2))
            
            # Explicação dos Resultados
            st.markdown("---")
            st.subheader("Explicação dos Resultados da Estratégia Protective Put")

            # Cálculos principais
            num_meses = df_resultado.shape[0]
            valor_acumulado = df_resultado['Valor Final ({})'.format(moeda)].sum()
            investimento_total = df_resultado['Custo Total'].sum()
            lucro_liquido_total = df_resultado['Lucro Liquido ({})'.format(moeda)].sum()
            rentabilidade_total = (lucro_liquido_total / investimento_total) * 100 if investimento_total else 0

            # Separar os meses positivos e negativos
            lucro_col = 'Lucro Liquido ({})'.format(moeda)
            df_resultado[lucro_col] = pd.to_numeric(df_resultado[lucro_col], errors='coerce')
            meses_lucro = df_resultado[df_resultado[lucro_col] > 0]
            meses_prejuizo = df_resultado[df_resultado[lucro_col] < 0]

            qtd_lucros = len(meses_lucro)
            qtd_prejuizos = len(meses_prejuizo)

            investido_nos_positivos = meses_lucro['Custo Total'].sum()
            saldo_nos_positivos = meses_lucro['Valor Final ({})'.format(moeda)].sum()

            st.markdown(f"""
            **Parâmetros da Simulação:**
            - Ativo analisado: **{ticker}**
            - Aporte mensal: **{moeda} {aporte_mensal:,.2f}**
            - Período: **{periodo}**
            - Número de meses simulados: **{num_meses}**
            - Strike da Put: **{valor_strike}% abaixo do preço**
            - Prêmio da Put: **{valor_premio}% do valor da ação**

            **Resultados Obtidos:**
            - Valor total acumulado: **{moeda} {valor_acumulado:,.2f}**
            - Total investido: **{moeda} {investimento_total:,.2f}**
            - Lucro líquido estimado: **{moeda} {lucro_liquido_total:,.2f}**
            - Rentabilidade acumulada: **{rentabilidade_total:.2f}%**

            **Desempenho Mensal:**
            - Meses com **lucro positivo**: **{qtd_lucros}**
            - Meses com **prejuízo**: **{qtd_prejuizos}**

            **Somente nos meses positivos:**
            - Total investido: **{moeda} {investido_nos_positivos:,.2f}**
            - Saldo acumulado: **{moeda} {saldo_nos_positivos:,.2f}**
            - Rentabilidade (positivos): **{((saldo_nos_positivos - investido_nos_positivos)/investido_nos_positivos)*100:.2f}%**

            **Análise:**
            A estratégia **Protective Put** se mostrou eficaz em limitar 
            perdas, com **{qtd_lucros}** meses gerando retornos positivos. Apesar
            do custo adicional com a compra das opções de venda, o saldo acumulado
            demonstra proteção contra quedas expressivas. Essa abordagem é ideal para
            investidores que priorizam segurança em ambientes de alta volatilidade.
            """)

            # Geração de gráfico
            st.subheader("A seguir, temos um gráfico ilustrando o progresso dessa estratégia:")
            fig, ax = plt.subplots(figsize=(10,6))
            ax.plot(df_resultado.index, df_resultado['Valor Final ({})'.format(moeda)].cumsum(), label='Valor Final Acumulado', color='green')
            ax.plot(df_resultado.index, df_resultado['Custo Total'].cumsum(), label='Investimento Total', color='gray', linestyle='--')
            ax.set_title('Simulação - Estratégia Protective Put')
            ax.set_ylabel('{}'.format(moeda))
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Melhor e pior mês
            try:
                melhor_mes = df_resultado.loc[df_resultado[lucro_col].idxmax()]
                pior_mes = df_resultado.loc[df_resultado[lucro_col].idxmin()]

                st.markdown(f"""
            **Melhor Mês:**
            - Data: **{melhor_mes.name}**
            - Lucro Líquido: **{moeda} {melhor_mes[lucro_col]:,.2f}**

            **Pior Mês:**
            - Data: **{pior_mes.name}**
            - Lucro Líquido: **{moeda} {pior_mes[lucro_col]:,.2f}**
            """)
            except:
                st.warning("Não foi possível calcular o melhor e pior mês.")


            st.markdown("""
                ---
                 **Legenda da tabela:**
                - **Preço de Compra ({moeda})** – Valor pago por ação
                - **Strike de {valor_strike}%** – Valor do strike da opção put reduzido em {valor_strike}%, representando o valor mínimo de cobertura.
                - **Prêmio de {valor_premio}%** – Valor de pago pela opção put por ação ({valor_premio}% do preço de compra).
                - **# de Ações** – Número total de ações compradas na operação.
                - **Custo das Ações** – Preço total pago pelas ações: `Preço de Compra × # de Ações`.
                - **Custo da Put** – Custo total com proteção: `Prêmio × # de Ações`.
                - **Custo Total** – Soma dos custos com ações e proteção (puts): `Custo Ações + Custo Put`.
                - **Preço de Venda ({moeda})** – Preço da ação no mês seguinte (simulação de venda no futuro).
                - **Valor Final ({moeda})** – Valor total obtido com a venda das ações: `Preço de Venda × # de Ações`.
                - **Lucro Líquido ({moeda})** – Resultado da operação: `Valor Final - Custo Total`.
                """.format(moeda = moeda, valor_strike = valor_strike, valor_premio = valor_premio))

           
        except Exception as e:
            st.error(f'Erro ao executar simulação: {e}')
else:
    st.info('Defina os parâmetros acima e clique em Simular Estratégia.')


