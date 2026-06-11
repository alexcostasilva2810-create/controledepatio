import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Importações seguras do ReportLab (Padrão de mercado para Streamlit)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# 3. GERADOR DE PDF PROFISSIONAL COM REPORTLAB (NUNCA DA ERRO DE DEFINIÇÃO)
# ---------------------------------------------------------------------------------
def gerar_comprovante_pdf(balsa, data, janela, placa, veiculo, motorista, nf, volume, produto):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, alignment=1, textColor=colors.HexColor('#0B192C'))
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#343A40'), spaceBefore=10, spaceAfter=5)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, leading=14)
    
    # Conteúdo do PDF
    story.append(Paragraph("<b>ZION TECNOLOGIA - COMPROVANTE DE AGENDAMENTO</b>", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 10))
    
    # Tabela 1: Programação
    story.append(Paragraph("<b>1. DADOS DA PROGRAMAÇÃO LOGÍSTICA</b>", header_style))
    dados_p = [
        [Paragraph(f"<b>Balsa:</b> {balsa}", normal_style), 
         Paragraph(f"<b>Data:</b> {data}", normal_style), 
         Paragraph(f"<b>Janela:</b> {janela}", normal_style)]
    ]
    t1 = Table(dados_p, colWidths=[180, 180, 180])
    t1.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.grey), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # Tabela 2: Veículo e Carga
    story.append(Paragraph("<b>2. INFORMAÇÕES DO VEÍCULO E CARGA</b>", header_style))
    dados_v = [
        [Paragraph(f"<b>Motorista:</b> {motorista}", normal_style), Paragraph(f"<b>Produto:</b> {produto}", normal_style)],
        [Paragraph(f"<b>Placa:</b> {placa}", normal_style), Paragraph(f"<b>Veículo:</b> {veiculo}", normal_style)],
        [Paragraph(f"<b>Nº NF:</b> {nf}", normal_style), Paragraph(f"<b>Volume:</b> {float(volume):.2f} m³", normal_style)]
    ]
    t2 = Table(dados_v, colWidths=[270, 270])
    t2.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.grey), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t2)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ---------------------------------------------------------------------------------
# 4. BANCO DE DADOS EM MEMÓRIA (SESSION STATE)
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
            "balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00",
            "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", "arquivo_nome": "NF 1736.pdf",
            "conteudo_bytes": gerar_comprovante_pdf("SD II", "12/06/2026", "06:00 às 07:00", "JVV-7606", "BITREN", "JOSE FRANCISCO", "154639", 51000.00, "ANIDRO")
        }
    ]

# Painel Superior Principal
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
# MÓDULO 1
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1, 2])
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        st.selectbox("Selecione a Embarcação", ["SD II"], key="m1_balsa")
        st.date_input("Data de Vigência", datetime(2026, 6, 12), key="m1_data")
        exigencia_cts = st.number_input("Exigência (CTS)", min_value=0, value=25)
        st.selectbox("Hora Início", ["06:00", "07:00", "08:00"])
        if st.button("🔴 PUBLICAR DISPONIBILIDADE", use_container_width=True):
            st.success("Configuração atualizada!")

    with col_dist:
        st.markdown(f'<div class="section-header-container">⏱️ Distribuição de Vagas</div>', unsafe_allow_html=True)
        cols_janelas = st.columns(4)
        for idx, of in enumerate(st.session_state.ofertas):
            col_id = idx % 4
            with cols_janelas[col_id]:
                st.markdown(f'<div class="janela-card"><div style="font-size:11px;color:#718096;">JANELA #{of["id"]}</div><div style="font-weight:bold;color:#007BFF;">{of["horario"]}</div></div>', unsafe_allow_html=True)
                st.number_input("Vagas", min_value=0, value=of['vagas_o'], key=f"v_man_{of['id']}", label_visibility="collapsed")

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
                "Nº NF": ag["nf"], "VOLUME": f"{float(ag['volume']):.2f} m³", "PRODUTO": ag["produto"], "ANEXO": ag["arquivo_nome"]
            })
        col_tabela, col_botoes = st.columns([5.1, 0.9])
        with col_tabela:
            st.dataframe(pd.DataFrame(registros_m1), use_container_width=True, hide_index=True)
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
# MÓDULO 2
# =================================================================================
with aba2:
    col_cadastro, col_cards = st.columns([1, 1.3])
    with col_cadastro:
        st.markdown('<div class="section-header-container">📝 Formulário de Agendamento Logístico</div>', unsafe_allow_html=True)
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
                
            arq_upload = st.file_uploader("ARQUIVO (ANEXAR NOTA FISCAL)", type=["pdf", "png", "jpg", "jpeg"])
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
                    nome_documento = arq_upload.name if arq_upload is not None else f"NF_{nf_in}.pdf"
                    
                    if arq_upload is not None:
                        binario_pdf = arq_upload.read()
                    else:
                        binario_pdf = gerar_comprovante_pdf("SD II", "12/06/2026", janela_limpa, placa_in, veiculo_in, motorista_in, nf_in, volume_in, produto_in)
                    
                    st.session_state.db_agendamentos.append({
                        "balsa": "SD II", "data": "12/06/2026", "janela": janela_limpa,
                        "placa": placa_in, "veiculo": veiculo_in, "motorista": motorista_in,
                        "nf": nf_in, "volume": float(volume_in), "produto": produto_in,
                        "arquivo_nome": nome_documento, "conteudo_bytes": binario_pdf
                    })
                    st.success("✅ Agendamento registrado com sucesso!")
                    st.rerun()

    with col_cards:
        st.markdown('<div class="section-header-container">📜 Comprovantes de Agendamento Emitidos</div>', unsafe_allow_html=True)
        if st.session_state.db_agendamentos:
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                st.markdown(f"""
                <div style="background-color: #F8F9FA; border-left: 4px solid #007BFF; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                    <span style="float: right; font-size: 11px; color: #6C757D;">📋 Registro #{idx+1}</span>
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>BALSA:</b> {ag.get('balsa')} | <b>DATA:</b> {ag.get('data')} | <b>HORÁRIO:</b> {ag.get('janela')}</p>
                    <p style="margin: 0 0 4px 0; font-size: 13px;"><b>PLACA:</b> {ag.get('placa')} | <b>MOTORISTA:</b> {ag.get('motorista')}</p>
                    <p style="margin: 0; font-size: 13px;"><b>Nº NF:</b> {ag.get('nf')} | <b>VOLUME:</b> {float(ag.get('volume', 0)):.2f} m³ | <b>ANEXO:</b> {ag.get('arquivo_nome')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_ed, c_dw = st.columns(2)
                with c_ed: st.button("📝 Editar", key=f"m2_ed_{idx}", use_container_width=True)
                with c_dw:
                    st.download_button(
                        label="📄 Baixar PDF da NF",
                        data=ag.get("conteudo_bytes", b""),
                        file_name=ag.get("arquivo_nome", "Documento.pdf"),
                        mime="application/pdf",
                        key=f"m2_dw_{idx}",
                        use_container_width=True
                    )
                st.markdown("<br>", unsafe_allow_html=True)
