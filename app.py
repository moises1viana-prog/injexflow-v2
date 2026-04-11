import streamlit as st
import pandas as pd
import sqlite3
import requests

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="InjexFlow 4.0 MES",
    layout="wide",
    page_icon="🏭"
)

st.markdown("## 🚀 Sistema MES Industrial em Tempo Real")

# ---------------- BANCO (OTIMIZADO) ----------------
@st.cache_resource
def get_conn():
    return sqlite3.connect('injexflow_industrial.db', check_same_thread=False)

def db_query(sql, params=(), commit=False):
    conn = get_conn()
    cur = conn.cursor()
    if commit:
        cur.execute(sql, params)
        conn.commit()
        return True
    return pd.read_sql_query(sql, conn, params=params)

# ---------------- LOGIN SIMPLES ----------------
usuarios = {
    "PCP": "123",
    "Almoxarifado": "123",
    "Manipulador": "123",
    "Ferramentaria": "123",
    "Regulador": "123",
    "Operador": "123",
    "Auditoria": "123",
    "Administração": "123"
}

if "setor" not in st.session_state:
    st.title("🏭 InjexFlow 4.0 - Login")

    setor = st.selectbox("Selecione seu Posto:", list(usuarios.keys()))
    senha = st.text_input("Senha", type="password")

    if st.button("Acessar"):
        if usuarios.get(setor) == senha:
            st.session_state.setor = setor
            st.rerun()
        else:
            st.error("Senha incorreta")

    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title(f"Posto: {st.session_state.setor}")
if st.sidebar.button("Logout"):
    del st.session_state.setor
    st.rerun()

# =====================================================
# ================== PCP ===============================
# =====================================================
if st.session_state.setor == "PCP":
    st.header("📋 Ficha de Abertura de OP")

    with st.form("pcp"):
        op = st.text_input("Código OP")
        prod = st.text_input("Produto")
        meta = st.number_input("Meta Total", value=1000)

        col1, col2 = st.columns(2)
        emb = col1.selectbox("Embalagem", ["Saco Plástico", "Caixa Papelão", "Saco + Caixa"])
        qtd_e = col2.number_input("Pçs por Embalagem", value=100)

        plano = st.text_area("Plano de Controle")

        if st.form_submit_button("Gerar e Travar OP"):
            db_query(
                """INSERT INTO ordens_producao 
                (op_codigo, produto, meta, embalagem, qtd_emb, plano_controle, status)
                VALUES (?,?,?,?,?,?,?)""",
                (op, prod, meta, emb, qtd_e, plano, "Aguardando Setup"),
                True
            )

            db_query("INSERT INTO liberacoes (op_id) VALUES (?)", (op,), True)

            st.success("OP Criada com sucesso!")

# =====================================================
# ================== ALMOX =============================
# =====================================================
elif st.session_state.setor == "Almoxarifado":
    st.header("📦 Saída de Material")

    ops = db_query("SELECT op_codigo FROM ordens_producao WHERE status='Aguardando Setup'")
    if ops.empty:
        st.warning("Nenhuma OP disponível")
        st.stop()

    op_sel = st.selectbox("OP:", ops['op_codigo'])

    with st.form("almox"):
        mat = st.text_input("Material")
        lote = st.text_input("Lote")

        if st.form_submit_button("Liberar"):
            db_query("INSERT INTO logs_almox VALUES (?,?,?)", (op_sel, mat, lote), True)
            db_query("UPDATE liberacoes SET almox=1 WHERE op_id=?", (op_sel,), True)
            st.success("Material liberado!")

# =====================================================
# ================== MANIPULAÇÃO =======================
# =====================================================
elif st.session_state.setor == "Manipulador":
    st.header("🧪 Preparação")

    ops = db_query("SELECT op_id FROM liberacoes WHERE almox=1 AND lib_manipulacao=0")
    if ops.empty:
        st.warning("Nada para preparar")
        st.stop()

    op_sel = st.selectbox("OP:", ops['op_id'])

    with st.form("manip"):
        c1, c2 = st.columns(2)
        temp = c1.number_input("Temp (°C)", value=80)
        tempo = c2.number_input("Tempo (h)", value=4.0)

        moido = st.slider("% Moído", 0, 100, 20)
        master = st.text_input("Lote Masterbatch")

        if st.form_submit_button("Liberar"):
            db_query(
                "INSERT INTO logs_manipulacao VALUES (?,?,?,?,?)",
                (op_sel, temp, tempo, moido, master),
                True
            )
            db_query("UPDATE liberacoes SET lib_manipulacao=1 WHERE op_id=?", (op_sel,), True)
            st.success("Material pronto!")

# =====================================================
# ================== FERRAMENTARIA =====================
# =====================================================
elif st.session_state.setor == "Ferramentaria":
    st.header("🔧 Molde")

    ops = db_query("SELECT op_codigo FROM ordens_producao")
    if ops.empty:
        st.warning("Sem OP")
        st.stop()

    op_sel = st.selectbox("OP:", ops['op_codigo'])

    with st.form("ferram"):
        molde = st.text_input("ID Molde")
        limp = st.checkbox("Limpo?")

        if st.form_submit_button("Liberar"):
            status = "OK" if limp else "PENDENTE"

            db_query(
                "INSERT INTO logs_ferramentaria VALUES (?,?,?)",
                (op_sel, molde, status),
                True
            )

            db_query("UPDATE liberacoes SET ferramenta=1 WHERE op_id=?", (op_sel,), True)
            st.success("Molde liberado!")

# =====================================================
# ================== REGULADOR =========================
# =====================================================
elif st.session_state.setor == "Regulador":
    st.header("⚙️ Setup")

    ops = db_query("SELECT op_codigo FROM ordens_producao")
    if ops.empty:
        st.warning("Sem OP")
        st.stop()

    op_sel = st.selectbox("OP:", ops['op_codigo'])

    lib_df = db_query("SELECT * FROM liberacoes WHERE op_id=?", (op_sel,))
    if lib_df.empty:
        st.error("Liberação não encontrada")
        st.stop()

    lib = lib_df.iloc[0]

    if lib['almox'] and lib['lib_manipulacao'] and lib['ferramenta']:
        st.success("Pode produzir")

        with st.form("setup"):
            c1, c2 = st.columns(2)
            ct = c1.number_input("Cavidades Total", value=4)
            ca = c2.number_input("Cavidades Ativas", value=4)

            if st.form_submit_button("Liberar Máquina"):
                db_query("INSERT INTO setups VALUES (?,?,?,?)", (op_sel, ct, ca, 25.0), True)
                db_query("UPDATE ordens_producao SET status='Em Produção' WHERE op_codigo=?", (op_sel,), True)
                st.success("Produção iniciada!")

    else:
        st.error("Faltam liberações")

    st.divider()

    st.subheader("🤖 IA Help")

    msg = st.text_input("Descreva defeito")

    if st.button("Consultar"):
        try:
            res = requests.post(
                "http://localhost:8000/api/v1/ia_help",
                json={"msg": msg},
                timeout=5
            ).json()

            st.warning(f"Sugestão: {res.get('res', 'Sem resposta')}")
        except:
            st.error("Erro na IA")

# =====================================================
# ================== OPERADOR ==========================
# =====================================================
elif st.session_state.setor == "Operador":
    op = db_query("SELECT * FROM ordens_producao WHERE status='Em Produção' LIMIT 1")

    if not op.empty:
        r = op.iloc[0]

        st.title(f"📲 Máquina: {r['op_codigo']}")
        st.info(f"{r['embalagem']} | {r['qtd_emb']} pçs")
        st.warning(f"Plano: {r['plano_controle']}")

        with st.expander("Parada"):
            motivo = st.selectbox("Motivo", ["Manutenção", "Material", "Qualidade"])
            obs = st.text_area("Descrição")

            if st.button("Enviar"):
                db_query(
                    "INSERT INTO paradas VALUES (datetime('now'),?,?,?)",
                    (r['op_codigo'], motivo, obs),
                    True
                )
                st.error("Parada registrada")

    else:
        st.write("Aguardando produção...")

# =====================================================
# ================== AUDITORIA =========================
# =====================================================
elif st.session_state.setor == "Auditoria":
    st.header("🔎 Auditoria")

    op_bus = st.text_input("OP:")

    if op_bus:
        st.subheader("Rastreabilidade")

        st.write("Manipulação")
        st.table(db_query("SELECT * FROM logs_manipulacao WHERE op_id=?", (op_bus,)))

        st.write("Qualidade")
        st.table(db_query("SELECT * FROM inspecoes WHERE op_id=?", (op_bus,)))

        with st.form("aud"):
            nome = st.text_input("Auditor")
            status = st.radio("Resultado", ["Aprovado", "Reprovado"])

            if st.form_submit_button("Salvar"):
                db_query(
                    "INSERT INTO auditorias VALUES (?,?,?,?,datetime('now'))",
                    (op_bus, nome, status, "OK"),
                    True
                )
                st.success("Auditoria salva")

# =====================================================
# ================== ADMIN =============================
# =====================================================
elif st.session_state.setor == "Administração":
    st.header("📊 OEE")

    ops = db_query("SELECT * FROM ordens_producao")

    for _, r in ops.iterrows():
        real_df = db_query(
            "SELECT SUM(pecas_boas) as total FROM producao WHERE op_id=?",
            (r['op_codigo'],)
        )

        real = real_df['total'][0] if not real_df.empty else 0
        real = real if real else 0

        performance = real / r['meta'] if r['meta'] else 0
        oee = performance * 100

        st.metric(
            f"OP {r['op_codigo']} - {r['produto']}",
            f"{oee:.1f}%"
        )