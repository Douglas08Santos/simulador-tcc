from html import parser
import re
import pandas as pd
import requests
from html.parser import HTMLParser

empresa = None
emp = None

if empresa == None:
    url = "https://www.tradingview.com/markets/stocks-usa/earnings/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    # Conteúdo da página (não terá os dados se forem carregados por JS)
    html = response.text

    # Regex para imagem, sigla e nome da empresa
    # rg = 'crossorigin src="(.+?)" alt="">\s+<div>\s+<a.+?>(.+)</a>\s<span class="tv-screener__description">\s+(.*?)</span>'

    # Regex sem a imagem
    rg = 'crossorigin src=".+?" alt="">\s+<div>\s+<a.+?>(.+)</a>\s<span class="tv-screener__description">\s+(.*?)</span>'
    # Regex para extrair os nomes das empresas
    emp = re.findall(rg, html)

    psr = HTMLParser()
    empresas = pd.DataFrame(emp, columns=['Sigla', 'Nome da Empresa'])

    empresas['Nome da Empresa'] = empresas['Nome da Empresa'].str.replace('&amp;', '&', regex=False)

else:
    print('Não precisou pesquisar')
