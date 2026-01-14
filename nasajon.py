import pandas as pd
import requests
import unicodedata
from thefuzz import process

TOKEN = "token apagado por segurança no github"
URL_IBGE = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
URL_CORRECAO = "https://mynxlubykylncinttggu.functions.supabase.co/ibge-submit"

def normalizar(t):
    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().strip()

print("Consultando API do IBGE...")
municipios_ibge = requests.get(URL_IBGE).json()
nomes_oficiais = [m['nome'] for m in municipios_ibge]
mapa_ibge = {normalizar(m['nome']): m for m in municipios_ibge}

df = pd.read_csv('input.csv', skipinitialspace=True)
resultados = []
ids_processados = set()

print("Processando municípios...")
for _, row in df.iterrows():
    m_input = str(row['municipio']).strip()
    pop_input = int(row['populacao'])

    melhor_match, score = process.extractOne(m_input, nomes_oficiais)

    status = "NAO_ENCONTRADO"
    match = None
    id_ibge = None

    if score > 85:
        match_temp = mapa_ibge.get(normalizar(melhor_match))
        id_temp = match_temp['id']

        if id_temp not in ids_processados:
            ids_processados.add(id_temp)
            match = match_temp
            id_ibge = id_temp
            status = "OK"
        else:
            status = "AMBIGUO"

    if status == "OK":
        resultados.append({
            "municipio_input": m_input,
            "populacao_input": pop_input,
            "municipio_ibge": match['nome'],
            "uf": match['microrregiao']['mesorregiao']['UF']['sigla'],
            "regiao": match['microrregiao']['mesorregiao']['UF']['regiao']['nome'],
            "id_ibge": id_ibge,
            "status": "OK"
        })
    else:
        resultados.append({
            "municipio_input": m_input, "populacao_input": pop_input,
            "municipio_ibge": None, "uf": None, "regiao": None, "id_ibge": None,
            "status": status
        })

df_res = pd.DataFrame(resultados)
df_res.to_csv('resultado.csv', index=False)

df_ok = df_res[df_res['status'] == "OK"]
stats = {
    "total_municipios": len(df_res),
    "total_ok": len(df_ok),
    "total_nao_encontrado": len(df_res[df_res['status'] != "OK"]),
    "total_erro_api": 0,
    "pop_total_ok": int(df_ok['populacao_input'].sum()),
    "medias_por_regiao": df_ok.groupby('regiao')['populacao_input'].mean().to_dict()
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("Enviando resultados para a Nasajon...")
resp = requests.post(URL_CORRECAO, headers=headers, json={"stats": stats})

print("\n--- RESPOSTA FINAL ---")
print(resp.json())