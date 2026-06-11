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
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# 3. GERADOR DE COMPROVANTE (NATIVO - SEM BIBLIOTECAS EXTERNAS)
# ---------------------------------------------------------------------------------
def gerar_comprovante_html_bytes(balsa, data, janela, placa, veiculo, motorista, nf, volume, produto):
    """Gera um arquivo HTML formatado como documento que qualquer navegador baixa e imprime como PDF"""
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; color: #333; }}
            .header {{ text-align: center; border-bottom: 2px solid #0B192C; padding-bottom: 10px; margin-bottom: 20px; }}
            .title {{ font-size: 20px; font-weight: bold; color: #0B192C; }}
            .meta {{ text-align: right; font-size: 12px; color: #666; }}
            .section-title {{ font-size: 14px; font-weight: bold; background: #343A40; color: white; padding: 6px; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
            th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; font-size: 13px; }}
            th {{ background: #f2f2f2; }}
            .footer {{ text-align: center; margin-top: 50px; font-size: 11px; color: #777; border-top: 1px solid #ccc; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">ZION TECNOLOGIA - COMPROVANTE DE AGENDAMENTO</div>
            <div class="meta">Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        </div>
        
        <div class="section-title">1. DADOS DA PROGRAMAÇÃO LOGÍSTICA</div>
        <table>
            <tr>
                <th>Embarcação / Balsa</th>
                <th>Data da Operação</th>
                <th>Janela Horária</th>
            </tr>
            <tr>
                <td>{balsa}</td>
                <td>{data}</td>
                <td>{janela}</td>
            </tr>
        </table>

        <div class="section-title">2. INFORMAÇÕES DO VEÍCULO E CARGA</div>
        <table>
            <tr>
                <th>Motorista</th>
                <td>{motorista}</td>
                <th>Produto</th>
                <td>{produto}</td>
            </tr>
            <tr>
                <th>Placa</th>
                <td>{placa}</td>
                <th>Veículo</th>
                <td>{veiculo}</td>
            </tr>
            <tr>
                <th>Nº Nota Fiscal</th>
                <td>{nf}</td>
                <th>Volume Cadastrado</th>
                <td>{float(volume):.2f} m³</td>
            </tr>
        </table>

        <div class="footer">
            Documento de controle de pátio interno - Validação de Portaria ZION<br>
            Vinculado à NF-e informada pelo cliente da cota operacional.
        </div>
    </body>
    </html>
    """
    return html_content.encode("utf-8")

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
        {"id": 6, "11:00 às 12:00": "11:00 às 12:00", "vagas_o": 2, "cotas_o": 0},
    ]

if "db_agendamentos" not in st.session_state:
    st.session_state.db_agendamentos = [
        {
            "balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00",
            "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", "arquivo_nome": "Comprovante_154639.html",
            "conteudo_bytes": gerar_comprovante_html_bytes("SD II", "12/06/2026", "06:00 às 07:00", "JVV-7606", "BITREN", "JOSE FRANCISCO", "154639", 51000.00, "ANIDRO")
        }
    ]

# Cabeçalho Principal do Painel
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
        cols_janelas = st.columns(3)
        for idx, of in enumerate(st.session_state.ofertas[:6]):
            col_id = idx % 3
            with cols_janelas[col_id]:
                st.markdown(f'<div class="janela-card"><div style="font-size:11px;color:#718096;">JANELA #{of["id"]}</div><div style="font-weight:bold;color:#007BFF;">{of["horario"]}</div></div>', unsafe_allow_html=True)
                st.number_input("Vagas", min_value=0, value=of['vagas_o'], key=f"v_m1_{of['id']}", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Ofertas Vigentes no Sistema (Linha Verde = Esgotado)</div>', unsafe_allow_html=True)
    
    df_of = pd.DataFrame(st.session_state.ofertas[:5])
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
                "Nº NF": ag["nf"], "VOLUME": f"{float(ag['volume']):.2f} m³", "PRODUTO": ag["produto"], "DOCUMENTO": ag["arquivo_nome"]
            })
        col_tabela, col_botoes = st.columns([5.1, 0.9])
        with col_tabela:
            st.dataframe(pd.DataFrame(registros_m1), use_container_width=True, hide_index=True)
        with col_botoes:
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                st.download_button(
                    label="📄 DOC",
                    data=ag["conteudo_bytes"],
                    file_name=ag["arquivo_nome"],
                    mime="text/html",
                    key=f"m1_down_{idx}",
                    use_container_width=True
                )

# =================================================================================
# MÓDULO 2: PORTAL DE AGENDAMENTO (CLIENTE FS)
# =================================================================================
with aba2:
    col_cadastro, col_cards = st.columns([1, 1.3])
    with col_cadastro:
        st.markdown('<div class="section-header-container">📝 Formulário de Agendamento Logístico</div>', unsafe_allow_html=True)
        with st.form("form_novo_agendamento", clear_on_submit=True):
            st.selectbox("1. SELECIONE A EMBARCAÇÃO / PROGRAMAÇÃO", ["SD II - Vigência: 12/06/2026"])
            
            opcoes_seletor = []
            for of in st.session_state.ofertas[:5]:
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
                
            submetido = st.form_submit_button("🔒 CONFIRMAR AGENDAMENTO FS")
            
            if submetido:
                id_janela_sel = int(janela_selecionada.split("#")[1].split("
