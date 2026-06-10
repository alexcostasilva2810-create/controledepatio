import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página para ocupar a tela cheia
st.set_page_config(
    page_title="Zion Tecnologia - Gestão Portuária",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS injetada para manter o design idêntico às imagens enviadas
st.markdown("""
    <style>
        /* Desativa paddings padrão do Streamlit para colar os elementos */
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
        
        /* Cabeçalho superior azul escuro */
        .header-top {
            background-color: #0b132b;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
        
        /* Container interno dos blocos (Simulação de Cards Bootstrap) */
        .card-body-custom {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-bottom-left-radius: 6px;
            border-bottom-right-radius: 6px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        }
        
        /* Boxes brancos das Janelas de Horário */
        .box-janela {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 8px;
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
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
            margin-bottom: 2px;
        }
        
        /* Remove margens extras que o streamlit coloca entre componentes acoplados */
        [data-testid="stVerticalBlock"] > div { gap: 0.2rem; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# BANCO DE DADOS EM MEMÓRIA (SESSION STATE)
# ==============================================================================
if "db_disponibilidades" not in st.session_state:
    st.session_state.db_disponibilidades = []

BALSAS_OPERACIONAIS = {
    "SD I": {"capacidade": "1040.4 m³", "cts_meta": 17},
    "SD II": {"capacidade": "1530.0 m³", "cts_meta": 25},
    "SD IV": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD V": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD VI": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD VII": {"capacidade": "1468.8 m³", "cts_meta": 24},
    "SD VIII": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD IX": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD X": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD XI": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD XII": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD XIII": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD XIV": {"capacidade": "1468.8 m³", "cts_meta": 24},
    "SD XV": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD XVI": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD XVII": {"capacidade": "1468.8 m³", "cts_meta": 24},
    "SD XVIII": {"capacidade": "795.6 m³", "cts_meta": 13},
    "SD XX": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXI": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXIII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "TWB 200": {"capacidade": "2142.0 m³", "cts_meta": 35}
}

# ==============================================================================
# CABEÇALHO ZION TECNOLOGIA (CONFORME SOLICITADO)
# ==============================================================================
st.markdown("""
    <div class="header-top">
        <div>
            <h4 style="margin: 0; font-weight: 700; color: white; letter-spacing: 0.5px;">SISTEMA DE PORTARIA & AGENDAMENTO LOGÍSTICO</h4>
            <small style="color: #a0aec0;">Painel de Configuração Master - Zion Tecnologia</small>
        </div>
        <span class="badge" style="background-color: #0d6efd; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;">
            MÓDULO 1: GESTÃO DE DISPONIBILIDADE
        </span>
    </div>
""", unsafe_allow_html=True)

# Layout de Colunas principais (Formulário na Esquerda [4], Distribuição na Direita [8])
col_esq, col_dir = st.columns([4, 8], gap="medium")

# ==============================================================================
# COLUNA ESQUERDA: CONFIGURAÇÃO DA OFERTA
# ==============================================================================
with col_esq:
    st.markdown('<p class="titulo-secao">⚓ Configuração da Oferta</p>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
        
        # Seleção de balsa
        lista_opcoes = ["Selecione a Balsa Ofertada..."] + sorted(list(BALSAS_OPERACIONAIS.keys()))
        balsa_sel = st.selectbox("BALSA / EMBARCAÇÃO DISPONÍVEL", lista_opcoes)
        
        # Gatilho de metadados
        cap_val, cts_val, cts_num = "0.0 m³", "0 CTS", 0
        if balsa_sel != "Selecione a Balsa Ofertada...":
            cap_val = BALSAS_OPERACIONAIS[balsa_sel]["capacidade"]
            cts_num = BALSAS_OPERACIONAIS[balsa_sel]["cts_meta"]
            cap_val = BALSAS_OPERACIONAIS[balsa_sel]["capacidade"]
            cts_val = f"{cts_num} CTS"
            
        # Linha: Capacidade e Meta
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("CAPACIDADE (m³)", value=cap_val, disabled=True)
        with c2:
            st.text_input("EXIGÊNCIA (CTS)", value=cts_val, disabled=True)
            
        # Linha: Data e Hora de Início
        c3, c4 = st.columns(2)
        with c3:
            data_op = st.date_input("DATA DA OPERAÇÃO", datetime.today())
        with c4:
            hora_ini = st.time_input("HORA INÍCIO", datetime.strptime("06:00", "%H:%M").time())
            
        # Linha: Quantidade de Janelas Operacionais
        qtd_janelas = st.selectbox(
            "QUANTIDADE DE JANELAS A DISPONIBILIBAR", 
            [6, 10, 12, 18, 24], 
            index=2, 
            help="Defina quantas janelas o cliente verá no portal."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Botão de envio estilizado nativo do Streamlit (estilo submit)
        btn_publicar = st.button("☁ PUBLICAR DISPONIBILIDADE", type="primary", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# COLUNA DIREITA: DISTRIBUIÇÃO DE VAGAS POR JANELA
# ==============================================================================
with col_dir:
    badge_meta_top = f"META TOTAL: {cts_val}"
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;" class="titulo-secao">
            <span>🕒 Distribuição de Vagas por Janela</span>
            <span class="badge bg-dark" style="font-size: 11px; padding: 2px 8px;">{badge_meta_top}</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
        
        if balsa_sel == "Selecione a Balsa Ofertada...":
            st.info("Aguardando a seleção da balsa para gerar a grade de distribuição horária.")
            vagas_digitadas = []
        else:
            # Algoritmo de divisão exata + resto na primeira janela (idêntico ao seu)
            base_vagas = cts_num // qtd_janelas
            resto = cts_num % qtd_janelas
            
            janelas_cronograma = []
            ponteiro_hora = datetime.combine(data_op, hora_ini)
            
            for i in range(qtd_janelas):
                inicio_str = ponteiro_hora.strftime("%H:%M")
                ponteiro_hora += timedelta(hours=1)  # Intervalo padrão de 1 hora por janela
                fim_str = ponteiro_hora.strftime("%H:%M")
                
                vagas_sugeridas = base_vagas + (resto if i == 0 else 0)
                janelas_cronograma.append({
                    "id": i + 1,
                    "faixa": f"{inicio_str} às {fim_str}",
                    "vagas_padrao": vagas_sugeridas
                })
            
            # Renderização dos inputs numéricos em colunas de 4 em 4
            vagas_digitadas = []
            colunas_grid = st.columns(4)
            
            for idx, jan in enumerate(janelas_cronograma):
                col_alvo = colunas_grid[idx % 4]
                with col_alvo:
                    # Rótulo HTML estilizado da janela
                    st.markdown(f"""
                        <div class="box-janela">
                            <span class="label-janela">Janela #{jan['id']}</span>
                            <div class="horario-janela">{jan['faixa']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Caixa de texto numérica acoplada logo abaixo da marcação visual
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
            
            # Barra de validação do status da alocação
            total_alocado = sum(item['vagas'] for item in vagas_digitadas)
            st.markdown("<br>", unsafe_allow_html=True)
            
            if total_alocado == cts_num:
                st.success(f"✔ GRADE PERFEITA: {total_alocado} de {cts_num} CTS distribuídos.")
            elif total_alocado > cts_num:
                st.error(f"❌ EXCESSO OPERACIONAL: Você distribuiu {total_alocado} CTS. O teto máximo permitido é {cts_num} CTS.")
            else:
                st.warning(f"⚠️ ALOCAÇÃO INCOMPLETA: {total_alocado} de {cts_num} CTS distribuídos. Ajuste os valores nas janelas.")
                
        st.markdown('</div>', unsafe_allow_html=True)

# Lógica de gravação ao submeter o formulário
if balsa_sel != "Selecione a Balsa Ofertada..." and btn_publicar:
    if total_alocado != cts_num:
        st.toast("Não foi possível salvar: A distribuição não corresponde à meta física da balsa.", icon="🚨")
    else:
        nova_oferta = {
            "balsa": balsa_sel,
            "data_vigencia": data_op.strftime("%d/%m/%Y"),
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

# ==============================================================================
# ELEMENTO INFERIOR: PAINEL DE OFERTAS VIGENTES NO SISTEMA
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="titulo-secao">📋 Painel de Ofertas Vigentes no Sistema</p>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card-body-custom">', unsafe_allow_html=True)
    
    if not st.session_state.db_disponibilidades:
        st.markdown('<div style="text-align: center; color: #6c757d; padding: 15px;">Nenhuma balsa cadastrada até o momento.</div>', unsafe_allow_html=True)
    else:
        for idx, item in enumerate(st.session_state.db_disponibilidades):
            # Cabeçalho interno do bloco consolidado da balsa
            c_card1, c_card2 = st.columns([5, 1])
            with c_card1:
                st.markdown(f"""
                    <div style="font-size: 15px; font-weight: bold; margin-bottom: 8px;">
                        ⚓ {item['balsa']} &nbsp;&nbsp;
                        <span class="badge bg-dark" style="font-size: 11px; padding: 3px 6px; color:white; border-radius:3px;">📅 {item['data_vigencia']}</span> &nbsp;
                        <span class="badge bg-info text-dark" style="font-size: 11px; padding: 3px 6px; border-radius:3px;">📊 {item['config_grade']}</span>
                    </div>
                """, unsafe_allow_html=True)
            with c_card2:
                if st.button("Excluir Regra", key=f"del_regra_{idx}", type="secondary", use_container_width=True):
                    st.session_state.db_disponibilidades.pop(idx)
                    st.toast("Regra excluída com sucesso.", icon="🗑️")
                    st.rerun()
            
            # Montagem do DataFrame estruturado para exibir a tabela
            lista_tabela = []
            for j in item['janelas_detalhe']:
                lista_tabela.append({
                    "IDENTIFICADOR": f"Janela #{j['janela_num']}",
                    "HORÁRIO DE ATENDIMENTO": j['horario'],
                    "VAGAS OFERTADAS": j['vagas'],
                    "COTAS OCUPADAS": j['ocupadas'],
                    "VAGAS DISPONÍVEIS": j['disponiveis']
                })
            
            df_display = pd.DataFrame(lista_tabela)
            # Renderiza a tabela limpa e ajustada à largura do container
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
