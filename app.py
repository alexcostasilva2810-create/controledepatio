import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página para ocupar a tela cheia
st.set_page_config(
    page_title="Zion Tecnologia - Controle de Pátio",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS customizada (Layout, Centralização e Cores)
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        
        /* Cabeçalho Superior Escuro e Centralizado */
        .header-top {
            background-color: #0b132b;
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 25px;
            text-align: center;
        }
        
        /* Títulos de Seções */
        .titulo-secao {
            background-color: #343a40;
            color: white;
            padding: 8px 14px;
            font-size: 14px;
            font-weight: bold;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-bottom: 0px;
        }
        
        /* Container interno dos blocos */
        .card-body-custom {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-bottom-left-radius: 6px;
            border-bottom-right-radius: 6px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.03);
            margin-bottom: 20px;
        }
        
        /* Boxes brancos das Janelas de Horário */
        .box-janela {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 6px;
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            margin-top: 5px;
        }
        .label-janela {
            font-size: 11px;
            font-weight: 600;
            color: #6c757d;
            text-transform: uppercase;
        }
        .horario-janela {
            font-weight: bold;
            color: #0d6efd;
            font-size: 13px;
        }

        /* Centralização do número inserido dentro do input do Streamlit */
        div[data-testid="stNumberInput"] input {
            text-align: center !important;
            font-weight: bold;
        }
        
        /* Cabeçalho fake para simular tabela perfeitamente alinhada nos módulos */
        .table-header-custom {
            background-color: #f1f3f5;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 11px;
            color: #495057;
            text-transform: uppercase;
            text-align: left;
            margin-bottom: 8px;
        }
        
        /* Alinhamento de dados verticais das linhas dos módulos */
        .cell-data {
            font-size: 12px;
            color: #212529;
            padding-top: 8px;
            text-align: center;
        }
        
        /* Ajuste do botão de download de NF para parecer um link limpo */
        div[data-testid="stDownloadButton"] button {
            padding: 2px 8px !important;
            font-size: 11px !important;
            background-color: #e2e8f0 !important;
            color: #4a5568 !important;
            border: 1px solid #cbd5e0 !important;
            border-radius: 4px !important;
        }
        div[data-testid="stDownloadButton"] button:hover {
            background-color: #cbd5e0 !important;
            color: #2d3748 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Helper para gerar um arquivo PDF em branco simulado para a NF
def gerar_pdf_simulado():
    return b"%PDF-1.4 ... Conteudo simulado da Nota Fiscal Zion Tecnologia ..."

# ==============================================================================
# BANCO DE DADOS EM MEMÓRIA (SESSION STATE)
# ==============================================================================
if "db_disponibilidades" not in st.session_state:
    st.session_state.db_disponibilidades = [{
        "balsa": "SD II",
        "data_vigencia": "12/06/2026",
        "config_grade": "12 Janelas Ativas",
        "janelas_detalhe": [
            {"janela_num": 1, "horario": "06:00 às 07:00", "vagas": 5, "ocupadas": 2, "disponiveis": 3},
            {"janela_num": 2, "horario": "07:00 às 08:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 3, "horario": "08:00 às 09:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 4, "horario": "09:00 às 10:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 5, "horario": "10:00 às 11:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 6, "horario": "11:00 às 12:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 7, "horario": "12:00 às 13:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 8, "horario": "13:00 às 14:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 9, "horario": "14:00 às 15:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 10, "horario": "15:00 às 16:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 11, "horario": "16:00 às 17:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
            {"janela_num": 12, "horario": "17:00 às 18:00", "vagas": 2, "ocupadas": 0, "disponiveis": 2},
        ]
    }]

if "db_agendamentos" not in st.session_state:
    st.session_state.db_agendamentos = [
        {"balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00", "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO", "nf": "154639", "volume": 51000.0, "produto": "ANIDRO", "arquivo_nome": "NF 1736.pdf"},
        {"balsa": "SD II", "data": "12/06/2026", "janela": "06:00 às 07:00", "placa": "HUG-9869", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO", "nf": "154639", "volume": 51000.0, "produto": "ANIDRO", "arquivo_nome": "NF 1812.pdf"}
    ]

if "edit_index" not in st.session_state:
    st.session_state.edit_index = -1

BALSAS_OPERACIONAIS = {
    "SD I": {"capacidade": "1040.4 m³", "cts_meta": 17}, "SD II": {"capacidade": "1530.0 m³", "cts_meta": 25},
    "SD IV": {"capacidade": "2325.6 m³", "cts_meta": 38}, "SD V": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD VI": {"capacidade": "1407.6 m³", "cts_meta": 23}, "SD VII": {"capacidade": "1468.8 m³", "cta_meta": 24},
    "SD VIII": {"capacidade": "1407.6 m³", "cts_meta": 23}, "SD IX": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD X": {"capacidade": "1407.6 m³", "cts_meta": 23}, "SD XI": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD XII": {"capacidade": "2325.6 m³", "cts_meta": 38}, "SD XIII": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD XIV": {"capacidade": "1468.8 m³", "cts_meta": 24}, "SD XV": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD XVI": {"capacidade": "1407.6 m³", "cts_meta": 23}, "SD XVII": {"capacidade": "1468.8 m³", "qs_meta": 24},
    "SD XVIII": {"capacidade": "795.6 m³", "cts_meta": 13}, "SD XX": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXI": {"capacidade": "2998.8 m³", "cts_meta": 49}, "SD XXII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXIII": {"capacidade": "2998.8 m³", "cts_meta": 49}, "TWB 200": {"capacidade": "2142.0 m³", "cts_meta": 35}
}

# ==============================================================================
# CABEÇALHO CENTRALIZADO
# ==============================================================================
st.markdown("""
    <div class="header-top">
        <h2 style="margin: 0; font-weight: 800; color: white; letter-spacing: 1px;">ZION TECNOLOGIA - LOGÍSTICA</h2>
        <p style="margin: 5px 0 0 0; color: #a0aec0; font-size: 14px;">SISTEMA DE PORTARIA & AGENDAMENTO LOGÍSTICO</p>
    </div>
""", unsafe_allow_html=True)

tab_modulo1, tab_modulo2 = st.tabs(["⚓ MÓDULO 1: Gestão de Disponibilidade (GD)", "🚛 MÓDULO 2: Portal de Agendamento (Cliente FS)"])

# ==============================================================================
# ABA 1: MÓDULO GESTÃO DE DISPONIBILIDADE (GD)
# ==============================================================================
with tab_modulo1:
    col_esq, col_dir = st.columns([4, 8], gap="medium")

    with col_esq:
        st.markdown('<p class="titulo-secao">⚓ Configuração da Oferta</p>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
            
            lista_opcoes = ["Selecione a Balsa Ofertada..."] + sorted(list(BALSAS_OPERACIONAIS.keys()))
            balsa_sel = st.selectbox("BALSA / EMBARCAÇÃO DISPONÍVEL", lista_opcoes, key="m1_balsa")
            
            cap_val, cts_val, cts_num = "0.0 m³", "0 CTS", 0
            if balsa_sel != "Selecione a Balsa Ofertada...":
                cap_val = BALSAS_OPERACIONAIS[balsa_sel]["capacidade"]
                cts_num = BALSAS_OPERACIONAIS[balsa_sel]["cts_meta"]
                cts_val = f"{cts_num} CTS"
                
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("CAPACIDADE (m³)", value=cap_val, disabled=True, key="m1_cap")
            with c2:
                st.text_input("EXIGÊNCIA (CTS)", value=cts_val, disabled=True, key="m1_cts")
                
            c3, c4 = st.columns(2)
            with c3:
                data_atual_ptbr = datetime.today().strftime("%d/%m/%Y")
                data_str = st.text_input("DATA DA OPERAÇÃO (DD/MM/AAAA)", value=data_atual_ptbr, key="m1_data")
            with c4:
                hora_ini = st.time_input("HORA INÍCIO", datetime.strptime("06:00", "%H:%M").time(), key="m1_hora")
                
            qtd_janelas = st.selectbox("QUANTIDADE DE JANELAS A DISPONIBILIBAR", [6, 10, 12, 18, 24], index=2, key="m1_qtd")
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_publicar = st.button("☁ PUBLICAR DISPONIBILIDADE", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_dir:
        badge_meta_top = f"META TOTAL: {cts_val}"
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center;" class="titulo-secao">
                <span>🕒 Distribuição de Vagas por Janela</span>
                <span style="background-color: #17a2b8; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{badge_meta_top}</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
            
            if balsa_sel == "Selecione a Balsa Ofertada...":
                st.info("Aguardando a seleção da balsa para gerar a grade de distribuição horária.")
                total_alocado = 0
                vagas_digitadas = []
            else:
                base_vagas = cts_num // qtd_janelas
                resto = cts_num % qtd_janelas
                
                janelas_cronograma = []
                try:
                    base_data = datetime.strptime(data_str, "%d/%m/%Y").date()
                except:
                    base_data = datetime.today().date()
                    
                ponteiro_hora = datetime.combine(base_data, hora_ini)
                
                for i in range(qtd_janelas):
                    inicio_str = ponteiro_hora.strftime("%H:%M")
                    ponteiro_hora += timedelta(hours=1)
                    fim_str = ponteiro_hora.strftime("%H:%M")
                    
                    vagas_sugeridas = base_vagas + (resto if i == 0 else 0)
                    janelas_cronograma.append({
                        "id": i + 1,
                        "faixa": f"{inicio_str} às {fim_str}",
                        "vagas_padrao": vagas_sugeridas
                    })
                
                vagas_digitadas = []
                colunas_grid = st.columns(4)
                
                for idx, jan in enumerate(janelas_cronograma):
                    col_alvo = colunas_grid[idx % 4]
                    with col_alvo:
                        st.markdown(f"""
                            <div class="box-janela">
                                <span class="label-janela">Janela #{jan['id']}</span>
                                <div class="horario-janela">{jan['faixa']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        cota_input = st.number_input(
                            f"Janela_{jan['id']}_input",
                            min_value=0,
                            value=int(jan['vagas_padrao']),
                            key=f"input_cota_{idx}",
                            label_visibility="collapsed"
                        )
                        vagas_digitadas.append({
                            "janela_num": jan['id'],
                            "horario": jan['faixa'],
                            "vagas": cota_input
                        })
                
                total_alocado = sum(item['vagas'] for item in vagas_digitadas)
                st.markdown("<br>", unsafe_allow_html=True)
                
                if total_alocado == cts_num:
                    st.success(f"✔ GRADE PERFEITA: {total_alocado} de {cts_num} CTS distribuídos.")
                elif total_alocado > cts_num:
                    st.error(f"❌ EXCESSO OPERACIONAL: Você distribuiu {total_alocado} CTS. O máximo permitido é {cts_num} CTS.")
                else:
                    st.warning(f"⚠️ ALOCAÇÃO INCOMPLETA: {total_alocado} de {cts_num} CTS distribuídos.")
                    
            st.markdown('</div>', unsafe_allow_html=True)

    if balsa_sel != "Selecione a Balsa Ofertada..." and btn_publicar:
        try:
            data_validada = datetime.strptime(data_str, "%d/%m/%Y").strftime("%d/%m/%Y")
            data_erro = False
        except ValueError:
            data_erro = True
            
        if data_erro:
            st.toast("Erro: Introduza a data no formato correto DD/MM/AAAA", icon="🚨")
        elif total_alocado != cts_num:
            st.toast("Erro: A distribuição não coincide com a meta física da balsa.", icon="🚨")
        else:
            nova_oferta = {
                "balsa": balsa_sel,
                "data_vigencia": data_validada,
                "config_grade": f"{qtd_janelas} Janelas Ativas",
                "janelas_detalhe": [
                    {
                        "janela_num": v["janela_num"],
                        "horario": v["horario"],
                        "vagas": v["vagas"],
                        "ocupadas": 0,
                        "disponiveis": v["vagas"]
                    } for v in vagas_digitadas
                ]
            }
            st.session_state.db_disponibilidades.append(nova_oferta)
            st.toast("Disponibilidade publicada com sucesso!", icon="✨")
            st.rerun()

    # SOLUÇÃO COMPACTA E CENTRALIZADA SEM ERROS
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="titulo-secao">📋 Painel de Ofertas Vigentes no Sistema (Visão GD)</p>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
        if not st.session_state.db_disponibilidades:
            st.markdown('<div style="text-align: center; color: #6c757d; padding: 10px;">Nenhuma balsa cadastrada até o momento.</div>', unsafe_allow_html=True)
        else:
            for idx, item in enumerate(st.session_state.db_disponibilidades):
                c_card1, c_card2 = st.columns([5, 1])
                with c_card1:
                    st.markdown(f"""
                        <div style="font-size: 15px; font-weight: bold; margin-bottom: 8px;">
                            ⚓ {item['balsa']} &nbsp;&nbsp;
                            <span style="background-color: #212529; color: white; font-size: 11px; padding: 3px 6px; border-radius:3px;">📅 {item['data_vigencia']}</span> &nbsp;
                            <span style="background-color: #0d6efd; color: white; font-size: 11px; padding: 3px 6px; border-radius:3px;">📊 {item['config_grade']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with c_card2:
                    if st.button("Excluir Regra", key=f"del_regra_{idx}", type="secondary", use_container_width=True):
                        st.session_state.db_disponibilidades.pop(idx)
                        st.toast("Regra operacional removida.", icon="🗑️")
                        st.rerun()
                
                lista_tabela = []
                for j in item['janelas_detalhe']:
                    lista_tabela.append({
                        "IDENTIFICADOR": f"Janela #{j['janela_num']}",
                        "HORÁRIO DE ATENDIMENTO": j['horario'],
                        "VAGAS OFERTADAS": int(j['vagas']),
                        "COTAS OCUPADAS": int(j['ocupadas']),
                        "VAGAS DISPONÍVEIS": int(j['disponiveis'])
                    })
                
                df_display = pd.DataFrame(lista_tabela)
                
                # Centralização nativa configurada individualmente por coluna mapeada de strings
                st.dataframe(
                    df_display, 
                    use_container_width=True, 
                    hide_index=True,
                    density="compact",
                    column_config={
                        "IDENTIFICADOR": st.column_config.Column(alignment="center"),
                        "HORÁRIO DE ATENDIMENTO": st.column_config.Column(alignment="center"),
                        "VAGAS OFERTADAS": st.column_config.Column(alignment="center"),
                        "COTAS OCUPADAS": st.column_config.Column(alignment="center"),
                        "VAGAS DISPONÍVEIS": st.column_config.Column(alignment="center"),
                    }
                )
                st.markdown("<hr style='margin: 15px 0; border-color: #e9ecef;'>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ==============================================================================
    # SEÇÃO DE AGENDADOS NO MÓDULO 1 EM LINHA COM COLUNAS ALINHADAS E DOWNLOAD DE NF
    # ==============================================================================
    st.markdown('<p class="titulo-secao">📋 VEÍCULOS AGENDADOS (Visão Geral de Portaria)</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
        if not st.session_state.db_agendamentos:
            st.markdown('<div style="text-align: center; color: #6c757d; padding: 10px;">Nenhum veículo agendado no sistema até o momento.</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="table-header-custom">
                    <table style="width: 100%; border-collapse: collapse; border: none; background: transparent; text-align: center;">
                        <tr>
                            <td style="width: 10%; text-align: center;">Balsa</td>
                            <td style="width: 10%; text-align: center;">Data</td>
                            <td style="width: 12%; text-align: center;">Horário</td>
                            <td style="width: 10%; text-align: center;">Placa</td>
                            <td style="width: 10%; text-align: center;">Veículo</td>
                            <td style="width: 14%; text-align: center;">Motorista</td>
                            <td style="width: 10%; text-align: center;">Nº NF</td>
                            <td style="width: 10%; text-align: center;">Volume</td>
                            <td style="width: 10%; text-align: center;">Produto</td>
                            <td style="width: 8%; text-align: center;">Anexo NF</td>
                        </tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
            for idx, ag in enumerate(st.session_state.db_agendamentos):
                cols_m1 = st.columns([1.0, 1.0, 1.2, 1.0, 1.0, 1.4, 1.0, 1.0, 1.0, 0.8])
                
                cols_m1[0].markdown(f'<div class="cell-data"><b>{ag["balsa"]}</b></div>', unsafe_allow_html=True)
                cols_m1[1].markdown(f'<div class="cell-data">{ag["data"]}</div>', unsafe_allow_html=True)
                cols_m1[2].markdown(f'<div class="cell-data" style="color:#0d6efd;font-weight:600;">{ag["janela"]}</div>', unsafe_allow_html=True)
                cols_m1[3].markdown(f'<div class="cell-data">`{ag["placa"]}`</div>', unsafe_allow_html=True)
                cols_m1[4].markdown(f'<div class="cell-data">{ag["veiculo"]}</div>', unsafe_allow_html=True)
                cols_m1[5].markdown(f'<div class="cell-data">{ag["motorista"]}</div>', unsafe_allow_html=True)
                cols_m1[6].markdown(f'<div class="cell-data">{ag["nf"]}</div>', unsafe_allow_html=True)
                cols_m1[7].markdown(f'<div class="cell-data">{float(ag["volume"]):.2f} m³</div>', unsafe_allow_html=True)
                cols_m1[8].markdown(f'<div class="cell-data">{ag["produto"]}</div>', unsafe_allow_html=True)
                
                with cols_m1[9]:
                    st.download_button(
                        label="📄 PDF",
                        data=gerar_pdf_simulado(),
                        file_name=ag["arquivo_nome"],
                        mime="application/pdf",
                        key=f"m1_down_{idx}"
                    )
                st.markdown("<div style='border-bottom: 1px solid #f1f3f5; margin: 4px 0;'></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ABA 2: MÓDULO 2 - PORTAL DE AGENDAMENTO (CLIENTE FS)
# ==============================================================================
with tab_modulo2:
    col_fs_esq, col_fs_dir = st.columns([4, 8], gap="medium")
    
    with col_fs_esq:
        st.markdown('<p class="titulo-secao">📝 Formulário de Agendamento Logístico</p>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
            
            if not st.session_state.db_disponibilidades:
                st.warning("Nenhuma balsa ou oferta está disponível no momento. Aguarde a publicação da GD.")
                oferta_selecionada = None
            else:
                opcoes_ofertas = [f"{o['balsa']} - Vigência: {o['data_vigencia']}" for o in st.session_state.db_disponibilidades]
                idx_oferta = st.selectbox("1. SELECIONE A EMBARCAÇÃO / PROGRAMAÇÃO", range(len(opcoes_ofertas)), format_func=lambda x: opcoes_ofertas[x], key="fs_oferta_sel")
                oferta_selecionada = st.session_state.db_disponibilidades[idx_oferta]
            
            if oferta_selecionada:
                opcoes_janelas = []
                for jan in oferta_selecionada["janelas_detalhe"]:
                    status_vagas = f"({jan['disponiveis']} vagas restantes)" if jan['disponiveis'] > 0 else "(ESGOTADA)"
                    opcoes_janelas.append(f"Janela #{jan['janela_num']} [{jan['horario']}] {status_vagas}")
                
                janela_idx_sel = st.selectbox("2. ESCOLHA O HORÁRIO DA JANELA", range(len(opcoes_janelas)), format_func=lambda x: opcoes_janelas[x], key="fs_janela_sel")
                janela_objeto = oferta_selecionada["janelas_detalhe"][janela_idx_sel]
                
                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                
                c_fs1, c_fs2 = st.columns(2)
                with c_fs1:
                    placa = st.text_input("PLACA", placeholder="ABC-1234", key="form_placa")
                    motorista = st.text_input("MOTORISTA", placeholder="Nome Completo", key="form_moto")
                with c_fs2:
                    veiculo = st.text_input("VEÍCULO", placeholder="Ex: Carreta Bitrem", key="form_veic")
                    num_nf = st.text_input("Nº NOTA FISCAL", placeholder="Apenas números", key="form_nf")
                    
                c_fs3, c_fs4 = st.columns(2)
                with c_fs3:
                    volume = st.number_input("VOLUME M³", min_value=0.0, value=0.0, step=100.0, format="%.2f", key="form_vol")
                with c_fs4:
                    produto = st.text_input("PRODUTO", placeholder="Ex: ANIDRO", key="form_prod")
                    
                arquivo_nf = st.file_uploader("ARQUIVO (ANEXAR NOTA FISCAL)", type=["pdf", "jpg", "png"], key="form_file")
                
                st.markdown("<br>", unsafe_allow_html=True)
                btn_confirmar_agendamento = st.button("🔒 CONFIRMAR AGENDAMENTO FS", type="primary", use_container_width=True)
                
                if btn_confirmar_agendamento:
                    if not (placa and veiculo and motorista and num_nf and volume > 0 and produto):
                        st.error("Por favor, preencha todos os campos obrigatórios.")
                    elif janela_objeto["disponiveis"] <= 0:
                        st.error("Não foi possível agendar: Esta janela já se encontra esgotada!")
                    else:
                        janela_objeto["ocupadas"] += 1
                        janela_objeto["disponiveis"] -= 1
                        
                        novo_agendamento = {
                            "balsa": oferta_selecionada["balsa"],
                            "data": oferta_selecionada["data_vigencia"],
                            "janela": janela_objeto["horario"],
                            "placa": placa.upper(),
                            "veiculo": veiculo.upper(),
                            "motorista": motorista.upper(),
                            "nf": num_nf,
                            "volume": float(volume),
                            "produto": produto.upper(),
                            "arquivo_nome": arquivo_nf.name if arquivo_nf is not None else "NF_Anexa.pdf"
                        }
                        st.session_state.db_agendamentos.append(novo_agendamento)
                        st.success("Agendamento efetuado com sucesso!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col_fs_dir:
        st.markdown('<p class="titulo-secao">📜 Comprovantes de Agendamento Emitidos</p>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
            
            if not st.session_state.db_agendamentos:
                st.info("Nenhum caminhão agendado para esta programação até o momento.")
            else:
                if st.session_state.edit_index == -1:
                    st.markdown("""
                        <div class="table-header-custom">
                            <table style="width: 100%; border-collapse: collapse; border: none; background: transparent; text-align: center;">
                                <tr>
                                    <td style="width: 10%; text-align: center;">Balsa</td>
                                    <td style="width: 10%; text-align: center;">Data</td>
                                    <td style="width: 12%; text-align: center;">Horário</td>
                                    <td style="width: 10%; text-align: center;">Placa</td>
                                    <td style="width: 10%; text-align: center;">Veículo</td>
                                    <td style="width: 13%; text-align: center;">Motorista</td>
                                    <td style="width: 10%; text-align: center;">Nº NF</td>
                                    <td style="width: 9%; text-align: center;">Volume</td>
                                    <td style="width: 8%; text-align: center;">Produto</td>
                                    <td style="width: 8%; text-align: center;">NF File</td>
                                    <td style="width: 10%; text-align: center;">Ações</td>
                                </tr>
                            </table>
                        </div>
                    """, unsafe_allow_html=True)
                
                for idx, ag in enumerate(st.session_state.db_agendamentos):
                    
                    if st.session_state.edit_index == idx:
                        st.markdown(f"<div style='background-color:#fff3cd; padding:8px; border-radius:4px; font-weight:bold; margin-bottom:10px; font-size:12px;'>✏️ Editando Lançamento #{idx+1}</div>", unsafe_allow_html=True)
                        
                        c_ed1, c_ed2, c_ed3 = st.columns([4, 4, 4])
                        with c_ed1:
                            ed_placa = st.text_input("PLACA", value=ag["placa"], key=f"ed_placa_{idx}")
                            ed_motorista = st.text_input("MOTORISTA", value=ag["motorista"], key=f"ed_moto_{idx}")
                        with c_ed2:
                            ed_veiculo = st.text_input("VEÍCULO", value=ag["veiculo"], key=f"ed_veic_{idx}")
                            ed_nf = st.text_input("Nº NF", value=ag["nf"], key=f"ed_nf_{idx}")
                        with c_ed3:
                            ed_volume = st.number_input("VOLUME M³", value=float(ag["volume"]), format="%.2f", key=f"ed_vol_{idx}")
                            ed_produto = st.text_input("PRODUTO", value=ag["produto"], key=f"ed_prod_{idx}")
                        
                        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                        if st.button("💾 Salvar Alterações", key=f"save_btn_{idx}", use_container_width=True, type="primary"):
                            st.session_state.db_agendamentos[idx]["placa"] = ed_placa.upper()
                            st.session_state.db_agendamentos[idx]["veiculo"] = ed_veiculo.upper()
                            st.session_state.db_agendamentos[idx]["motorista"] = ed_motorista.upper()
                            st.session_state.db_agendamentos[idx]["nf"] = ed_nf
                            st.session_state.db_agendamentos[idx]["volume"] = float(ed_volume)
                            st.session_state.db_agendamentos[idx]["produto"] = ed_produto.upper()
                            
                            st.session_state.edit_index = -1
                            st.toast("Alterações salvas com sucesso!", icon="✨")
                            st.rerun()
                    else:
                        cols_m2 = st.columns([1.0, 1.0, 1.2, 1.0, 1.0, 1.3, 1.0, 0.9, 0.8, 0.8, 1.0])
                        
                        cols_m2[0].markdown(f'<div class="cell-data"><b>{ag["balsa"]}</b></div>', unsafe_allow_html=True)
                        cols_m2[1].markdown(f'<div class="cell-data">{ag["data"]}</div>', unsafe_allow_html=True)
                        cols_m2[2].markdown(f'<div class="cell-data" style="color:#0d6efd;font-weight:600;">{ag["janela"]}</div>', unsafe_allow_html=True)
                        cols_m2[3].markdown(f'<div class="cell-data">`{ag["placa"]}`</div>', unsafe_allow_html=True)
                        cols_m2[4].markdown(f'<div class="cell-data">{ag["veiculo"]}</div>', unsafe_allow_html=True)
                        cols_m2[5].markdown(f'<div class="cell-data">{ag["motorista"]}</div>', unsafe_allow_html=True)
                        cols_m2[6].markdown(f'<div class="cell-data">{ag["nf"]}</div>', unsafe_allow_html=True)
                        cols_m2[7].markdown(f'<div class="cell-data">{float(ag["volume"]):.2f} m³</div>', unsafe_allow_html=True)
                        cols_m2[8].markdown(f'<div class="cell-data">{ag["produto"]}</div>', unsafe_allow_html=True)
                        
                        with cols_m2[9]:
                            st.download_button(
                                label="📄 PDF",
                                data=gerar_pdf_simulado(),
                                file_name=ag["arquivo_nome"],
                                mime="application/pdf",
                                key=f"m2_down_{idx}"
                            )
                            
                        with cols_m2[10]:
                            if st.button("📝 Editar", key=f"edit_btn_{idx}", use_container_width=True):
                                st.session_state.edit_index = idx
                                st.rerun()
                                
                    st.markdown("<div style='border-bottom: 1px solid #e9ecef; margin: 4px 0;'></div>", unsafe_allow_html=True)
                    
            st.markdown('</div>', unsafe_allow_html=True)
