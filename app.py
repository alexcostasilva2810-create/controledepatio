import streamlit as st
import pandas as pd
from datetime import datetime
import io
from fpdf import FPDF

# Configuração da Página
st.set_page_config(
    page_title="ZION TECNOLOGIA - LOGÍSTICA",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS Personalizada para emular a interface original
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
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
        letter-spacing: 1px;
    }
    .top-banner p {
        margin: 5px 0 0 0;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #8E9AAF;
    }
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
    div[data-testid="stForm"] .stButton>button {
        background-color: #FF4D4D !important;
        color: white !important;
        border: none !important;
        width: 100%;
        font-weight: bold;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# GERADOR DE PDF REAL E VISÍVEL (CORREÇÃO DA PÁGINA EM BRANCO)
# ---------------------------------------------------------------------------------
def gerar_pdf_com_conteudo(num_nf, motorista, placa, veiculo, volume, produto):
    """Gera um PDF real com texto desenhado para não abrir em branco no Adobe Reader"""
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho do Documento
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "ZION TECNOLOGIA - COMPROVANTE DE NOTA FISCAL", ln=True, align="C")
    pdf.ln(10)
    
    # Detalhes da NF
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, f"DOCUMENTO AUXILIAR DE NOTA FISCAL: #{num_nf}", ln=True, align="L")
    pdf.line(10, 30, 200, 30)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(95, 8, f"Motorista: {motorista}", border=1)
    pdf.cell(95, 8, f"Produto: {produto}", border=1, ln=True)
    
    pdf.cell(47, 8, f"Placa: {placa}", border=1)
    pdf.cell(48, 8, f"Veiculo: {veiculo}", border=1)
    pdf.cell(95, 8, f"Volume cadastrado: {volume:.2f} m3", border=1, ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(190, 5, "Este documento e uma representacao oficial do agendamento logistico.", ln=True, align="C")
    
    return pdf.output(dest="S").encode("latin-1")

# ---------------------------------------------------------------------------------
# SESSÃO DE DADOS (SESSION STATE)
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
    ]

if "db_agendamentos" not in st.session_state:
    # Popula com PDFs iniciais que já contêm texto legível
    st.session_state.db_agendamentos = [
        {
            "balsa": "SD II", "data": "10/06/2026", "janela": "06:00 às 07:00",
            "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", "arquivo_nome": "NF_1736.pdf",
            "conteudo_bytes": gerar_pdf_com_conteudo("154639", "JOSE FRANCISCO", "JVV-7606", "BITREN", 51000.00, "ANIDRO")
        },
        {
            "balsa": "SD II", "data": "10/06/2026", "janela": "06:00 às 07:00",
            "placa": "HUG-9869", "veiculo": "BITREN", "motorista": "ANTONIO SILVA",
            "nf": "154640", "volume": 45000.00, "produto": "ANIDRO", "arquivo_nome": "NF_1812.pdf",
            "conteudo_bytes": gerar_pdf_com_conteudo("154640", "ANTONIO SILVA", "HUG-9869", "BITREN", 45000.00, "ANIDRO")
        }
    ]

# Cabeçalho do Painel
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
# MÓDULO 1: GESTÃO DE DISPONIBILIDADE
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1, 2])
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        st.selectbox("Selecione a Embarcação", ["SD II"], key="gd_balsa")
        st.date_input("Data de Vigência", datetime(2026, 6, 10), key="gd_data")
        exigencia_cts = st.number_input("Exigência (CTS)", min_value=0, value=25)
        st.selectbox("Hora Início", ["06:00", "07:00", "08:00"])
        if st.button("🔴 PUBLICAR DISPONIBILIDADE", use_container_width=True):
            st.success("Disponibilidade de vagas atualizada!")

    with col_dist:
        st.markdown(f'<div class="section-header-container">⏱️ Distribuição de Vagas <span class="meta-badge">META TOTAL: {exigencia_cts} CTS</span></div>', unsafe_allow_html=True)
        cols_janelas = st.columns(4)
        total_distribuido = 0
        for idx, of in enumerate(st.session_state.ofertas[:8]):
            col_id = idx % 4
            with cols_janelas[col_id]:
                st.markdown(f'<div class="janela-card"><div class="janela-titulo">JANELA #{of["id"]}</div><div class="janela-horario">{of["horario"]}</div></div>', unsafe_allow_html=True)
                vagas_atual = st.number_input("Vagas", min_value=0, value=of['vagas_o'], key=f"v_gd_{of['id']}", label_visibility="collapsed")
                total_distribuido += vagas_atual

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Ofertas Vigentes no Sistema (Visão GD)</div>', unsafe_allow_html=True)
    df_ofertas_view = pd.DataFrame(st.session_state.ofertas)
    df_ofertas_view.columns = ['IDENTIFICADOR', 'HORÁRIO DE ATENDIMENTO', 'VAGAS OFERTADAS', 'COTAS OCUPADAS']
    df_ofertas_view['VAGAS DISPONÍVEIS'] = df_ofertas_view['VAGAS OFERTADAS'] - df_ofertas_view['COTAS OCUPADAS']
    st.dataframe(df_ofertas_view, use_container_width=True, hide_index=True)

    # Portaria Geral
    st.markdown('<div class="section-header-container">🗂️ VEÍCULOS AGENDADOS (Visão Geral de Portaria)</div>', unsafe_allow_html=True)
    if st.session_state.db_agendamentos:
        registros_limpos = []
        for ag in st.session_state.db_agendamentos:
            registros_limpos.append({
                "BALSA": ag["balsa"], "DATA": ag["data"], "HORÁRIO": ag["janela"],
                "PLACA": ag["placa"], "VEÍCULO": ag["veiculo"], "MOTORISTA": ag["motorista"],
                "Nº NF": ag["nf"], "VOLUME": f"{float(ag['volume']):.2f} m³", "PRODUTO": ag["produto"], "ARQUIVO": ag["arquivo_nome"]
            })
        col_grid, col_botoes = st.columns([5.2, 0.8])
        with col_grid:
            st.dataframe(pd.DataFrame(registros_limpos), use_container_width=True, hide_index=True)
        with col_botoes:
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                st.download_button(
                    label="📄 PDF",
                    data=ag["conteudo_bytes"],
                    file_name=ag["arquivo_nome"],
                    mime="application/pdf",
                    key=f"m1_down_{idx}",
                    use_container_width=True
                )

# =================================================================================
# MÓDULO 2: PORTAL DE AGENDAMENTO (CLIENTE FS)
# =================================================================================
with aba2:
    col_form, col_comp = st.columns([1, 1.3])
    with col_form:
        st.markdown('<div class="section-header-container">📝 Formulário de Agendamento</div>', unsafe_allow_html=True)
        with st.form("form_agendamento"):
            st.selectbox("1. SELECIONE A EMBARCAÇÃO", ["SD II - Vigência: 10/06/2026"])
            opcoes_janelas = [f"Janela #{of['id']} [{of['horario']}]" for of in st.session_state.ofertas]
            janela_sel = st.selectbox("2. ESCOLHA O HORÁRIO DA JANELA", opcoes_janelas)
            
            c_placa, c_veic = st.columns(2)
            with c_placa: placa = st.text_input("PLACA", value="JVV-7606").upper()
            with c_veic: veiculo = st.text_input("VEÍCULO", value="BITREN").upper()
                
            c_mot, c_nf = st.columns(2)
            with c_mot: motorista = st.text_input("MOTORISTA", value="JOSE FRANCISCO").upper()
            with c_nf: num_nf = st.text_input("Nº NOTA FISCAL", value="154639")
                
            c_vol, c_prod = st.columns(2)
            with c_vol: volume = st.number_input("VOLUME M³", value=51000.00, step=1.0)
            with c_prod: produto = st.text_input("PRODUTO", value="ANIDRO").upper()
                
            arquivo_nf = st.file_uploader("ANEXAR COMPROVANTE/NF", type=["pdf", "png", "jpg", "jpeg"])
            btn_confirmar = st.form_submit_button("🔒 CONFIRMAR AGENDAMENTO FS")
            
            if btn_confirmar:
                # SE O CLIENTE ANEXOU, PEGA OS BYTES. SE NÃO, GERA UM PDF COM TEXTO DINÂMICO
                if arquivo_nf is not None:
                    dados_bytes = arquivo_nf.read()
                    nome_arq = arquivo_nf.name
                else:
                    dados_bytes = gerar_pdf_com_conteudo(num_nf, motorista, placa, veiculo, volume, produto)
                    nome_arq = f"NF_{num_nf}.pdf"
                
                horario_limpo = janela_sel.split("[")[1].split("]")[0] if "[" in janela_sel else "06:00 às 07:00"
                
                st.session_state.db_agendamentos.append({
                    "balsa": "SD II", "data": "10/06/2026", "janela": horario_limpo,
                    "placa": placa, "veiculo": veiculo, "motorista": motorista,
                    "nf": num_nf, "volume": float(volume), "produto": produto,
                    "arquivo_nome": nome_arq, "conteudo_bytes": dados_bytes
                })
                st.success("✅ Agendamento salvo com sucesso!")
                st.rerun()

    with col_comp:
        st.markdown('<div class="section-header-container">📜 Comprovantes Emitidos</div>', unsafe_allow_html=True)
        if st.session_state.db_agendamentos:
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                st.markdown(f"""
                <div style="background-color: #F8F9FA; border-left: 4px solid #007BFF; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>BALSA:</b> {ag['balsa']} | <b>DATA:</b> {ag['data']} | <b>HORÁRIO:</b> {ag['janela']}</p>
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>PLACA:</b> {ag['placa']} | <b>MOTORISTA:</b> {ag['motorista']}</p>
                    <p style="margin: 0; font-size: 13px;"><b>Nº NF:</b> {ag['nf']} | <b>VOLUME:</b> {float(ag['volume'])} m³ | <b>ANEXO:</b> {ag['arquivo_nome']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_ed, c_dw = st.columns(2)
                with c_ed: st.button("📝 Editar", key=f"m2_ed_{idx}", use_container_width=True)
                with c_dw:
                    st.download_button(
                        label="📄 Baixar PDF da NF",
                        data=ag["conteudo_bytes"],
                        file_name=ag["arquivo_nome"],
                        mime="application/pdf",
                        key=f"m2_dw_{idx}",
                        use_container_width=True
                    )
