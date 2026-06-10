import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página para ocupar a tela cheia
st.set_page_config(
    page_title="SISTEMA DE PORTARIA & AGENDAMENTO LOGÍSTICO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização customizada para manter a identidade visual executiva (Zion Tecnologia)
st.markdown("""
    <style>
        .header-top {
            background-color: #0b132b;
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .box-janela {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .label-custom {
            font-size: 11px;
            font-weight: 700;
            color: #475569;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .meta-text {
            color: #0284c7;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# BANCO DE DADOS EM MEMÓRIA (STREAMLIT SESSION STATE)
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
# TOPO DO SISTEMA
# ==============================================================================
st.markdown("""
    <div class="header-top">
        <div>
            <h3 style="margin: 0; font-weight: 700; color: white;">⚓ SISTEMA DE PORTARIA & AGENDAMENTO LOGÍSTICO</h3>
            <span style="color: #94a3b8; font-size: 14px;">Painel de Configuração Master - Zion Tecnologia</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.subheader("MÓDULO 1: GESTÃO DE DISPONIBILIDADE (GD)")

# Divisão de colunas principais (Formulário à esquerda, Grade à direita)
col_form, col_grade = st.columns([1, 2], gap="large")

with col_form:
    st.subheader("Cadastro de Oferta de Balsa")
    
    # Campo 1: Localidade / Embarcação
    lista_balsas_keys = ["Selecione a Balsa Ofertada..."] + sorted(list(BALSAS_OPERACIONAIS.keys()))
    balsa_selecionada = st.selectbox("LOCALIDADE / EMBARCAÇÃO", lista_balsas_keys, label_visibility="visible")
    
    # Validações e métricas automáticas
    capacidade_view = "0.0 m³"
    meta_view = "0 CTS"
    meta_num = 0
    
    if balsa_selecionada != "Selecione a Balsa Ofertada...":
        capacidade_view = BALSAS_OPERACIONAIS[balsa_selecionada]["capacidade"]
        meta_num = BALSAS_OPERACIONAIS[balsa_selecionada]["cts_meta"]
        meta_view = f"{meta_num} CTS"

    # Campos de leitura lado a lado
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Capacidade Volumétrica", value=capacidade_view, disabled=True)
    with c2:
        st.text_input("Exigência Física (Meta)", value=meta_view, disabled=True)
        
    # Vigência e Primeiro Agendamento
    c3, c4 = st.columns(2)
    with c3:
        data_vigencia = st.date_input("VIGÊNCIA DA DISPONIBILIDADE", datetime.today())
    with c4:
        hora_inicio = st.time_input("HORA DO 1º AGENDAMENTO", datetime.strptime("07:00", "%H:%M").time())
        
    # Intervalo e Qtd de Janelas
    c5, c6 = st.columns(2)
    with c5:
        intervalo_opcao = st.selectbox("INTERVALO (FREQ.)", ["A cada 1 hora", "A cada 2 horas"], index=1)
        freq_horas = 1 if "1 hora" in intervalo_opcao else 2
    with c6:
        qtd_janelas = st.selectbox("QTD DE JANELAS", [6, 12, 18, 24], index=1)

    # Botão de Envio (Estilo Preto conforme original)
    st.markdown("<br>", unsafe_allow_html=True)
    btn_enviar = st.button("PUBLICAR DISPONIBILIDADE", type="primary", use_container_width=True)

# ==============================================================================
# GRADE DINÂMICA DE DISTRIBUIÇÃO DE VAGAS
# ==============================================================================
with col_grade:
    st.subheader("Distribuição Inteligente de Vagas")
    
    if balsa_selecionada == "Selecione a Balsa Ofertada...":
        st.info("Aguardando definição dos parâmetros do formulário...")
        valores_janelas = []
    else:
        st.write(f"As vagas foram calculadas e divididas igualmente para atingir o teto operacional de **{meta_view}** da balsa **{balsa_selecionada}**.")
        
        # Geração dos Horários calculados das Janelas
        base_vagas = meta_num // qtd_janelas
        sobra_vagas = meta_num % qtd_janelas
        
        janelas_calculadas = []
        hora_atual = datetime.combine(data_vigencia, hora_inicio)
        
        for i in range(qtd_janelas):
            h_ini = hora_atual.strftime("%H:%M")
            hora_atual += timedelta(hours=freq_horas)
            h_fim = hora_atual.strftime("%H:%M")
            
            vagas_sugeridas = base_vagas + (sobra_vagas if i == 0 else 0)
            janelas_calculadas.append({
                "num": i + 1,
                "horario": f"{h_ini} - {h_fim}",
                "sugerido": vagas_sugeridas
            })
            
        # Desenha a grade com inputs numéricos editáveis
        valores_janelas = []
        grid_cols = st.columns(4) # Exibe em colunas organizadas de 4 em 4
        
        for idx, jan in enumerate(janelas_calculadas):
            col_target = grid_cols[idx % 4]
            with col_target:
                st.markdown(f"""
                    <div class="box-janela">
                        <span class="label-custom">Janela #{jan['num']}</span>
                        <div style="font-weight:bold; color:#0284c7; font-size:13px; margin-bottom:5px;">{jan['horario']}</div>
                    </div>
                """, unsafe_allow_html=True)
                # Input acoplado logo abaixo da caixinha horária
                v_digitado = st.number_input(
                    "Vagas", 
                    min_value=0, 
                    value=int(jan['sugerido']), 
                    key=f"input_j_{idx}", 
                    label_visibility="collapsed"
                )
                valores_janelas.append({
                    "janela_num": jan['num'],
                    "horario": jan['horario'],
                    "vagas": v_digitado
                })
                
        # Validação do Saldo em tempo real
        total_alocado = sum(j['vagas'] for j in valores_janelas)
        
        if total_alocado == meta_num:
            st.success(f"✔ Perfeito! Grade de vagas balanceada em exatamente {total_alocado} de {meta_num} CTS.")
        elif total_alocado > meta_num:
            st.error(f"❌ Excesso: Você distribuiu {total_alocado} CTS, mas o limite físico permitido é {meta_num}.")
        else:
            st.warning(f"⚠️ Alocando: {total_alocado} de {meta_num} CTS digitados. Distribua o restante nas janelas livres.")

        # Lógica de gravação ao acionar o botão
        if btn_enviar:
            if total_alocado != meta_num:
                st.toast("Erro: A soma das janelas precisa fechar com a meta!", icon="🚨")
            else:
                # Transforma a estrutura para salvar na memória
                nova_regra = {
                    "balsa": balsa_selecionada,
                    "data": data_vigencia.strftime("%d/%m/%Y"),
                    "hora_inicio": hora_inicio.strftime("%H:%M"),
                    "config_grade": f"{qtd_janelas} janelas de {freq_horas}h",
                    "janelas_detalhe": [
                        {
                            "janela_num": j["janela_num"],
                            "horario": j["horario"],
                            "vagas": j["vagas"],
                            "ocupadas": 0,
                            "disponiveis": j["vagas"]
                        } for j in valores_janelas
                    ]
                }
                st.session_state.db_disponibilidades.append(nova_regra)
                st.toast("Disponibilidade gravada e liberada com sucesso!", icon="✨")
                st.rerun()

# ==============================================================================
# PAINEL DE OFERTAS VIGENTES NO SISTEMA
# ==============================================================================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.subheader("Painel de Ofertas Vigentes no Sistema")

if not st.session_state.db_disponibilidades:
    st.info("Nenhuma balsa cadastrada até o momento.")
else:
    # Renderiza dinamicamente cada balsa salva no estado
    for idx, item in enumerate(st.session_state.db_disponibilidades):
        with st.container():
            # Cabeçalho do Card da Balsa
            c_header1, c_header2 = st.columns([4, 1])
            with c_header1:
                st.markdown(f"""
                    <h4>⚓ {item['balsa']} &nbsp;&nbsp;
                        <span style="font-size:13px;" class="badge bg-dark">Data Vigência: {item['data']}</span>&nbsp;
                        <span style="font-size:13px;" class="badge bg-info text-dark">1º Agendamento: {item['hora_inicio']}</span>&nbsp;
                        <span style="font-size:13px;" class="badge bg-primary text-white">{item['config_grade']}</span>
                    </h4>
                """, unsafe_allow_html=True)
            with c_header2:
                # Botão para deletar a regra correspondente
                if st.button("Excluir Regra", key=f"btn_del_{idx}", type="secondary"):
                    st.session_state.db_disponibilidades.pop(idx)
                    st.toast("Regra operacional removida.", icon="🗑️")
                    st.rerun()
            
            # Tabela de Detalhes Internos
            df_janelas = pd.DataFrame(item['janelas_detalhe'])
            df_janelas.columns = [
                "Identificador", "Horário de Atendimento", "Vagas Ofertadas", "Cotas Ocupadas", "Vagas Disponíveis"
            ]
            
            # Formata a coluna Identificador para exibir o prefixo amigável
            df_janelas["Identificador"] = df_janelas["Identificador"].apply(lambda x: f"Janela #{x}")
            
            st.dataframe(df_janelas, use_container_width=True, hide_index=True)
            st.markdown("<br>", unsafe_allow_html=True)
