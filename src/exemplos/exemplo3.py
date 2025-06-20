import yfinance as yf
import streamlit as st

st.set_page_config(page_title='Exemplo Streamlit', layout='centered')
st.title('Exemplo de uso do Streamlit')

# Definindo uma entrada de texto
ticker = st.text_input(
    label='Digite o ticker do ativo (ex: PETR4.SA, VALE3.SA):',
    value='PETR4.SA'
)

# Condição de se o botão for pressionado
if st.button('Simular'):
    dados = yf.Ticker(ticker)

    dados_historicos = dados.history('1mo')
    st.subheader('Últimas Cotações da {}'.format(ticker))
    st.dataframe(dados_historicos)
