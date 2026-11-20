import json


with open("data/raw/despesas_209787_2024.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

print(f"Total de registros: {len(dados)}")
print("\n--- Chaves do primeiro registro ---")
for chave in dados[0].keys():
    print(f"- {chave}")
    