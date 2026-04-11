import requests

URL = "http://127.0.0.1:8000/api/v1/registrar"
HEADERS = {"x-api-key": "MOISES_PROG_2026_JF"}

dados = {
    "injetora_id": "Haitian Pluto 01",
    "molde_id": "MOLDE_A1",
    "op_id": "OP-2026-X",
    "pecas_boas": 85,
    "pecas_ruins": 3,
    "consumo_kwh": 12.8,
    "status_maquina": "Produzindo"
}

try:
    response = requests.post(URL, json=dados, headers=HEADERS)
    if response.status_code == 200:
        print("✅ Dados enviados com sucesso para o banco local!")
        print(f"Selo ISO gerado: {response.json()['hash']}")
    else:
        print(f"❌ Erro: {response.status_code}")
except Exception as e:
    print(f"🚨 Servidor desligado? Erro: {e}")