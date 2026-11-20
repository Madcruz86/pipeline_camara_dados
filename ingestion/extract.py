import requests
import json
import time
import os
import boto3

# URL base para pegar as despesas de um deputado específico (iremos utilizar o 209787)
URL_INICIAL = "https://dadosabertos.camara.leg.br/api/v2/deputados/209787/despesas?ano=2024&itens=100&formato=json"

def extrair_despesas(url):
    despesas_totais = []
    url_atual = url
    pagina = 1

    while url_atual:
        print(f'Buscando página {pagina}...')

        # 1. Faz a requisição
        resposta = requests.get(url_atual)

        # Verifica de deu erro
        if resposta.status_code != 200:
            print(f"Erro na requisição: {resposta.status_code}")
            break

        dados_json = resposta.json()

        # 2. Pega os dados da página atual e adiciona na lista total
        despesas_pagina = dados_json.get("dados", [])
        despesas_totais.extend(despesas_pagina)

        print(f"  -> {len(despesas_pagina)} registros encontrados nessa página.")

        # 3. Procura o link da proxima página
        url_atual = None # Reseta a URL
        for link in dados_json.get("links", []):
            if link.get("rel") == "next":
                url_atual = link.get("href")
                break

        # Boa prática: dar um pequeno sleep para não sobrecarrecar a API

        time.sleep(1)
        pagina += 1

    return despesas_totais

if __name__ == "__main__":
    print("Iniciando a extração...")
    dados = extrair_despesas(URL_INICIAL)
    print(f"Extração finalizada. Total de registros: {len(dados)}")

    # 4. Salvar em arquivo local
    os.makedirs("data/raw", exist_ok=True)
    caminho_arquivo = 'data/raw/despesas_209787_2024.json'

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    print(f"Dados salvos em {caminho_arquivo}")

    # Upload para o S3
    print(f"Iniciando o upload para o S3...")
    s3_client = boto3.client('s3')
    nome_bucket = 'bucket-pipeline-camara-2024'
    caminho_s3 = 'raw/despesas/ano=2024/despesas_209787_2024.json'

    try:
        s3_client.upload_file(caminho_arquivo, nome_bucket, caminho_s3)
        print(f"Sucesso! Arquivo enviado para o s3://{nome_bucket}/{caminho_s3}")
    except Exception as e:
        print(f"Erro no upload: {e}")
        
