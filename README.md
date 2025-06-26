
# 📊 Simulador de Estratégias de Investimento com Python e Streamlit

Este projeto implementa um **simulador interativo de estratégias de investimento** usando **Python**, **Streamlit** e **yFinance**, permitindo a simulação de diferentes perfis e técnicas de alocação de capital em ativos da bolsa de valores.

## 🎯 Objetivo

Oferecer uma ferramenta educacional e analítica para investidores e estudantes, com foco em estratégias como:

- Investimento **Passivo**
- Estratégias **Técnicas** (médias móveis)
- Estratégias **Qualitativas** (momentum)
- Estratégias com **Derivativos e Opções**:
  - Protective Put
  - Bull Call Spread

---

## 🧩 Estrutura do Projeto

```text
📁 projeto_simulador_investimentos/
│
├── Home.py                         # Página inicial: pesquisa de ativos e earnings
├── pages/
    ├── 1_Simulador_Passivo.py         # Estratégia passiva de longo prazo (juros compostos)
    ├── 2_Simulador_Tecnico.py         # Estratégia de cruzamento de médias móveis
    ├── 3_Simulador_Qualitativo.py     # Estratégia de momentum baseada em retornos acumulados
    ├── 4_Simulador_Protective_Put.py  # Estratégia com opções (put) como proteção
    └── 5_Simulador_Bull_Call_Spread.py# Estratégia Bull Call Spread com calls ITM e OTM
├── earnings/                      # Módulo com lista das próximas divulgações de resultados
├── README.md                      # Este arquivo
└── requirements.txt               # Bibliotecas necessárias
```

---

## 🖥️ Funcionalidades por Página

### 🔹 `Home.py`

- Pesquisa de ativos via [Yahoo Finance](https://finance.yahoo.com)
- Visualização de últimas cotações
- Calendário de divulgações de resultados ("earnings") via [TradingView](https://www.tradingview.com/markets/stocks-usa/earnings/)

### 🔹 `1_Simulador_Passivo.py`

- Simula aportes mensais constantes com taxa fixa de retorno (juros compostos)
- Ideal para perfil conservador de longo prazo
- Geração de gráfico e saldo final

### 🔹 `2_Simulador_Tecnico.py`

- Estratégia com cruzamento de médias móveis (MM20 x MM50)
- Compra e venda baseadas em sinais técnicos
- Mostra histórico de operações e evolução do capital

### 🔹 `3_Simulador_Qualitativo.py`

- Estratégia de **momentum**: seleciona os dois ativos com melhor desempenho nos últimos 2 meses
- Rebalanceamento mensal automático
- Permite adicionar e customizar lista de ativos

### 🔹 `4_Simulador_Protective_Put.py`

- Simula compra de ações com proteção de opções de venda (puts)
- Permite configurar porcentagens de strike e prêmio
- Mostra custo total, lucro líquido e evolução gráfica

### 🔹 `5_Simulador_Bull_Call_Spread.py`

- Estratégia com derivativos: compra de call ITM e venda de call OTM
- Simulação mensal com ajuste de parâmetros (prêmio, strike, etc.)
- Exibe lucro bruto, custo total e lucro líquido acumulado

---

## ⚙️ Instalação

```bash
git clone https://github.com/Douglas08Santos/simulador-tcc
cd simulador-tcc
pip install -r requirements.txt
```

---

## ▶️ Como Executar

No terminal:

```bash
streamlit run src/app/Home.py
```

Ou para abrir outras páginas diretamente:

```bash
streamlit run run src/app/pages/1_Simulador_Passivo.py
```

As demais páginas estarão acessíveis no menu lateral, se organizadas corretamente na pasta `/pages`.

---

## 🧪 Requisitos

- Python 3.9+
- Streamlit
- yfinance
- pandas
- matplotlib
- requests
- beautifulsoup4

Para instalar manualmente:

```bash
pip install streamlit yfinance pandas matplotlib requests beautifulsoup4
```

---

## 📚 Referências

- [Streamlit Documentation](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/stable/)
- [Yahoo Finance API via yFinance](https://pypi.org/project/yfinance/)
---

## 🧠 Licença

Este projeto é de uso livre para fins **educacionais e acadêmicos**. Comercialização ou distribuição não autorizada é desencorajada sem menção ao autor original.

---

## 💡 Observações

- Os resultados da simulação são baseados em dados históricos e **não representam recomendação de investimento**.
- O simulador pode ser expandido com novas estratégias, como **Straddle**, **Iron Condor**, **Market Neutral**, entre outras.

---

> Desenvolvido por [Douglas Alexandre dos Santos](santosdouglas0809@gmail.com)
>
> *“A melhor forma de prever o futuro é criá-lo.” – Peter Drucker*
