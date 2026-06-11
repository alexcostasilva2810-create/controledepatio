import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre no topo)
st.set_page_config(
    page_title="ZION TECNOLOGIA - LOGÍSTICA",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================================================================================
# ESPAÇO PARA CADASTRO DE FUNCIONÁRIOS (ADICIONE OU ALTERE OS USUÁRIOS AQUI)
# =================================================================================
USUARIOS_CADASTRADOS = {
    "admin": "zion123",        # Usuário: admin | Senha: zion123
    "portaria": "patio2024",   # Usuário: portaria | Senha: patio2024
    "fs_cliente": "fs01"       # Usuário: fs_cliente | Senha: fs01
}

# ---------------------------------------------------------------------------------
# CONTROLE DE SESSÃO E LOGIN
# ---------------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def realizar_login(usuario, senha):
    if usuario in USUARIOS_CADASTRADOS and USUARIOS_CADASTRADOS[usuario] == senha:
        st.session_state.autenticado = True
        st.session_state.usuario_logado = usuario
        st.rerun()
    else:
        st.error("❌ Usuário ou senha incorretos.")

def realizar_logout():
    st.session_state.autenticado = False
    st.rerun()

# ---------------------------------------------------------------------------------
# TELA DE CAPA / ABERTURA (SÓ LIBERA O SISTEMA SE AUTENTICADO)
# ---------------------------------------------------------------------------------
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Imagem Portuária Marítima Profissional de Carga e Derivados
        st.image("https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1470&auto=format&fit=crop", 
                 caption="ZION TECNOLOGIA - TERMINAL PORTUÁRIO MARÍTIMO", use_container_width=True)
        
        st.markdown("""
            <div style="background-color: #0B192C; padding: 20px; border-radius: 10px; text-align: center; color: white; font-family: sans-serif;">
                <h2 style="margin:0; padding-bottom:5px;">CONTROLE DE ACESSO</h2>
                <p style="margin:0; opacity:0.8;">Painel de Controle de Pátio e Agendamentos</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            user = st.text_input("Usuário / Funcionário")
            password = st.text_input("Senha de Acesso", type="password")
            if st.button("ACESSAR OPERAÇÃO", use_container_width=True):
                realizar_login(user, password)
    st.stop()  # Trava o script aqui, impedindo a renderização do sistema sem login

# =================================================================================
# SISTEMA PRINCIPAL INTEGRAL (MANTIDO EXATAMENTE COMO ESTAVA)
# =================================================================================

# 2. ESTILIZAÇÃO VISUAL (CSS)
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .top-banner {
        background-color: #0B192C;
        color: white;
        text-align: center;
        padding: 20px 10px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .top-banner h1 {
        margin: 0;
        font-size: 24px;
        font-weight: bold;
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
    .janela-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
        margin-bottom: 15px;
    }
    div[data-testid="stForm"] .stButton>button {
        background-color: #FF4D4D !important;
        color: white !important;
        border: none !important;
        width: 100%;
        font-weight: bold;
        padding: 10px;
    }
    .tabela-header {
        background-color: #F1F3F5;
        font-weight: bold;
        padding: 8px;
        border-bottom: 2px solid #CED4DA;
        text-align: center;
        font-size: 12px;
    }
    .tabela-linha {
        padding: 6px;
        border-bottom: 1px solid #DEE2E6;
        text-align: center;
        font-size: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS EM MEMÓRIA
if "ofertas" not in st.session_state:
    st.session_state.ofertas = [
        {"id": 1, "horario": "06:00 às 07:00", "vagas_o": 5, "cotas_o": 2},
        {"id": 2, "horario": "07:00 às 08:00", "vagas_o": 2, "cotas_o": 2},
        {"id": 3, "horario": "08:00 às 09:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 4, "horario": "09:00 às 10:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 5, "horario": "10:00 às 11:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 6, "horario": "11:00 às 12:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 7, "horario": "12:00 às 13:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 8, "horario": "13:00 às 14:00", "vagas_o": 2, "cotas_o": 0},
    ]

if "db_agendamentos" not in st.session_state:
    st.session_state.db_agendamentos = [
        {
            "id": 0, "balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00",
            "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", 
            "arquivo_nome": "Nota_Fiscal_154639.pdf", "conteudo_bytes": b"%PDF-1.4 ... dados"
        }
    ]

if "editando_id" not in st.session_state:
    st.session_state.editando_id = None

# Cabeçalho com informações de login e botão para deslogar na barra lateral
st.markdown(f"""
    <div class="top-banner">
        <h1>ZION TECNOLOGIA - LOGÍSTICA</h1>
        <p>Painel Integrado de Controle de Pátio | Operador: {st.session_state.usuario_logado.upper()}</p>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 ENCERRAR SESSÃO"):
    realizar_logout()

aba1, aba2 = st.tabs([
    "⚓ MÓDULO 1: Gestão de Disponibilidade (GD)", 
    "🚛 MÓDULO 2: Portal de Agendamento (Cliente FS)"
])

# =================================================================================
# MÓDULO 1: GESTÃO DE DISPONIBILIDADE
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1, 2])
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        st.selectbox("Selecione a Embarcação", ["SD II"], key="m1_balsa")
        st.date_input("Data de Vigência", datetime(2026, 6, 12), key="m1_data")
        exigencia_cts = st.number_input("Exigência (CTS)", min_value=0, value=25)
        if st.button("🔴 PUBLICAR DISPONIBILIDADE", use_container_width=True):
            st.success("Configuração atualizada com sucesso!")

    with col_dist:
        st.markdown(f'<div class="section-header-container">⏱️ Distribuição de Vagas</div>', unsafe_allow_html=True)
        cols_janelas = st.columns(4)
        for idx, of in enumerate(st.session_state.ofertas):
            col_id = idx % 4
            with cols_janelas[col_id]:
                st.markdown(f'<div class="janela-card"><div style="font-size:11px;color:#718096;">JANELA #{of["id"]}</div><div style="font-weight:bold;color:#007BFF;">{of["horario"]}</div></div>', unsafe_allow_html=True)
                st.number_input("Vagas", min_value=0, value=of['vagas_o'], key=f"v_m1_{of['id']}", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Ofertas Vigentes no Sistema (Linha Verde = Esgotado)</div>', unsafe_allow_html=True)
    
    df_of = pd.DataFrame(st.session_state.ofertas)
    df_of.columns = ['IDENTIFICADOR', 'HORÁRIO DE ATENDIMENTO', 'VAGAS OFERTADAS', 'COTAS OCUPADAS']
    df_of['VAGAS DISPONÍVEIS'] = df_of['VAGAS OFERTADAS'] - df_of['COTAS OCUPADAS']
    
    def aplicar_cor_vagas(row):
        return ['background-color: #D4EDDA; color: #155724; font-weight: bold;'] * len(row) if row['VAGAS DISPONÍVEIS'] <= 0 else [''] * len(row)

    st.dataframe(df_of.style.apply(aplicar_cor_vagas, axis=1), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header-container">🗂️ VEÍCULOS AGENDADOS (Visão Geral de Portaria)</div>', unsafe_allow_html=True)
    if st.session_state.db_agendamentos:
        pesos_m1 = [1.0, 1.0, 1.5, 1.0, 1.0, 1.5, 1.0, 1.0, 1.0, 1.2]
        c_m1 = st.columns(pesos_m1)
        c_m1[0].markdown('<div class="tabela-header">BALSA</div>', unsafe_allow_html=True)
        c_m1[1].markdown('<div class="tabela-header">DATA</div>', unsafe_allow_html=True)
        c_m1[2].markdown('<div class="tabela-header">HORÁRIO</div>', unsafe_allow_html=True)
        c_m1[3].markdown('<div class="tabela-header">PLACA</div>', unsafe_allow_html=True)
        c_m1[4].markdown('<div class="tabela-header">VEÍCULO</div>', unsafe_allow_html=True)
        c_m1[5].markdown('<div class="tabela-header">MOTORISTA</div>', unsafe_allow_html=True)
        c_m1[6].markdown('<div class="tabela-header">Nº NF</div>', unsafe_allow_html=True)
        c_m1[7].markdown('<div class="tabela-header">VOLUME</div>', unsafe_allow_html=True)
        c_m1[8].markdown('<div class="tabela-header">PRODUTO</div>', unsafe_allow_html=True)
        c_m1[9].markdown('<div class="tabela-header">NF (PDF)</div>', unsafe_allow_html=True)
        
        for idx, ag in enumerate(st.session_state.db_agendamentos):
            l_m1 = st.columns(pesos_m1)
            l_m1[0].markdown(f'<div class="tabela-linha">{ag.get("balsa")}</div>', unsafe_allow_html=True)
            l_m1[1].markdown(f'<div class="tabela-linha">{ag.get("data")}</div>', unsafe_allow_html=True)
            l_m1[2].markdown(f'<div class="tabela-linha">{ag.get("janela")}</div>', unsafe_allow_html=True)
            l_m1[3].markdown(f'<div class="tabela-linha">{ag.get("placa")}</div>', unsafe_allow_html=True)
            l_m1[4].markdown(f'<div class="tabela-linha">{ag.get("veiculo")}</div>', unsafe_allow_html=True)
            l_m1[5].markdown(f'<div class="tabela-linha">{ag.get("motorista")}</div>', unsafe_allow_html=True)
            l_m1[6].markdown(f'<div class="tabela-linha">{ag.get("nf")}</div>', unsafe_allow_html=True)
            l_m1[7].markdown(f'<div class="tabela-linha">{float(ag.get("volume", 0)):.2f}</div>', unsafe_allow_html=True)
            l_m1[8].markdown(f'<div class="tabela-linha">{ag.get("produto")}</div>', unsafe_allow_html=True)
            l_m1[9].download_button(
                label="📄 Abrir NF",
                data=ag.get("conteudo_bytes", b""),
                file_name=ag.get("arquivo_nome", "NF.pdf"),
                mime="application/pdf",
                key=f"m1_pdf_view_{idx}",
                use_container_width=True
            )

# =================================================================================
# MÓDULO 2: PORTAL DE AGENDAMENTO (VISÃO HORIZONTAL COMPLETA COM EDICÃO)
# =================================================================================
with aba2:
    col_cadastro, col_tabela_fs = st.columns([1, 2.5])
    with col_cadastro:
        st.markdown('<div class="section-header-container">📝 Novo Agendamento Logístico</div>', unsafe_allow_html=True)
        with st.form("form_novo_agendamento", clear_on_submit=True):
            st.selectbox("1. SELECIONE A EMBARCAÇÃO / PROGRAMAÇÃO", ["SD II - Vigência: 12/06/2026"])
            
            opcoes_seletor = []
            for of in st.session_state.ofertas:
                restantes = of['vagas_o'] - of['cotas_o']
                status_texto = f"({restantes} vagas)" if restantes > 0 else "(ESGOTADA)"
                opcoes_seletor.append(f"Janela #{of['id']} [{of['horario']}] {status_texto}")
                
            janela_selecionada = st.selectbox("2. ESCOLHA O HORÁRIO DA JANELA", opcoes_seletor)
            
            c_pl, c_ve = st.columns(2)
            with c_pl: placa_in = st.text_input("PLACA", value="JVV-7606").upper()
            with c_ve: veiculo_in = st.text_input("VEÍCULO", value="BITREN").upper()
                
            c_mo, c_nf = st.columns(2)
            with c_mo: motorista_in = st.text_input("MOTORISTA", value="JOSE FRANCISCO").upper()
            with c_nf: nf_in = st.text_input("Nº NOTA FISCAL", value="154639")
                
            c_vo, c_pr = st.columns(2)
            with c_vo: volume_in = st.number_input("VOLUME M³", value=51000.00, step=0.01)
            with c_pr: produto_in = st.text_input("PRODUTO", value="ANIDRO").upper()
                
            arq_upload = st.file_uploader("ARQUIVO (ANEXAR NOTA FISCAL EM PDF)", type=["pdf"])
            submetido = st.form_submit_button("🔒 CONFIRMAR AGENDAMENTO FS")
            
            if submetido:
                id_janela_sel = int(janela_selecionada.split("#")[1].split(" ")[0])
                index_janela = next((index for (index, d) in enumerate(st.session_state.ofertas) if d["id"] == id_janela_sel), None)
                vagas_restantes = st.session_state.ofertas[index_janela]['vagas_o'] - st.session_state.ofertas[index_janela]['cotas_o']
                
                if vagas_restantes <= 0:
                    st.error("❌ Erro: Esta janela horária está esgotada!")
                else:
                    st.session_state.ofertas[index_janela]['cotas_o'] += 1
                    janela_limpa = st.session_state.ofertas[index_janela]['horario']
                    
                    if arq_upload is not None:
                        nome_documento = arq_upload.name
                        binario_doc = arq_upload.read()
                    else:
                        nome_documento = f"Nota_{nf_in}.pdf"
                        binario_doc = b"%PDF-1.4 ... (Sem arquivo enviado)"
                    
                    novo_id = len(st.session_state.db_agendamentos)
                    st.session_state.db_agendamentos.append({
                        "id": novo_id, "balsa": "SD II", "data": "12/06/2026", "janela": janela_limpa,
                        "placa": placa_in, "veiculo": veiculo_in, "motorista": motorista_in,
                        "nf": nf_in, "volume": float(volume_in), "produto": produto_in,
                        "arquivo_nome": nome_documento, "conteudo_bytes": binario_doc
                    })
                    st.success("✅ Agendamento registrado com sucesso!")
                    st.rerun()

    with col_tabela_fs:
        st.markdown('<div class="section-header-container">📋 VEÍCULOS AGENDADOS FS (Visão de Tabela Horizontal)</div>', unsafe_allow_html=True)
        pesos_colunas = [1.2, 1.2, 1.6, 1.2, 1.2, 1.8, 1.2, 1.2, 1.0]
        
        c = st.columns(pesos_colunas)
        c[0].markdown('<div class="tabela-header">BALSA</div>', unsafe_allow_html=True)
        c[1].markdown('<div class="tabela-header">DATA</div>', unsafe_allow_html=True)
        c[2].markdown('<div class="tabela-header">HORÁRIO</div>', unsafe_allow_html=True)
        c[3].markdown('<div class="tabela-header">PLACA</div>', unsafe_allow_html=True)
        c[4].markdown('<div class="tabela-header">VEÍCULO</div>', unsafe_allow_html=True)
        c[5].markdown('<div class="tabela-header">MOTORISTA</div>', unsafe_allow_html=True)
        c[6].markdown('<div class="tabela-header">Nº NF</div>', unsafe_allow_html=True)
        c[7].markdown('<div class="tabela-header">VOLUME</div>', unsafe_allow_html=True)
        c[8].markdown('<div class="tabela-header">AÇÃO</div>', unsafe_allow_html=True)
        
        for idx, ag in enumerate(st.session_state.db_agendamentos):
            l = st.columns(pesos_colunas)
            
            if st.session_state.editando_id == ag["id"]:
                balsa_ed = l[0].text_input("Balsa", value=ag["balsa"], key=f"b_ed_{idx}", label_visibility="collapsed")
                data_ed = l[1].text_input("Data", value=ag["data"], key=f"d_ed_{idx}", label_visibility="collapsed")
                janela_ed = l[2].text_input("Janela", value=ag["janela"], key=f"j_ed_{idx}", label_visibility="collapsed")
                placa_ed = l[3].text_input("Placa", value=ag["placa"], key=f"p_ed_{idx}", label_visibility="collapsed").upper()
                veiculo_ed = l[4].text_input("Veículo", value=ag["veiculo"], key=f"v_ed_{idx}", label_visibility="collapsed").upper()
                motorista_ed = l[5].text_input("Motorista", value=ag["motorista"], key=f"m_ed_{idx}", label_visibility="collapsed").upper()
                nf_ed = l[6].text_input("NF", value=ag["nf"], key=f"n_ed_{idx}", label_visibility="collapsed")
                volume_ed = l[7].number_input("Vol", value=float(ag["volume"]), key=f"vo_ed_{idx}", label_visibility="collapsed", step=0.01)
                
                if l[8].button("💾", key=f"btn_salvar_{idx}", use_container_width=True):
                    st.session_state.db_agendamentos[idx].update({
                        "balsa": balsa_ed, "data": data_ed, "janela": janela_ed,
                        "placa": placa_ed, "veiculo": veiculo_ed, "motorista": motorista_ed,
                        "nf": nf_ed, "volume": volume_ed
                    })
                    st.session_state.editando_id = None
                    st.toast("Alterações salvas!")
                    st.rerun()
            else:
                l[0].markdown(f'<div class="tabela-linha">{ag.get("balsa")}</div>', unsafe_allow_html=True)
                l[1].markdown(f'<div class="tabela-linha">{ag.get("data")}</div>', unsafe_allow_html=True)
                l[2].markdown(f'<div class="tabela-linha">{ag.get("janela")}</div>', unsafe_allow_html=True)
                l[3].markdown(f'<div class="tabela-linha">{ag.get("placa")}</div>', unsafe_allow_html=True)
                l[4].markdown(f'<div class="tabela-linha">{ag.get("veiculo")}</div>', unsafe_allow_html=True)
                l[5].markdown(f'<div class="tabela-linha">{ag.get("motorista")}</div>', unsafe_allow_html=True)
                l[6].markdown(f'<div class="tabela-linha">{ag.get("nf")}</div>', unsafe_allow_html=True)
                l[7].markdown(f'<div class="tabela-linha">{float(ag.get("volume", 0)):.2f}</div>', unsafe_allow_html=True)
                
                if l[8].button("✏️", key=f"btn_editar_{idx}", use_container_width=True):
                    st.session_state.editando_id = ag["id"]
                    st.rerun()
