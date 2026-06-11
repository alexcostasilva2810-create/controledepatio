import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="ZION TECNOLOGIA - LOGÍSTICA",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    /* Estilo para simular o cabeçalho de tabela no Módulo 2 */
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

# ---------------------------------------------------------------------------------
# 3. BANCO DE DADOS EM MEMÓRIA (SESSION STATE)
# ---------------------------------------------------------------------------------
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
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", "arquivo_nome": "Exemplo_NF.pdf"
        }
    ]

if "editando_id" not in st.session_state:
    st.session_state.editando_id = None

# Cabeçalho do Painel
st.markdown("""
    <div class="top-banner">
        <h1>ZION TECNOLOGIA - LOGÍSTICA</h1>
        <p>Painel Integrado de Controle de Pátio e Fluxo de Vagas</p>
    </div>
""", unsafe_allow_html=True)

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
        registros_m1 = []
        for ag in st.session_state.db_agendamentos:
            registros_m1.append({
                "BALSA": ag["balsa"], "DATA": ag["data"], "HORÁRIO": ag["janela"],
                "PLACA": ag["placa"], "VEÍCULO": ag["veiculo"], "MOTORISTA": ag["motorista"],
                "Nº NF": ag["nf"], "VOLUME": f"{float(ag['volume']):.2f} m³", "PRODUTO": ag["produto"], "NOME DO ARQUIVO": ag["arquivo_nome"]
            })
        st.dataframe(pd.DataFrame(registros_m1), use_container_width=True, hide_index=True)

# =================================================================================
# MÓDULO 2: PORTAL DE AGENDAMENTO (VISÃO HORIZONTAL CORRIGIDA)
# =================================================================================
with aba2:
    # Mantemos o formulário de cadastro no topo ou na lateral esquerda
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
                    nome_documento = arq_upload.name if arq_upload is not None else "N/A"
                    
                    novo_id = len(st.session_state.db_agendamentos)
                    st.session_state.db_agendamentos.append({
                        "id": novo_id, "balsa": "SD II", "data": "12/06/2026", "janela": janela_limpa,
                        "placa": placa_in, "veiculo": veiculo_in, "motorista": motorista_in,
                        "nf": nf_in, "volume": float(volume_in), "produto": produto_in,
                        "arquivo_nome": nome_documento
                    })
                    st.success("✅ Agendamento registrado!")
                    st.rerun()

    # CONFIGURAÇÃO VISUAL EM TABELA HORIZONTAL SOLICITADA
    with col_tabela_fs:
        st.markdown('<div class="section-header-container">📋 VEÍCULOS AGENDADOS FS (Visão de Tabela Horizontal)</div>', unsafe_allow_html=True)
        
        # Desenho do Cabeçalho da Tabela
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([1.2, 1.2, 1.6, 1.2, 1.2, 1.8, 1.2, 1.4, 1.2])
        c1.markdown('<div class="tabela-header">BALSA</div>', unsafe_allow_html=True)
        c2.markdown('<div class="tabela-header">DATA</div>', unsafe_allow_html=True)
        c3.markdown('<div class="tabela-header">HORÁRIO</div>', unsafe_allow_html=True)
        c4.markdown('<div class="tabela-header">PLACA</div>', unsafe_allow_html=True)
        c5.markdown('<div class="tabela-header">VEÍCULO</div>', unsafe_allow_html=True)
        c6.markdown('<div class="tabela-header">MOTORISTA</div>', unsafe_allow_html=True)
        c7.markdown('<div class="tabela-header">Nº NF</div>', unsafe_allow_html=True)
        c8.markdown('<div class="tabela-header">VOLUME</div>', unsafe_allow_html=True)
        c9.markdown('<div class="tabela-header">AÇÃO</div>', unsafe_allow_html=True)
        
        # Renderização das Linhas da Tabela
        for idx, ag in enumerate(st.session_state.db_agendamentos):
            # Cria um escopo de colunas para cada linha de registro
            l1, l2, l3, l4, l5, l6, l7, l8, l9 = st.columns([1.2, 1.2, 1.6, 1.2, 1.2, 1.8, 1.2, 1.4, 1.2])
            
            # Modo de Edição Ativo para esta linha específica
            if st.session_state.editando_id == ag["id"]:
                balsa_ed = l1.text_input("Balsa", value=ag["balsa"], key=f"b_ed_{idx}", label_visibility="collapsed")
                data_ed = l2.text_input("Data", value=ag["data"], key=f"d_ed_{idx}", label_visibility="collapsed")
                janela_ed = l3.text_input("Janela", value=ag["janela"], key=f"j_ed_{idx}", label_visibility="collapsed")
                placa_ed = l4.text_input("Placa", value=ag["placa"], key=f"p_ed_{idx}", label_visibility="collapsed").upper()
                veiculo_ed = l5.text_input("Veículo", value=ag["veiculo"], key=f"v_ed_{idx}", label_visibility="collapsed").upper()
                motorista_ed = l6.text_input("Motorista", value=ag["motorista"], key=f"m_ed_{idx}", label_visibility="collapsed").upper()
                nf_ed = l7.text_input("NF", value=ag["nf"], key=f"n_ed_{idx}", label_visibility="collapsed")
                volume_ed = l8.number_input("Vol", value=float(ag["volume"]), key=f"vo_ed_{idx}", label_visibility="collapsed", step=0.01)
                
                # Botão do Disquete para Salvar
                if l9.button("💾", key=f"btn_salvar_{idx}", use_container_width=True, help="Salvar Alterações"):
                    st.session_state.db_agendamentos[idx].update({
                        "balsa": balsa_ed, "data": data_ed, "janela": janela_ed,
                        "placa": placa_ed, "veiculo": veiculo_ed, "motorista": motorista_ed,
                        "nf": nf_ed, "volume": volume_ed
                    })
                    st.session_state.editando_id = None
                    st.toast("Alterações salvas com sucesso!")
                    st.rerun()
                    
            # Modo de Visualização Normal
            else:
                l1.markdown(f'<div class="tabela-linha">{ag["balsa"]}</div>', unsafe_allow_html=True)
                l2.markdown(f'<div class="tabela-linha">{ag["data"]}</div>', unsafe_allow_html=True)
                l3.markdown(f'<div class="tabela-linha">{ag["janela"]}</div>', unsafe_allow_html=True)
                l4.markdown(f'<div class="tabela-linha">{ag["placa"]}</div>', unsafe_allow_html=True)
                l5.markdown(f'<div class="tabela-linha">{ag["veiculo"]}</div>', unsafe_allow_html=True)
                l6.markdown(f'<div class="tabela-linha">{ag["motorista"]}</div>', unsafe_allow_html=True)
                l7.markdown(f'<div class="tabela-linha">{ag["nf"]}</div>', unsafe_allow_html=True)
                l8.markdown(f'<div class="tabela-linha">{float(ag["volume"]):.2f}</div>', unsafe_allow_html=True)
                
                # Botão da Canetinha para Editar
                if l9.button("✏️", key=f"btn_editar_{idx}", use_container_width=True, help="Editar Registro"):
                    st.session_state.editando_id = ag["id"]
                    st.rerun()
