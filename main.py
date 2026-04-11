import sqlite3
import datetime
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# ================= CONFIG =================
app = FastAPI(
    title="InjexFlow API",
    version="2.0",
    description="API Industrial para controle MES"
)

DB_NAME = "injexflow_industrial.db"
API_KEY = os.getenv("API_KEY", "injex_dev_2026")

# ================= DATABASE =================
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        cursor = conn.cursor()

        # OP
        cursor.execute('''CREATE TABLE IF NOT EXISTS ordens_producao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            op_codigo TEXT UNIQUE,
            produto TEXT,
            meta INTEGER,
            embalagem TEXT,
            qtd_emb INTEGER,
            plano_controle TEXT,
            status TEXT
        )''')

        # Liberações
        cursor.execute('''CREATE TABLE IF NOT EXISTS liberacoes (
            op_id TEXT PRIMARY KEY,
            almox INTEGER DEFAULT 0,
            lib_manipulacao INTEGER DEFAULT 0,
            ferramenta INTEGER DEFAULT 0,
            regulador INTEGER DEFAULT 0
        )''')

        # Logs
        cursor.execute('CREATE TABLE IF NOT EXISTS logs_almox (op_id TEXT, material TEXT, lote TEXT)')
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs_manipulacao (
            op_id TEXT, temp_estufa INTEGER, tempo_secagem REAL, moido_pct INTEGER, master_lote TEXT
        )''')
        cursor.execute('CREATE TABLE IF NOT EXISTS logs_ferramentaria (op_id TEXT, molde_id TEXT, limpeza TEXT)')

        # Produção
        cursor.execute('CREATE TABLE IF NOT EXISTS setups (op_id TEXT, cav_totais INTEGER, cav_ativas INTEGER, ciclo_padrao REAL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS producao (timestamp TEXT, op_id TEXT, ciclos INTEGER, pecas_boas INTEGER)')

        # Qualidade
        cursor.execute('CREATE TABLE IF NOT EXISTS inspecoes (timestamp TEXT, op_id TEXT, status TEXT, obs TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS paradas (timestamp TEXT, op_id TEXT, motivo TEXT, obs TEXT)')

        # Auditoria
        cursor.execute('CREATE TABLE IF NOT EXISTS auditorias (op_id TEXT, auditor TEXT, status TEXT, parecer TEXT, data TEXT)')

        conn.commit()

init_db()

# ================= SCHEMAS =================
class RegistroProducao(BaseModel):
    op_id: str = Field(..., example="OP123")
    ciclos: int = Field(..., gt=0, example=10)

class IARequest(BaseModel):
    msg: str

# ================= HELPERS =================
def validar_api_key(x_api_key):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Acesso negado")

def now():
    return datetime.datetime.utcnow().isoformat()

# ================= IA HELP =================
@app.post("/api/v1/ia_help")
async def ia_help(dados: IARequest):
    msg = dados.msg.lower()

    base_ia = [
        ("rechupe", "Aumentar pressão de recalque e verificar temperatura do molde."),
        ("rebarba", "Reduzir pressão de injeção ou verificar fechamento do molde."),
        ("queima", "Limpar saídas de gases e reduzir velocidade de injeção."),
        ("incompleta", "Aumentar dosagem ou temperatura do canhão."),
        ("bolha", "Verificar umidade do material e tempo de secagem."),
    ]

    for erro, solucao in base_ia:
        if erro in msg:
            return {"res": solucao}

    return {"res": "Verifique parâmetros gerais do processo e ficha técnica."}

# ================= REGISTRO PRODUÇÃO =================
@app.post("/api/v1/registrar")
async def registrar(dados: RegistroProducao, x_api_key: str = Header(None)):
    validar_api_key(x_api_key)

    try:
        with get_conn() as conn:
            cursor = conn.cursor()

            setup = cursor.execute(
                "SELECT cav_ativas FROM setups WHERE op_id=?",
                (dados.op_id,)
            ).fetchone()

            mult = setup[0] if setup else 1
            pecas = dados.ciclos * mult

            cursor.execute(
                "INSERT INTO producao VALUES (?,?,?,?)",
                (now(), dados.op_id, dados.ciclos, pecas)
            )

            conn.commit()

        return {
            "status": "OK",
            "pecas": pecas,
            "cavidades": mult
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= HEALTH CHECK =================
@app.get("/api/v1/health")
async def health():
    return {"status": "online"}

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )