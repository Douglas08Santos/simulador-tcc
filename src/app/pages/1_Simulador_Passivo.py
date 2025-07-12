import streamlit as st
import matplotlib.pyplot as plt


# Função de cálculo de juros compostos
def simular_passivo(inicial, mensal, anos, taxa):
    taxa_mensal = (1 + taxa / 100) ** (1 / 12) - 1
    saldo = [inicial]
    for _ in range(anos * 12):
        resultado = saldo[-1] * (1 + taxa_mensal) + mensal
        saldo.append(round(resultado, 2))
    return saldo

def criar_grafico(resultado):
    tempo = list(range(len(resultado)))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(tempo, resultado, color='green')
    # Adicionando rotulos nos resultados anuais
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
    return fig

# --------- Streamlit
st.set_page_config(page_title="Simulador Passivo", layout="centered")
st.title("Simulador - Investidor Passivo")


st.markdown("""
Nesta simulação, o investidor realiza aportes mensais constantes e obtém um retorno fixo ao longo do tempo (juros compostos).

Ideal para perfis conservadores ou com horizonte de longo prazo.
""")

# Entradas do usuário
aporte_inicial = st.number_input("Aporte Inicial (R$)", value=500, step=500)
aporte_mensal = st.number_input("Aporte Mensal (R$)", value=500, step=100)
anos = st.slider("Período da Simulação (anos)", 1, 40, 10)
taxa_anual = st.slider("Retorno Anual (%)", 1, 20, 5)

if st.button("Simular"):
    resultado = simular_passivo(aporte_inicial, aporte_mensal, anos, taxa_anual)

    # Explicação textual dos resultados
    total_aportado = aporte_inicial + aporte_mensal * (anos * 12)
    ganho = resultado[-1] - total_aportado
    percentual = (ganho / total_aportado) * 100
    st.markdown("---")
    st.subheader("Explicação dos Resultados")
    st.markdown(f"""
        **Parâmetros definidos:**
        - Aporte inicial: R$ {aporte_inicial:,.2f}
        - Aporte mensal: R$ {aporte_mensal:,.2f}
        - Período: {anos} anos ({anos * 12} meses)
        - Rentabilidade anual: {taxa_anual}% ao ano

        **Resultados obtidos:**
        - Total investido no período: R$ {total_aportado:,.2f}
        - Saldo final estimado: R$ {resultado[-1]:,.2f}
        - Ganho obtido com os juros compostos: R$ {ganho:,.2f} (**{percentual:.2f}% de retorno sobre o capital investido**)

        **Análise:**
        Mesmo com aportes constantes e um retorno conservador de {taxa_anual}% ao ano, o simulador mostra que a 
        disciplina nos aportes e o tempo são elementos-chave para alcançar bons resultados financeiros no longo prazo.
            """)
    st.subheader("A seguir, temos um gráfico ilustrando o progresso dessa estratégia:")
    grafico = criar_grafico(resultado)
    st.pyplot(grafico)
else:
    st.info("Preencha os parâmetros e clique em Simular para visualizar o resultado.")
