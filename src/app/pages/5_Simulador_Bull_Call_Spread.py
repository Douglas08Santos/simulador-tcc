import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import yfinance as yf

st.set_page_config(page_title='Simulador Bull Call Spread', layout='centered')
st.title('Simulador - Estratégia com Opções: Bull Call Spread')

st.markdown('''
Esta simulação utiliza a estratégia **Bull Call Spread**, onde:
- O investidor **compra uma call ITM** (in-the-money)
- E simultaneamente **vende uma call OTM** (out-of-the-money)

A estratégia busca lucro com **alta moderada do ativo**, limitando tanto o lucro quanto a perda.

            
**Premissas:**
- Aporte mensal constante em ações
- Compra e venda de opções com strike e prêmios estimados a partir do preço da ação            
- Compra de puts com vencimento de 30 dias
            
**Personalizações disponíveis:**
- Escolha de ativo (ticker)
- Período de simulação
- Aporte mensal
- Porcentagem do strike de venda (limite superior, OTM) (5% acima do preço da ação, por padrão)
- Porcentagem do strike de compra (limite inferior, ITM) (5% abaixo do preço da ação, por padrão)        
- Porcentagem do prêmio ITM (8% do valor da ação, por padrão)
- Porcentagem do prêmio OTM (3% do valor da ação, por padrão)
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

aporte_mensal = st.number_input('Aporte Mensal (R$)', value=500, step=50)


# Configuração de parametros 
# Criando o select_slider para o strike
strikes = list(range(1, 11))
legenda_strike = [str(i) for i in range(1, 11)]
strikes_dic = dict(zip(legenda_strike, strikes))

# Limite Superior
valor_strike_venda = st.select_slider(
    'Selecione a porcentagem (%) do strike de venda (limite superior, OTM):',
    options=legenda_strike,
    value='5' # Valor Inicial
)

valor_strike_compra = st.select_slider(
    'Selecione a porcentagem (%) do strike de compra (limite inferior, ITM):',
    options=legenda_strike,
    value='5' # Valor Inicial
)

# Criando o select_slider para os prêmios
premios = list(range(1, 11))
legenda_premio = [str(i) for i in range(1, 11)]
premio_dic = dict(zip(legenda_premio, premios))

valor_premio_itm = st.select_slider(
    'Selecione a porcentagem (%) do prêmio ITM:',
    options=legenda_strike,
    value='8' # Valor Inicial
)

valor_premio_otm = st.select_slider(
    'Selecione a porcentagem (%) do prêmio OTM:',
    options=legenda_strike,
    value='3' # Valor Inicial
)

# Cálculos
# Strike Venda - OTM - Superior
# Strike Compra - ITM - Inferior
# Definindo strikes superiores e inferiores da Bull Call Spread
# strike_compra = preco_compra * 0.95 # ITM - 5% a menos
# strike_venda = preco_compra * 1.05  # OTM - 5% a mais
def simular_bull_call(df, aporte_mensal, moeda):
    df['Strike_OTM'] = df['Close'] * ((100 + strikes_dic[valor_strike_venda])/100)
    df['Strike_ITM'] = df['Close'] * ((100 - strikes_dic[valor_strike_compra])/100)
    df['Spread'] = df['Strike_OTM'] - df['Strike_ITM']
    df['Premio_ITM'] = df['Strike_ITM'] * (premio_dic[valor_premio_itm])/100
    df['Premio_OTM'] = df['Strike_OTM'] * (premio_dic[valor_premio_otm])/100
    df['Custo_Estrategia'] = (df['Premio_ITM'] - df['Premio_OTM'])
    df['Qtd_Contratos'] = aporte_mensal // (df['Custo_Estrategia'] * 100)
    df['Custo_Total'] = df['Qtd_Contratos'] * df['Custo_Estrategia'] * 100
    df['Preco_Venda'] = -1.0
    df['Lucro_Bruto'] = -1.0


    valor_final = []
    for i in range(len(df) - 2):
        preco_venda = df.loc[df.index[i+1], 'Close']
        df.loc[df.index[i], 'Preco_Venda'] = round(preco_venda, 2)
        index = df.index[i]
        if preco_venda >= df.loc[index, 'Strike_OTM']:
            df.loc[index, 'Lucro_Bruto'] = df.loc[
                index, 'Spread'] * 100 * df.loc[
                    index, 'Qtd_Contratos']
        elif preco_venda > df.loc[index, 'Strike_ITM']:
            # df['Spread'] = preco_venda - df['Strike_ITM']
            df.loc[index, 'Lucro_Bruto'] = (preco_venda - df.loc[
                index, 'Strike_ITM']) * 100 * df.loc[
                    index, 'Qtd_Contratos']
        else:
            df.loc[index, 'Lucro_Bruto'] = float(0)
        
    df['Lucro_Liquido'] = df['Lucro_Bruto'] - df['Custo_Total']

    df = df.iloc[:-2].copy()

    return df

def baixar_dados(ticker):
    try:
        dados = yf.Ticker(ticker)
        moeda = dados.get_info()['currency']
    except:
        raise ValueError("Erro ao procurar o ativo {}. Confira o nome ou substitua por outro.".format(ticker))
    
    return dados


if st.button('Simular Estratégia'):
    with st.spinner('Executando simulação da estratégia Bull Call Spread...'):
        try:
            ticker = ticker.upper()
            dados = baixar_dados(ticker)
            df_dados_historicos = dados.history(opcoes_dic[periodo])['Close'].resample('ME').last()
            moeda = dados.get_info()['currency']   
            # Converter para Dataframe
            df_dados_historicos = pd.DataFrame(df_dados_historicos)

            df_resultado = simular_bull_call(df_dados_historicos, aporte_mensal, moeda)

            # Tabela de Operações# Renomeando colunas para impressão da tabela
            df_resultado = df_resultado.rename(columns={
                'Close': 'Preço de Compra ({})'.format(moeda),
                'Strike_ITM': 'Strike Inferior(ITM) {}%'.format(strikes_dic[valor_strike_compra]),
                'Strike_OTM': 'Strike Superior(OTM) {}%'.format(strikes_dic[valor_strike_venda]),
                'Premio_ITM': 'Prêmio ITM {}%'.format(premio_dic[valor_premio_itm]),
                'Premio_OTM': 'Prêmio OTM {}%'.format(premio_dic[valor_premio_otm]),
                'Custo_Estrategia': 'Custo da Estratégia',
                'Qtd_Contratos':'# de Contratos',
                'Custo_Total': 'Custo Total',
                'Lucro_Bruto': 'Lucro Bruto ({})'.format(moeda),
                'Lucro_Liquido': 'Lucro Liquído ({})'.format(moeda),
                'Preco_Venda': 'Preço de Venda ({})'.format(moeda)
            })

            df_resultado.index.names = ['Data']
            df_resultado.index = df_resultado.index.strftime('%d/%m/%Y')
            st.subheader('Resultado da Simulação - Bull Call Spread')
            st.dataframe(df_resultado.round(2))

             # Explicação dos Resultados
            st.subheader("Explicação dos Resultados")

            # Cálculos complementares
            num_meses = df_resultado.shape[0]
            meses_lucrativos = (df_resultado['Lucro Liquído ({})'.format(moeda)] > 0).sum()
            meses_negativos = (df_resultado['Lucro Liquído ({})'.format(moeda)] < 0).sum()
            valor_final = df_resultado['Lucro Bruto ({})'.format(moeda)].sum()
            aporte_total = df_resultado["Custo Total"].sum()
            rentabilidade_total = (valor_final - aporte_total) / aporte_total * 100 if aporte_total != 0 else 0

            melhor_mes = df_resultado.loc[df_resultado['Lucro Liquído ({})'.format(moeda)].idxmax()]
            pior_mes = df_resultado.loc[df_resultado['Lucro Liquído ({})'.format(moeda)].idxmin()]

            # Filtrar apenas os meses com lucro líquido positivo
            df_positivos = df_resultado[df_resultado['Lucro Liquído ({})'.format(moeda)] > 0]

            # Cálculos específicos
            valor_final_positivo = df_positivos['Lucro Bruto ({})'.format(moeda)].sum()
            aporte_total_positivo = df_positivos["Custo Total"].sum()
            lucro_liquido_positivo = valor_final_positivo - aporte_total_positivo

            st.markdown(f"""
            **Parâmetros definidos:**
            - Aporte mensal: **{moeda} {aporte_mensal:,.2f}**
            - Período analisado: **{periodo}**
            - Estratégia utilizada: **Bull Call Spread**
            - Strike de compra (ITM): **{valor_strike_compra}% abaixo** do preço da ação
            - Strike de venda (OTM): **{valor_strike_venda}% acima** do preço da ação
            - Prêmio ITM: **{valor_premio_itm}%** do preço da ação
            - Prêmio OTM: **{valor_premio_otm}%** do preço da ação

            **Resumo do desempenho:**
            - Meses com **lucro líquido positivo**: **{meses_lucrativos}**
            - Meses com **resultado negativo**: **{meses_negativos}**
            - **Valor acumulado bruto (lucros antes dos custos):** {moeda} {valor_final:,.2f}
            - **Valor total investido na estratégia:** {moeda} {aporte_total:,.2f}
            - **Lucro líquido estimado:** {moeda} {valor_final - aporte_total:,.2f}
            - **Rentabilidade acumulada:** {rentabilidade_total:.2f}%
    
            **Resultados Somente dos Meses Lucrativos**
            - **Total de meses com lucro:** {df_positivos.shape[0]}  
            - **Valor acumulado bruto (apenas meses positivos):** {moeda} {valor_final_positivo:,.2f}  
            - **Valor investido (nesses meses):** {moeda} {aporte_total_positivo:,.2f}  
            - **Lucro líquido nesses meses:** {moeda} {lucro_liquido_positivo:,.2f}

            **Melhor mês:**
            - Data: **{melhor_mes.name}**
            - Preço de compra: **{moeda} {melhor_mes['Preço de Compra ({})'.format(moeda)]:,.2f}**
            - Preço de venda: **{moeda} {melhor_mes['Preço de Venda ({})'.format(moeda)]:,.2f}**
            - Lucro líquido: **{moeda} {melhor_mes['Lucro Liquído ({})'.format(moeda)]:,.2f}**

            **Pior mês:**
            - Data: **{pior_mes.name}**
            - Preço de compra: **{moeda} {pior_mes['Preço de Compra ({})'.format(moeda)]:,.2f}**
            - Preço de venda: **{moeda} {pior_mes['Preço de Venda ({})'.format(moeda)]:,.2f}**
            - Lucro líquido: **{moeda} {pior_mes['Lucro Liquído ({})'.format(moeda)]:,.2f}**

            **Análise:**
            A estratégia **Bull Call Spread** consiste na **compra de uma call ITM** e **venda de uma call OTM**. 
            Isso resulta em um **custo líquido inicial**, que limita a perda máxima ao valor desse custo.

            - O **lucro é limitado** pela diferença entre os strikes, subtraída do custo da operação.
            - Resultados positivos ocorrem quando o preço do ativo no vencimento **fica acima do strike da call comprada (ITM)**.
            - Resultados excelentes ocorrem quando o preço **atinge ou supera o strike da call vendida (OTM)**.
            - Em meses com desvalorização ou lateralização do ativo, o **lucro é zero ou negativo**, já que o custo da estratégia não é recuperado.

            O desempenho ao longo do tempo depende da **frequência com que o ativo se valoriza dentro da faixa do spread**.
            """
            )

             # Gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df_resultado.index, df_resultado['Lucro_Bruto'].cumsum(),
                    label='Saldo Acumulado', color='green')
            ax.plot(df_resultado.index, df_resultado['Custo_Total'].cumsum(),
                    label='Investimento Total', color='gray', linestyle='--')
            ax.set_title('Simulação - Estratégia Bull Call Spread')
            ax.set_ylabel('{}'.format(moeda))
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)




            st.markdown("""
                ---
                **Observação:**

                - **Preço de Compra ({moeda})** – Valor da ação subjacente no momento da montagem da estratégia.

                - **Strike Inferior (ITM) {strike_compra}%** – Preço de exercício da opção de compra **dentro do dinheiro** (In the Money), 5% abaixo do preço atual.

                - **Strike Superior (OTM) {strike_venda}%** – Preço de exercício da opção de compra **fora do dinheiro** (Out of the Money), 5% acima do preço atual.

                - **Spread** – Diferença entre os strikes: `Strike Superior - Strike Inferior`. Representa o ganho bruto máximo possível por ação.

                - **Prêmio ITM {premio_itm}%** – Prêmio (preço) pago pela opção de strike inferior (ITM), por padrão é considerado {premio_itm}% do valor da ação.

                - **Prêmio OTM {premio_otm}%** – Prêmio (preço) recebido pela venda da opção de strike superior (OTM), por padrão é considerando {premio_otm}% do valor da ação.

                - **Custo da Estratégia** – Custo líquido por ação: `Prêmio ITM - Prêmio OTM`. Representa o valor investido por ação na montagem do spread.

                - **# de Contratos** – Quantidade de contratos negociados (cada contrato geralmente representa 100 ações).

                - **Custo Total** – Valor total investido na estratégia: `Custo da Estratégia × 100 × # de Contratos`.

                - **Lucro Bruto ({moeda})** – Ganho bruto máximo possível: `Spread × 100 × # de Contratos`.

                - **Preço de Venda ({moeda})** – Preço da ação no vencimento ou na simulação do fechamento da posição.

                - **Lucro Líquido ({moeda})** – Resultado final da operação: `Lucro Bruto - Custo Total`. Pode variar conforme o preço de venda da ação no vencimento.

                                        
                        
            """.format(moeda = moeda, strike_compra = valor_strike_compra, strike_venda = valor_strike_venda,
                    premio_itm = valor_premio_itm, premio_otm = valor_premio_itm))

        except Exception as e:
                st.error(f'Erro ao executar simulação: {e}')

else:
    st.info('Defina os parâmetros acima e clique em Simular Estratégia.')
