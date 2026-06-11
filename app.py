import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre no topo)
st.set_page_config(
    page_title="ZION TECNOLOGIA - ACESSO",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================================================================================
# 2. ESPAÇO PARA CADASTRO DE FUNCIONÁRIOS (ADICIONE NOVOS AQUI)
# =================================================================================
USUARIOS_CADASTRADOS = {
    "admin": "zion123",        # Usuário: admin | Senha: zion123
    "portaria": "pátio2024",   # Usuário: portaria | Senha: pátio2024
    "gerente": "logistica",    # Usuário: gerente | Senha: logistica
    "fs_cliente": "fs01"       # Usuário: fs_cliente | Senha: fs01
}

# ---------------------------------------------------------------------------------
# 3. CONTROLE DE SESSÃO E LOGIN
# ---------------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def realizar_login(usuario, senha):
    if usuario in USUARIOS_CADASTRADOS and USUARIOS_CADASTRADOS[usuario] == senha:
        st.session_state.autenticado = True
        st.session_state.usuario_logado = usuario
        st.rerun()
    else:
        st.error("Usuário ou senha incorretos.")

def realizar_logout():
    st.session_state.autenticado = False
    st.rerun()

# ---------------------------------------------------------------------------------
# 4. TELA DE ABERTURA (LOGIN)
# ---------------------------------------------------------------------------------
if not st.session_state.autenticado:
    # Centralizar a tela de login
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Imagem Portuária Profissional
        st.image("https://images.unsplash.com/photo-1578575437130-527eed3abbec?q=80&w=1470&auto=format&fit=crop", 
                 caption="ZION TECNOLOGIA - TERMINAL LOGÍSTICO", use_container_width=True)
        
        st.markdown("""
            <div style="background-color: #0B192C; padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h2>ACESSO AO SISTEMA DE PÁTIO</h2>
                <p>Insira suas credenciais para continuar</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            user = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            if st.button("ENTRAR NO SISTEMA", use_container_width=True):
                realizar_login(user, password)
    st.stop() # Interrompe o código aqui até logar

# =================================================================================
# 5. CÓDIGO DO SISTEMA (SÓ APARECE APÓS LOGIN)
# =================================================================================

# Estilização CSS (Mantida do código anterior)
st.markdown("""
    <style>
    .top-banner {
        background-color: #0B192C;
        color: white;
        text-align: center;
        padding: 15px 10px;
        border-radius: 4px;
        margin-bottom: 20px;
        position: relative;
    }
    .logout-btn {
        position: absolute;
        right: 20px;
        top: 20px;
    }
    .section-header-container {
        background-color: #343A40;
        color: white;
        padding: 8px 12px;
        border-radius: 4px 4px 0 0;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    .tabela-header { background-color: #F1F3F5; font-weight: bold; padding: 8px; border-bottom: 2px solid #CED4DA; text-align: center; font-size: 11px; }
    .tabela-linha { padding: 6px; border-bottom: 1px solid #DEE2E6; text-align: center; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# Banner com botão de Logout
st.markdown(f"""
    <div class="top-banner">
        <h1>ZION TECNOLOGIA - LOGÍSTICA</h1>
        <p>Usuário Logado: {st.session_state.usuario_logado.upper()}</p>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 ENCERRAR SESSÃO"):
    realizar_logout()

# --- INICIALIZAÇÃO DE DADOS (Preservando sua lógica de agendamentos e PDFs) ---
if "ofertas" not in st.session_state:
    st.session_state.ofertas = [
        {"id": 1, "horario": "06:00 às 07:00", "vagas_o": 5, "cotas_o": 2},
        {"id": 2, "horario": "07:00 às 08:00", "vagas_o": 2, "cotas_o": 2},
        {"id": 3, "horario": "08:00 às 09:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 4, "horario": "09:00 às 10:00", "vagas_o": 2, "cotas_o": 0}
    ]

if "db_agendamentos" not in st.session_state:
    st.session_state.db_agendamentos = [
        {
            "id": 0, "balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00",
            "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", 
            "arquivo_nome": "Nota_Fiscal_154639.pdf", "conteudo_bytes": b"PDF_DATA"
        }
    ]

if "editando_id" not in st.session_state:
    st.session_state.editando_id = None

# --- NAVEGAÇÃO DOS MÓDULOS ---
aba1, aba2 = st.tabs(["⚓ MÓDULO 1: Gestão de Disponibilidade (GD)", "🚛 MÓDULO 2: Portal de Agendamento (Cliente FS)"])

# =================================================================================
# MÓDULO 1 (SISTEMA GD)
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1, 2])
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        st.selectbox("Selecione a Embarcação", ["SD II"], key="m1_balsa")
        st.date_input("Data de Vigência", datetime(2026, 6, 12), key="m1_data")
        if st.button("🔴 PUBLICAR DISPONIBILIDADE"): st.success("Atualizado!")

    with col_dist:
        st.markdown('<div class="section-header-container">📋 Fluxo de Vagas</div>', unsafe_allow_html=True)
        df_of = pd.DataFrame(st.session_state.ofertas)
        df_of['VAGAS DISPONÍVEIS'] = df_of['vagas_o'] - df_of['cotas_o']
        def aplicar_cor(row):
            return ['background-color: #D4EDDA;'] * len(row) if row['VAGAS DISPONÍVEIS'] <= 0 else [''] * len(row)
        st.dataframe(df_of.style.apply(aplicar_cor, axis=1), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header-container">🗂️ VEÍCULOS AGENDADOS (VISUALIZAR NF)</div>', unsafe_allow_html=True)
    if st.session_state.db_agendamentos:
        pesos_m1 = [1, 1, 1.5, 1, 1, 1.5, 1, 1, 1.2]
        cols = st.columns(pesos_m1)
        headers = ["BALSA", "DATA", "HORÁRIO", "PLACA", "VEÍCULO", "MOTORISTA", "NF", "VOL", "PDF"]
        for i, h in enumerate(headers): cols[i].markdown(f'<div class="tabela-header">{h}</div>', unsafe_allow_html=True)
        
        for idx, ag in enumerate(st.session_state.db_agendamentos):
            l = st.columns(pesos_m1)
            l[0].markdown(f'<div class="tabela-linha">{ag["balsa"]}</div>', unsafe_allow_html=True)
            l[1].markdown(f'<div class="tabela-linha">{ag["data"]}</div>', unsafe_allow_html=True)
            l[2].markdown(f'<div class="tabela-linha">{ag["janela"]}</div>', unsafe_allow_html=True)
            l[3].markdown(f'<div class="tabela-linha">{ag["placa"]}</div>', unsafe_allow_html=True)
            l[4].markdown(f'<div class="tabela-linha">{ag["veiculo"]}</div>', unsafe_allow_html=True)
            l[5].markdown(f'<div class="tabela-linha">{ag["motorista"]}</div>', unsafe_allow_html=True)
            l[6].markdown(f'<div class="tabela-linha">{ag["nf"]}</div>', unsafe_allow_html=True)
            l[7].markdown(f'<div class="tabela-linha">{ag["volume"]}</div>', unsafe_allow_html=True)
            l[8].download_button("📄 Ver", data=ag["conteudo_bytes"], file_name=ag["arquivo_nome"], key=f"m1_pdf_{idx}", use_container_width=True)

# =================================================================================
# MÓDULO 2 (PORTAL CLIENTE FS)
# =================================================================================
with aba2:
    col_cad, col_tab = st.columns([1, 2.5])
    with col_cad:
        st.markdown('<div class="section-header-container">📝 Novo Agendamento</div>', unsafe_allow_html=True)
        with st.form("form_fs"):
            janela_sel = st.selectbox("Escolha a Janela", [f"Janela #{o['id']} [{o['horario']}]" for o in st.session_state.ofertas])
            placa = st.text_input("PLACA").upper()
            motorista = st.text_input("MOTORISTA").upper()
            num_nf = st.text_input("Nº NF")
            arquivo = st.file_uploader("Upload NF (PDF)", type=["pdf"])
            if st.form_submit_button("CONFIRMAR AGENDAMENTO"):
                st.success("Agendamento Realizado!")

    with col_tab:
        st.markdown('<div class="section-header-container">📋 MEUS AGENDAMENTOS (EDIÇÃO ✏️ / SALVAR 💾)</div>', unsafe_allow_html=True)
        pesos_fs = [1.2, 1.2, 1.6, 1.2, 1.2, 1.8, 1.2, 1.2, 1.0]
        c_fs = st.columns(pesos_fs)
        h_fs = ["BALSA", "DATA", "JANELA", "PLACA", "VEÍCULO", "MOTORISTA", "NF", "VOL", "AÇÃO"]
        for i, h in enumerate(h_fs): c_fs[i].markdown(f'<div class="tabela-header">{h}</div>', unsafe_allow_html=True)

        for idx, ag in enumerate(st.session_state.db_agendamentos):
            l = st.columns(pesos_fs)
            if st.session_state.editando_id == ag["id"]:
                # Modo Edição
                placa_ed = l[3].text_input("P", ag["placa"], key=f"pl_{idx}", label_visibility="collapsed")
                mot_ed = l[5].text_input("M", ag["motorista"], key=f"mt_{idx}", label_visibility="collapsed")
                if l[8].button("💾", key=f"sv_{idx}"):
                    st.session_state.db_agendamentos[idx]["placa"] = placa_ed
                    st.session_state.db_agendamentos[idx]["motorista"] = mot_ed
                    st.session_state.editando_id = None
                    st.rerun()
            else:
                # Modo Visualização
                l[0].markdown(f'<div class="tabela-linha">{ag["balsa"]}</div>', unsafe_allow_html=True)
                l[1].markdown(f'<div class="tabela-linha">{ag["data"]}</div>', unsafe_allow_html=True)
                l[2].markdown(f'<div class="tabela-linha">{ag["janela"]}</div>', unsafe_allow_html=True)
                l[3].markdown(f'<div class="tabela-linha">{ag["placa"]}</div>', unsafe_allow_html=True)
                l[4].markdown(f'<div class="tabela-linha">{ag["veiculo"]}</div>', unsafe_allow_html=True)
                l[5].markdown(f'<div class="tabela-linha">{ag["motorista"]}</div>', unsafe_allow_html=True)
                l[6].markdown(f'<div class="tabela-linha">{ag["nf"]}</div>', unsafe_allow_html=True)
                l[7].markdown(f'<div class="tabela-linha">{ag["volume"]}</div>', unsafe_allow_html=True)
                if l[8].button("✏️", key=f"ed_{idx}"):
                    st.session_state.editando_id = ag["id"]
                    st.rerun()
