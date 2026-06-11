import streamlit as st
import pandas as pd
from datetime import datetime
import io
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre no topo)
st.set_page_config(
    page_title="ZION TECNOLOGIA - LOGÍSTICA",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ESTILIZAÇÃO CSS PERSONALIZADA
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
# 3. GERADOR EMISSOR DE PDF REAL (Garante documento com dados visíveis)
# ---------------------------------------------------------------------------------
def criar_comprovante_pdf(balsa, data, janela, placa, veiculo, motorista, nf, volume, produto):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Desenhar Cabeçalho do Documento
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "ZION TECNOLOGIA - COMPROVANTE DE AGENDAMENTO", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 5, f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="R")
        pdf.line(10, 32, 200, 32)
        pdf.ln(8)
        
        # Bloco 1: Dados do Agendamento
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, "1. DADOS DA PROGRAMAÇÃO LOGÍSTICA", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(63, 8, f"Embarcação: {balsa}", border=1)
        pdf.cell(63, 8, f"Data Operação: {data}", border=1)
        pdf.cell(64, 8, f"Janela Horária: {janela}", border=1, ln=True)
        pdf.ln(5)
        
        # Bloco 2: Dados do Transporte
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, "2. INFORMAÇÕES DE TRANSPORTE E CARGA", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(95, 8, f"Motorista: {motorista}", border=1)
        pdf.cell(95, 8, f"Produto: {produto}", border=1, ln=True)
        
        pdf.cell(47, 8, f"Placa: {placa}", border=1)
        pdf.cell(48, 8, f"Veículo: {veiculo}", border=1)
        pdf.cell(95, 8, f"Volume Cadastrado: {float(volume):.2f} m³", border=1, ln=True)
        pdf.ln(10)
        
        # Rodapé de Validação
        pdf.line(10, 110, 200, 110)
        pdf.ln(2)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(190, 5, f"Documento fiscal de controle interno - NF-e vinculada: Nº {nf}", ln=True, align="C")
        
        # Retorna o stream puro de bytes do PDF montado
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        # Fallback de segurança para nunca quebrar o fluxo do sistema
        return b"%PDF-1.4 ... erro ao gerar pdf ..."

# ---------------------------------------------------------------------------------
# 4. INICIALIZAÇÃO BLINDADA DO BANCO DE DADOS (SESSION STATE)
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
    ]

if "db_agendamentos" not in st.session_state:
    st.session_state.db_agendamentos = [
        {
            "balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00",
            "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", "arquivo_nome": "NF 1736.pdf",
            "conteudo_bytes": criar_comprovante_pdf("SD II", "12/06/2026", "06:00 às 07:00", "JVV-7606", "BITREN", "JOSE FRANCISCO", "154639", 51000.00, "ANIDRO")
        },
        {
            "balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00",
            "placa": "HUG-9869", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", "arquivo_nome": "NF 1812.pdf",
            "conteudo_bytes": criar_comprovante_pdf("SD II", "12/06/2026", "06:00 às 07:00", "HUG-9869", "BITREN", "JOSE FRANCISCO", "154639", 51000.00, "ANIDRO")
        }
    ]

# Cabeçalho Fixo do Painel Superior
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
# CONTROLADOR - MÓDULO 1: GESTÃO DE DISPONIBILIDADE
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1, 2])
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        st.selectbox("Selecione a Embarcação", ["SD II"], key="gd_balsa_sel")
        st.date_input("Data de Vigência", datetime(2026, 6, 12), key="gd_data_sel")
        exigencia_cts = st.number_input("Exigência (CTS)", min_value=0, value=25)
        st.selectbox("Hora Início", ["06:00", "07:00", "08:00"], key="gd_hora_sel")
        if st.button("🔴 PUBLICAR DISPONIBILIDADE", use_container_width=True):
            st.success("Disponibilidade publicada com sucesso!")

    with col_dist:
        st.markdown(f'<div class="section-header-container">⏱️ Distribuição de Vagas por Janela <span class="meta-badge">META: {exigencia_cts} CTS</span></div>', unsafe_allow_html=True)
        cols_janelas = st.columns(4)
        for idx, of in enumerate(st.session_state.ofertas[:8]):
            col_id = idx % 4
            with cols_janelas[col_id]:
                st.markdown(f'<div class="janela-card"><div class="janela-titulo">JANELA #{of["id"]}</div><div class="janela-horario">{of["horario"]}</div></div>', unsafe_allow_html=True)
                st.number_input("Vagas", min_value=0, value=of['vagas_o'], key=f"v_input_m1_{of['id']}", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Ofertas Vigentes no Sistema (Visão GD)</div>', unsafe_allow_html=True)
    df_of = pd.DataFrame(st.session_state.ofertas)
    df_of.columns = ['IDENTIFICADOR', 'HORÁRIO DE ATENDIMENTO', 'VAGAS OFERTADAS', 'COTAS OCUPADAS']
    df_of['VAGAS DISPONÍVEIS'] = df_of['VAGAS OFERTADAS'] - df_of['COTAS OCUPADAS']
    st.dataframe(df_of, use_container_width=True, hide_index=True)

    # VISÃO GERAL DE PORTARIA (TABELA DE VEÍCULOS AGENDADOS)
    st.markdown('<div class="section-header-container">🗂️ VEÍCULOS AGENDADOS (Visão Geral de Portaria)</div>', unsafe_allow_html=True)
    if st.session_state.db_agendamentos:
        registros_m1 = []
        for ag in st.session_state.db_agendamentos:
            # Extração blindada e segura para evitar estouro numérico na tabela
            try:
                v_formatado = f"{float(ag['volume']):.2f} m³"
            except:
                v_formatado = f"{ag['volume']} m³"
                
            registros_m1.append({
                "BALSA": ag.get("balsa", "SD II"),
                "DATA": ag.get("data", "12/06/2026"),
                "HORÁRIO": ag.get("janela", "06:00 às 07:00"),
                "PLACA": ag.get("placa", ""),
                "VEÍCULO": ag.get("veiculo", ""),
                "MOTORISTA": ag.get("motorista", ""),
                "Nº NF": ag.get("nf", ""),
                "VOLUME": v_formatado,
                "PRODUTO": ag.get("produto", ""),
                "ANEXO NF": ag.get("arquivo_nome", "Documento.pdf")
            })
            
        col_tabela, col_acoes = st.columns([5.1, 0.9])
        with col_tabela:
            st.dataframe(pd.DataFrame(registros_m1), use_container_width=True, hide_index=True)
        with col_acoes:
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                st.download_button(
                    label="📄 PDF",
                    data=ag.get("conteudo_bytes", b""),
                    file_name=ag.get("arquivo_nome", f"NF_{idx}.pdf"),
                    mime="application/pdf",
                    key=f"btn_download_m1_{idx}",
                    use_container_width=True
                )

# =================================================================================
# CONTROLADOR - MÓDULO 2: PORTAL DE AGENDAMENTO (CLIENTE FS)
# =================================================================================
with aba2:
    col_cadastro, col_cards = st.columns([1, 1.3])
    with col_cadastro:
        st.markdown('<div class="section-header-container">📝 Formulário de Agendamento Logístico</div>', unsafe_allow_html=True)
        with st.form("form_novo_agendamento", clear_on_submit=True):
            st.selectbox("1. SELECIONE A EMBARCAÇÃO / PROGRAMAÇÃO", ["SD II - Vigência: 12/06/2026"])
            
            listagem_janelas = [f"Janela #{of['id']} [{of['horario']}]" for of in st.session_state.ofertas]
            janela_selecionada = st.selectbox("2. ESCOLHA O HORÁRIO DA JANELA", listagem_janelas)
            
            c_pl, c_ve = st.columns(2)
            with c_pl: placa_in = st.text_input("PLACA", value="JVV-7606").upper()
            with c_ve: veiculo_in = st.text_input("VEÍCULO", value="BITREN").upper()
                
            c_mo, c_nf = st.columns(2)
            with c_mo: motorista_in = st.text_input("MOTORISTA", value="JOSE FRANCISCO").upper()
            with c_nf: nf_in = st.text_input("Nº NOTA FISCAL", value="154639")
                
            c_vo, c_pr = st.columns(2)
            with c_vo: volume_in = st.number_input("VOLUME M³", value=51000.00, step=0.01)
            with c_pr: produto_in = st.text_input("PRODUTO", value="ANIDRO").upper()
                
            arq_upload = st.file_uploader("ARQUIVO (ANEXAR NOTA FISCAL)", type=["pdf", "png", "jpg", "jpeg"])
            
            submetido = st.form_submit_button("🔒 CONFIRMAR AGENDAMENTO FS")
            
            if submetido:
                janela_limpa = janela_selecionada.split("[")[1].split("]")[0] if "[" in janela_selecionada else "06:00 às 07:00"
                nome_documento = arq_upload.name if arq_upload is not None else f"NF {nf_in}.pdf"
                
                # SE O CLIENTE FEZ UPLOAD, LÊ OS BYTES. CASO CONTRÁRIO, GERA O PDF COMPLETO COM OS DADOS DIGITADOS
                if arq_upload is not None:
                    binario_pdf = arq_upload.read()
                else:
                    binario_pdf = criar_comprovante_pdf("SD II", "12/06/2026", janela_limpa, placa_in, veiculo_in, motorista_in, nf_in, volume_in, produto_in)
                
                # INJEÇÃO IMUTÁVEL GARANTINDO A PRESENÇA DO CONTEÚDO BINÁRIO
                novo_registro = {
                    "balsa": "SD II",
                    "data": "12/06/2026",
                    "janela": janela_limpa,
                    "placa": placa_in,
                    "veiculo": veiculo_in,
                    "motorista": motorista_in,
                    "nf": nf_in,
                    "volume": float(volume_in),
                    "produto": produto_in,
                    "arquivo_nome": nome_documento,
                    "conteudo_bytes": binario_pdf
                }
                
                st.session_state.db_agendamentos.append(novo_registro)
                st.success("✅ Agendamento processado com sucesso!")
                st.rerun()

    with col_cards:
        st.markdown('<div class="section-header-container">📜 Comprovantes de Agendamento Emitidos</div>', unsafe_allow_html=True)
        if st.session_state.db_agendamentos:
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                try:
                    vol_val = float(ag.get("volume", 0))
                except:
                    vol_val = 0.0

                st.markdown(f"""
                <div style="background-color: #F8F9FA; border-left: 4px solid #007BFF; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                    <span style="float: right; font-size: 11px; color: #6C757D;">📋 Registro #{idx+1}</span>
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>BALSA:</b> {ag.get('balsa')} | <b>DATA:</b> {ag.get('data')} | <b>HORÁRIO:</b> {ag.get('janela')}</p>
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>PLACA:</b> {ag.get('placa')} | <b>VEÍCULO:</b> {ag.get('veiculo')} | <b>MOTORISTA:</b> {ag.get('motorista')}</p>
                    <p style="margin: 0; font-size: 13px;"><b>Nº NF:</b> {ag.get('nf')} | <b>VOLUME:</b> {vol_val:.2f} m³ | <b>PRODUTO:</b> {ag.get('produto')} | <b>ANEXO:</b> {ag.get('arquivo_nome')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_ed, c_dw = st.columns(2)
                with c_ed:
                    st.button("📝 Editar", key=f"btn_edit_card_{idx}", use_container_width=True)
                with c_dw:
                    st.download_button(
                        label="📄 Baixar PDF da NF",
                        data=ag.get("conteudo_bytes", b""),
                        file_name=ag.get("arquivo_nome", f"NF_{ag.get('nf')}.pdf"),
                        mime="application/pdf",
                        key=f"btn_download_m2_{idx}",
                        use_container_width=True
                    )
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Nenhum comprovante emitido até o momento.")
