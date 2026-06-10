import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(
    page_title="ZION TECNOLOGIA - LOGÍSTICA",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS Personalizada para emular a interface das imagens
st.markdown("""
    <style>
    /* Estilo global */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Top Banner */
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
        letter-spacing: 1px;
    }
    .top-banner p {
        margin: 5px 0 0 0;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #8E9AAF;
    }

    /* Meta Total Badge */
    .meta-badge {
        float: right;
        background-color: #17A2B8;
        color: white;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: bold;
        border-radius: 4px;
        margin-top: -3px;
    }

    /* Cards de Janela de Ofertas */
    .janela-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .janela-titulo {
        font-size: 11px;
        color: #718096;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .janela-horario {
        font-size: 14px;
        font-weight: bold;
        color: #007BFF;
        margin-bottom: 8px;
    }

    /* Subtítulos de Seções */
    .section-header-container {
        background-color: #343A40;
        color: white;
        padding: 8px 12px;
        border-radius: 4px 4px 0 0;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
    }
    
    .stButton>button {
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# FUNÇÕES AUXILIARES (CORREÇÃO DE ERRO DO ADOBE ACROBAT)
# ---------------------------------------------------------------------------------
def gerar_pdf_simulado():
    """Gera a estrutura binária mínima e perfeitamente válida de um arquivo PDF
    de uma página para evitar erros de corrupção ou arquivo danificado no Adobe Reader."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
    )

# ---------------------------------------------------------------------------------
# BANCO DE DADOS EM MEMÓRIA (SESSION STATE)
# ---------------------------------------------------------------------------------
if "ofertas" not in st.session_state:
    st.session_state.ofertas = [
        {"id": 1, "horario": "06:00 às 07:00", "vagas_o": 5, "cotas_o": 2},
        {"id": 2, "horario": "07:00 às 08:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 3, "horario": "08:00 às 09:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 4, "horario": "09:00 às 10:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 5, "horario": "10:00 às 11:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 6, "horario": "11:00 às 12:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 7, "horario": "12:00 às 13:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 8, "horario": "13:00 às 14:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 9, "horario": "14:00 às 15:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 10, "horario": "15:00 às 16:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 11, "horario": "16:00 às 17:00", "vagas_o": 2, "cotas_o": 0},
        {"id": 12, "horario": "17:00 às 18:00", "vagas_o": 2, "cotas_o": 0},
    ]

if "db_agendamentos" not in st.session_state:
    pdf_base = gerar_pdf_simulado()
    st.session_state.db_agendamentos = [
        {
            "balsa": "SD II",
            "data": "12/06/2026",
            "janela": "06:00 às 07:00",
            "placa": "JVV-7606",
            "veiculo": "BITREN",
            "motorista": "JOSE FRANCISCO",
            "nf": "154639",
            "volume": 51000.00,
            "produto": "ANIDRO",
            "arquivo_nome": "NF 1736.pdf",
            "conteudo_bytes": pdf_base
        },
        {
            "balsa": "SD II",
            "data": "12/06/2026",
            "janela": "06:00 às 07:00",
            "placa": "HUG-9869",
            "veiculo": "BITREN",
            "motorista": "JOSE FRANCISCO",
            "nf": "154639",
            "volume": 51000.00,
            "produto": "ANIDRO",
            "arquivo_nome": "NF 1812.pdf",
            "conteudo_bytes": pdf_base
        }
    ]

# ---------------------------------------------------------------------------------
# CABEÇALHO DO SISTEMA
# ---------------------------------------------------------------------------------
st.markdown("""
    <div class="top-banner">
        <h1>ZION TECNOLOGIA - LOGÍSTICA</h1>
        <p>Sistema de Portaria & Agendamento Logístico</p>
    </div>
""", unsafe_allow_html=True)

aba1, aba2 = st.tabs([
    "⚓ MÓDULO 1: Gestão de Disponibilidade (GD)", 
    "🚛 MÓDULO 2: Portal de Agendamento (Cliente FS)"
])

# =================================================================================
# MÓDULO 1: GESTÃO DE DISPONIBILIDADE (GD)
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1, 2])
    
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        
        balsa_gd = st.selectbox("Selecione a Embarcação", ["SD II"], key="gd_balsa")
        data_gd = st.date_input("Data de Vigência", datetime(2026, 6, 12), key="gd_data")
        exigencia_cts = st.number_input("Exigência (CTS)", min_value=0, value=25)
        hora_inicio = st.selectbox("Hora Início", ["06:00", "07:00", "08:00"])
        
        if st.button("🔴 PUBLICAR DISPONIBILIDADE", use_container_width=True):
            st.success("Disponibilidade de vagas atualizada com sucesso no sistema!")

    with col_dist:
        st.markdown(f'<div class="section-header-container">⏱️ Distribuição de Vagas por Janela <span class="meta-badge">META TOTAL: {exigencia_cts} CTS</span></div>', unsafe_allow_html=True)
        
        cols_janelas = st.columns(4)
        total_distribuido = 0
        
        for idx, of in enumerate(st.session_state.ofertas[:12]):
            col_id = idx % 4
            with cols_janelas[col_id]:
                st.markdown(f"""
                    <div class="janela-card">
                        <div class="janela-titulo">JANELA #{of['id']}</div>
                        <div class="janela-horario">{of['horario']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                vagas_atual = st.number_input(
                    "Vagas", 
                    min_value=0, 
                    value=of['vagas_o'], 
                    key=f"vaga_input_{of['id']}",
                    label_visibility="collapsed"
                )
                total_distribuido += vagas_atual

        if total_distribuido < exigencia_cts:
            st.warning(f"⚠️ ALOCAÇÃO INCOMPLETA: {total_distribuido} de {exigencia_cts} CTS distribuídos.")
        else:
            st.success(f"✅ ALOCAÇÃO CONCLUÍDA: {total_distribuido} CTS distribuídos.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Ofertas Vigentes no Sistema (Visão GD) <span style="margin-left:auto; background:#007BFF; padding:2px 8px; font-size:11px; border-radius:3px;">⚓ SD II | 🗓️ 12/06/2026 | 🎫 12 Janelas Ativas</span></div>', unsafe_allow_html=True)
    
    df_ofertas_view = pd.DataFrame(st.session_state.ofertas)
    df_ofertas_view.columns = ['IDENTIFICADOR', 'HORÁRIO DE ATENDIMENTO', 'VAGAS OFERTADAS', 'COTAS OCUPADAS']
    df_ofertas_view['VAGAS DISPONÍVEIS'] = df_ofertas_view['VAGAS OFERTADAS'] - df_ofertas_view['COTAS OCUPADAS']
    
    col_table_gd, col_btn_excluir = st.columns([5, 1])
    with col_table_gd:
        st.dataframe(df_ofertas_view, use_container_width=True, hide_index=True)
    with col_btn_excluir:
        st.button("Excluir Regra", key="btn_excluir_regra", use_container_width=True)

    # Lista de Veículos Agendados na Visão Portaria
    st.markdown('<div class="section-header-container">🗂️ VEÍCULOS AGENDADOS (Visão Geral de Portaria)</div>', unsafe_allow_html=True)
    
    if st.session_state.db_agendamentos:
        for idx, ag in enumerate(st.session_state.db_agendamentos):
            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2.5, 2, 1.5, 1.5])
            with c1:
                st.markdown(f"**BALSA:** {ag['balsa']}<br>**DATA:** {ag['data']}", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**HORÁRIO:** {ag['janela']}<br>**PLACA:** `{ag['placa']}`", unsafe_allow_html=True)
            with c3:
                st.markdown(f"**VEÍCULO:** {ag['veiculo']}<br>**MOTORISTA:** {ag['motorista']}", unsafe_allow_html=True)
            with c4:
                st.markdown(f"**Nº NF:** {ag['nf']}<br>**VOLUME:** {ag['volume']:.2f} m³", unsafe_allow_html=True)
            with c5:
                st.markdown(f"**PRODUTO:** {ag['produto']}<br>**ANEXO:** {ag['arquivo_nome']}", unsafe_allow_html=True)
            with c6:
                st.download_button(
                    label="📄 PDF",
                    data=ag.get("conteudo_bytes", gerar_pdf_simulado()),
                    file_name=ag["arquivo_nome"],
                    mime="application/pdf",
                    key=f"m1_down_portaria_{idx}",
                    use_container_width=True
                )
            st.markdown("<hr style='margin:8px 0; border:0; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum veículo agendado no momento.")

# =================================================================================
# MÓDULO 2: PORTAL DE AGENDAMENTO (CLIENTE FS)
# =================================================================================
with aba2:
    col_form, col_comp = st.columns([1, 1.3])
    
    with col_form:
        st.markdown('<div class="section-header-container">📝 Formulário de Agendamento Logístico</div>', unsafe_allow_html=True)
        
        with st.form("form_agendamento", clear_on_submit=False):
            embarcacao_sel = st.selectbox(
                "1. SELECIONE A EMBARCAÇÃO / PROGRAMAÇÃO",
                ["SD II - Vigência: 12/06/2026"]
            )
            
            opcoes_janelas = [f"Janela #{of['id']} [{of['horario']}] ({of['vagas_o'] - of['cotas_o']} vagas restantes)" for of in st.session_state.ofertas]
            janela_sel = st.selectbox("2. ESCOLHA O HORÁRIO DA JANELA", opcoes_janelas)
            
            c_placa, c_veic = st.columns(2)
            with c_placa:
                placa = st.text_input("PLACA", value="JVV-7606").upper()
            with c_veic:
                veiculo = st.text_input("VEÍCULO", value="BITREN").upper()
                
            c_mot, c_nf = st.columns(2)
            with c_mot:
                motorista = st.text_input("MOTORISTA", value="JOSE FRANCISCO").upper()
            with c_nf:
                num_nf = st.text_input("Nº NOTA FISCAL", value="154639")
                
            c_vol, c_prod = st.columns(2)
            with c_vol:
                volume = st.number_input("VOLUME M³", value=51000.00, step=100.0)
            with c_prod:
                produto = st.text_input("PRODUTO", value="ANIDRO").upper()
                
            arquivo_nf = st.file_uploader("ARQUIVO (ANEXAR NOTA FISCAL)", type=["pdf", "png", "jpg", "jpeg"])
            
            btn_confirmar = st.form_submit_button("🔒 CONFIRMAR AGENDAMENTO FS")
            
            if btn_confirmar:
                # Intercepta e guarda os bytes originais para o Adobe Acrobat ler perfeitamente
                dados_arquivo_bytes = arquivo_nf.read() if arquivo_nf is not None else gerar_pdf_simulado()
                nome_do_arquivo = arquivo_nf.name if arquivo_nf is not None else "NF_Automatica.pdf"
                horario_janela_limpo = janela_sel.split("[")[1].split("]")[0] if "[" in janela_sel else "06:00 às 07:00"
                
                novo_reg = {
                    "balsa": embarcacao_sel.split(" - ")[0],
                    "data": embarcacao_sel.split(": ")[1] if ": " in embarcacao_sel else "12/06/2026",
                    "janela": horario_janela_limpo,
                    "placa": placa,
                    "veiculo": veiculo,
                    "motorista": motorista,
                    "nf": num_nf,
                    "volume": float(volume),
                    "produto": produto,
                    "arquivo_nome": nome_do_arquivo,
                    "conteudo_bytes": dados_arquivo_bytes
                }
                
                st.session_state.db_agendamentos.append(novo_reg)
                st.success("✅ Agendamento efetuado com sucesso!")
                st.rerun()

    with col_comp:
        st.markdown('<div class="section-header-container">📜 Comprovantes de Agendamento Emitidos</div>', unsafe_allow_html=True)
        
        if st.session_state.db_agendamentos:
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                st.markdown(f"""
                <div style="background-color: #F8F9FA; border-left: 4px solid #007BFF; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
                    <span style="float: right; font-size: 11px; color: #6C757D;">📋 Registro #{idx+1}</span>
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>BALSA:</b> {ag['balsa']} | <b>DATA:</b> {ag['data']} | <b>HORÁRIO:</b> {ag['janela']}</p>
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>PLACA:</b> {ag['placa']} | <b>VEÍCULO:</b> {ag['veiculo']} | <b>MOTORISTA:</b> {ag['motorista']}</p>
                    <p style="margin: 0; font-size: 13px;"><b>Nº NF:</b> {ag['nf']} | <b>VOLUME:</b> {ag['volume']:.2f} m³ | <b>PRODUTO:</b> {ag['produto']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_edit, c_down = st.columns([1, 1])
                with c_edit:
                    if st.button(f"📝 Editar", key=f"m2_btn_edit_{idx}", use_container_width=True):
                        st.info("Formulário carregado para edição.")
                with c_down:
                    st.download_button(
                        label="📄 Baixar PDF da NF",
                        data=ag.get("conteudo_bytes", gerar_pdf_simulado()),
                        file_name=ag["arquivo_nome"],
                        mime="application/pdf",
                        key=f"m2_btn_down_{idx}",
                        use_container_width=True
                    )
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Nenhum comprovante emitido até o momento.")
