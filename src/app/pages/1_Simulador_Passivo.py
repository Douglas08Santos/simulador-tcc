import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador Passivo", layout="centered")
st.title("Simulador - Investidor Passivo")

st.markdown("""
Nesta simulação, o investidor realiza aportes mensais constantes e obtém um retorno fixo ao longo do tempo (juros compostos).
Ideal para perfis conservadores ou com horizonte de longo prazo.
""")

# Entradas do usuário
aporte_inicial = st.number_input("Aporte Inicial (R$)", value=10000, step=500)
aporte_mensal = st.number_input("Aporte Mensal (R$)", value=500, step=100)
anos = st.slider("Período da Simulação (anos)", 1, 40, 30)
taxa_anual = st.slider("Retorno Anual (%)", 1, 20, 8)

# Função de cálculo de juros compostos
def simular_passivo(inicial, mensal, anos, taxa):
    taxa_mensal = (1 + taxa / 100) ** (1 / 12) - 1
    saldo = [inicial]
    for _ in range(anos * 12):
        saldo.append(saldo[-1] * (1 + taxa_mensal) + mensal)
    return saldo

if st.button("Simular"):
    resultado = simular_passivo(aporte_inicial, aporte_mensal, anos, taxa_anual)
    # Como não tem uma opção center = True, é usado colunas para centralizar
    _, _,col = st.columns(3)
    with col:
        st.metric("Saldo Final", f"R$ {resultado[-1]:,.2f}")
    tempo = list(range(len(resultado)))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(tempo, resultado, color='green')
    # Adicionando rotulos dos resultados anuais
    for i in range(len(resultado)):
        if i > 0 and i % 12 == 0:
            ax.text(
                x=tempo[i],
                y=resultado[i],
                s='R${:,.2f}'.format(round(resultado[i], 2)),
                va='top',
                ha='left'
            )
    ax.set_title("Evolução do Saldo - Investidor Passivo")
    ax.set_xlabel("Meses")
    ax.set_ylabel("Saldo acumulado (R$)")
    ax.grid(True)
    st.pyplot(fig)

else:
    st.info("Preencha os parâmetros e clique em Simular para visualizar o resultado.")
