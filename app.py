import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import qrcode
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre no topo)
st.set_page_config(
    page_title="ZION TECNOLOGIA - LOGÍSTICA",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================================================================================
# DICIONÁRIO DE BALSAS OPERACIONAIS ORIGINAL RESTAURADO
# =================================================================================
BALSAS_OPERACIONAIS = {
    "SD I": {"capacidade": "1040.4 m³", "cts_meta": 17}, 
    "SD II": {"capacidade": "1530.0 m³", "cts_meta": 25},
    "SD IV": {"capacidade": "2325.6 m³", "cts_meta": 38}, 
    "SD V": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD VI": {"capacidade": "1407.6 m³", "cts_meta": 23}, 
    "SD VII": {"capacidade": "1468.8 m³", "cts_meta": 24}, # Corrigido cta_meta para cts_meta
    "SD VIII": {"capacidade": "1407.6 m³", "cts_meta": 23}, 
    "SD IX": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD X": {"capacidade": "1407.6 m³", "cts_meta": 23}, 
    "SD XI": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD XII": {"capacidade": "2325.6 m³", "cts_meta": 38}, 
    "SD XIII": {"capacidade": "2325.6 m³", "cts_meta": 38},
    "SD XIV": {"capacidade": "1468.8 m³", "cts_meta": 24}, 
    "SD XV": {"capacidade": "1407.6 m³", "cts_meta": 23},
    "SD XVI": {"capacidade": "1407.6 m³", "cts_meta": 23}, 
    "SD XVII": {"capacidade": "1468.8 m³", "cts_meta": 24}, # Corrigido qs_meta para cts_meta
    "SD XVIII": {"capacidade": "795.6 m³", "cts_meta": 13}, 
    "SD XX": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXI": {"capacidade": "2998.8 m³", "cts_meta": 49}, 
    "SD XXII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXIII": {"capacidade": "2998.8 m³", "cts_meta": 49}, 
    "TWB 200": {"capacidade": "2142.0 m³", "cts_meta": 35}
}

# =================================================================================
# ESPAÇO PARA CADASTRO DE FUNCIONÁRIOS
# =================================================================================
USUARIOS_CADASTRADOS = {
    "admin": "zion123",        
    "portaria": "patio2024",   
    "fs_cliente": "fs01"       
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
# TELA DE LOGIN
# ---------------------------------------------------------------------------------
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
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
    st.stop()

# =================================================================================
# ESTRUTURA DE DADOS (ESTADOS DE SESSÃO)
# =================================================================================
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
            "id": 100, "balsa": "SD II", "data": "12/06/2026", "janela": "07:00 às 08:00",
            "placa": "JVV-7606", "veiculo": "BITREN", "motorista": "JOSE FRANCISCO",
            "nf": "154639", "volume": 51000.00, "produto": "ANIDRO", 
            "arquivo_nome": "Nota_Fiscal_154639.pdf", "conteudo_bytes": b"",
            "chegada_efetiva": None, "status_chegada": "Aguardando"
        }
    ]

# GERAÇÃO DO TEXTO DO PASSPORT INTEGRADO
def obter_texto_qrcode(agendamento_dict):
    return (
        f"ID:{agendamento_dict['id']}\n"
        f"BALSA:{agendamento_dict['balsa']}\n"
        f"PLACA:{agendamento_dict['placa']}\n"
        f"MOTORISTA:{agendamento_dict['motorista']}\n"
        f"JANELA:{agendamento_dict['janela']}\n"
        f"NF:{agendamento_dict['nf']}"
    )

def gerar_imagem_qrcode(texto):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def calcular_status_atraso(janela_str, horario_chegada_dt):
    try:
        hora_limite_str = janela_str.split(" às ")[1].strip()
        hora_limite = datetime.strptime(hora_limite_str, "%H:%M").time()
        chegada_time = horario_chegada_dt.time()
        hoje = datetime.today()
        dt_limite = datetime.combine(hoje, hora_limite)
        dt_chegada = datetime.combine(hoje, chegada_time)
        
        if dt_chegada > dt_limite:
            diferenca = dt_chegada - dt_limite
            horas_atraso = diferenca.total_seconds() / 3600
            return f"🚨 Atrasado ({horas_atraso:.2f}h)"
        else:
            return "✅ No Prazo"
    except Exception:
        return "⚠️ Erro no cálculo"

# ESTILIZAÇÃO VISUAL (CSS)
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .top-banner { background-color: #0B192C; color: white; text-align: center; padding: 20px 10px; border-radius: 4px; margin-bottom: 20px; }
    .top-banner h1 { margin: 0; font-size: 24px; font-weight: bold; }
    .section-header-container { background-color: #343A40; color: white; padding: 8px 12px; border-radius: 4px 4px 0 0; font-size: 14px; font-weight: bold; margin-bottom: 12px; }
    .janela-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 12px; text-align: center; margin-bottom: 15px; }
    
    div.stButton > button[key="btn_publicar_grade"] {
        background-color: #1E3A8A !important; color: white !important; border: 1px solid #172554 !important; width: 100%; font-weight: bold !important; padding: 12px !important; border-radius: 6px !important;
    }
    .tabela-header { background-color: #F1F3F5; font-weight: bold; padding: 8px; border-bottom: 2px solid #CED4DA; text-align: center; font-size: 11px; }
    .tabela-linha { padding: 6px; border-bottom: 1px solid #DEE2E6; text-align: center; font-size: 12px; display: flex; align-items: center; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="top-banner">
        <h1>ZION TECNOLOGIA - LOGÍSTICA INTEGRADA</h1>
        <p>Controle Operacional de Pátio, Docas e Recepção de Fluxo | Operador: {st.session_state.usuario_logado.upper()}</p>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 ENCERRAR SESSÃO"):
    realizar_logout()

aba1, aba2, aba3 = st.tabs([
    "⚓ MÓDULO 1: Gestão de Disponibilidade (GD)", 
    "🚛 MÓDULO 2: Portal de Agendamento (Cliente FS)",
    "📱 MÓDULO 3: Recepção e Apontamento (Portaria ETC)"
])

# =================================================================================
# MÓDULO 1: GESTÃO DE DISPONIBILIDADE
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1.2, 2])
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        
        # Puxa a lista real das chaves do dicionário de balsas
        balsa_selecionada_m1 = st.selectbox("Selecione a Embarcação", list(BALSAS_OPERACIONAIS.keys()), key="m1_balsa")
        
        # Busca automática dos dados da balsa selecionada
        dados_balsa_atual = BALSAS_OPERACIONAIS[balsa_selecionada_m1]
        st.info(f"📊 **Capacidade Nominal:** {dados_balsa_atual['capacidade']}")
        
        st.date_input("Data de Vigência", datetime(2026, 6, 12), key="m1_data")
        
        st.markdown("**Período de Chegada na ETC:**")
        c_hora_ini, c_hora_fim = st.columns(2)
        with c_hora_ini: hora_inicio = st.selectbox("A partir de:", ["06:00", "07:00", "08:00", "09:00", "18:00"], index=1)
        with c_hora_fim: hora_fim = st.selectbox("Até as:", ["17:00", "18:00", "19:00", "20:00", "22:00"], index=1)
            
        c_int, c_qtd_jan = st.columns(2)
        with c_int: intervalo_janela = st.selectbox("Intervalo (Frequência):", ["1 hora", "2 horas"], index=0)
        with c_qtd_jan: qtd_janelas = st.selectbox("Janelas Ofertadas:", [6, 8, 12, 24], index=1)
            
        # Puxa automaticamente o valor cts_meta cadastrado no seu dicionário
        exigencia_cts = st.number_input("Exigência (CTS)", min_value=0, value=int(dados_balsa_atual["cts_meta"]))
        
        if st.button("🔄 PUBLICAR E CONFIGURAR GRADE", key="btn_publicar_grade"):
            st.success(f"Nova grade para a balsa {balsa_selecionada_m1} publicada com sucesso!")

    with col_dist:
        st.markdown(f'<div class="section-header-container">⏱️ Distribuição de Vagas</div>', unsafe_allow_html=True)
        cols_janelas = st.columns(4)
        for idx, of in enumerate(st.session_state.ofertas):
            col_id = idx % 4
            with cols_janelas[col_id]:
                st.markdown(f'<div class="janela-card"><div style="font-size:11px;color:#718096;">JANELA #{of["id"]}</div><div style="font-weight:bold;color:#007BFF;">{of["horario"]}</div></div>', unsafe_allow_html=True)
                st.number_input("Vagas", min_value=0, value=of['vagas_o'], key=f"v_m1_{of['id']}", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Ofertas Vigentes no Sistema</div>', unsafe_allow_html=True)
    df_of = pd.DataFrame(st.session_state.ofertas)
    df_of.columns = ['IDENTIFICADOR', 'HORÁRIO DE ATENDIMENTO', 'VAGAS OFERTADAS', 'COTAS OCUPADAS']
    df_of['VAGAS DISPONÍVEIS'] = df_of['VAGAS OFERTADAS'] - df_of['COTAS OCUPADAS']
    st.dataframe(df_of, use_container_width=True, hide_index=True)

# =================================================================================
# MÓDULO 2: PORTAL DE AGENDAMENTO (GERAÇÃO DE PASSAPORTE)
# =================================================================================
with aba2:
    col_cadastro, col_tabela_fs = st.columns([1.1, 2.5])
    with col_cadastro:
        st.markdown('<div class="section-header-container">📝 Novo Agendamento Logístico</div>', unsafe_allow_html=True)
        with st.form("form_novo_agendamento", clear_on_submit=True):
            balsa_selecionada_ag = st.selectbox("1. SELECIONE A EMBARCAÇÃO", [f"{b} ({BALSAS_OPERACIONAIS[b]['capacidade']})" for b in BALSAS_OPERACIONAIS.keys()])
            
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
                
            arq_upload = st.file_uploader("ANEXAR NOTA FISCAL (PDF)", type=["pdf"])
            submetido = st.form_submit_button("🔒 CONFIRMAR AGENDAMENTO FS")
            
            if submetido:
                partes_janela = janela_selecionada.split("#")
                id_janela_sel = int(partes_janela[1].split(" ")[0])
                index_janela = next((index for (index, d) in enumerate(st.session_state.ofertas) if d["id"] == id_janela_sel), None)
                vagas_restantes = st.session_state.ofertas[index_janela]['vagas_o'] - st.session_state.ofertas[index_janela]['cotas_o']
                
                if vagas_restantes <= 0:
                    st.error("❌ Erro: Esta janela horária está esgotada!")
                else:
                    st.session_state.ofertas[index_janela]['cotas_o'] += 1
                    janela_limpa = st.session_state.ofertas[index_janela]['horario']
                    balsa_nome_limpo = balsa_selecionada_ag.split(" (")[0]
                    
                    binario_doc = arq_upload.read() if arq_upload else b""
                    nome_documento = arq_upload.name if arq_upload else f"Nota_{nf_in}.pdf"
                    
                    novo_id = int(datetime.now().timestamp())
                    st.session_state.db_agendamentos.append({
                        "id": novo_id, "balsa": balsa_nome_limpo, "data": "12/06/2026", "janela": janela_limpa,
                        "placa": placa_in, "veiculo": veiculo_in, "motorista": motorista_in,
                        "nf": nf_in, "volume": float(volume_in), "produto": produto_in,
                        "arquivo_nome": nome_documento, "conteudo_bytes": binario_doc,
                        "chegada_efetiva": None, "status_chegada": "Aguardando"
                    })
                    st.success("✅ Agendamento registrado com sucesso!")
                    st.rerun()

    with col_tabela_fs:
        st.markdown('<div class="section-header-container">📋 VEÍCULOS AGENDADOS (Emissão do Passe do Carreteiro)</div>', unsafe_allow_html=True)
        pesos_colunas = [0.8, 1.0, 1.3, 1.0, 1.1, 1.5, 1.0, 1.4]
        
        c = st.columns(pesos_colunas)
        c[0].markdown('<div class="tabela-header">BALSA</div>', unsafe_allow_html=True)
        c[1].markdown('<div class="tabela-header">DATA</div>', unsafe_allow_html=True)
        c[2].markdown('<div class="tabela-header">HORÁRIO</div>', unsafe_allow_html=True)
        c[3].markdown('<div class="tabela-header">PLACA</div>', unsafe_allow_html=True)
        c[4].markdown('<div class="tabela-header">VEÍCULO</div>', unsafe_allow_html=True)
        c[5].markdown('<div class="tabela-header">MOTORISTA</div>', unsafe_allow_html=True)
        c[6].markdown('<div class="tabela-header">Nº NF</div>', unsafe_allow_html=True)
        c[7].markdown('<div class="tabela-header">PASSAPORTE CARRETEIRO</div>', unsafe_allow_html=True)
        
        for idx, ag in enumerate(st.session_state.db_agendamentos):
            l = st.columns(pesos_colunas)
            l[0].markdown(f'<div class="tabela-linha">{ag.get("balsa")}</div>', unsafe_allow_html=True)
            l[1].markdown(f'<div class="tabela-linha">{ag.get("data")}</div>', unsafe_allow_html=True)
            l[2].markdown(f'<div class="tabela-linha">{ag.get("janela")}</div>', unsafe_allow_html=True)
            l[3].markdown(f'<div class="tabela-linha">{ag.get("placa")}</div>', unsafe_allow_html=True)
            l[4].markdown(f'<div class="tabela-linha">{ag.get("veiculo")}</div>', unsafe_allow_html=True)
            l[5].markdown(f'<div class="tabela-linha">{ag.get("motorista")}</div>', unsafe_allow_html=True)
            l[6].markdown(f'<div class="tabela-linha">{ag.get("nf")}</div>', unsafe_allow_html=True)
            
            texto_qr = obter_texto_qrcode(ag)
            bytes_qr = gerar_imagem_qrcode(texto_qr)
            
            l[7].download_button(
                label="📄 Imprimir Passe",
                data=bytes_qr,
                file_name=f"PASSAPORTE_ZION_{ag['placa']}.png",
                mime="image/png",
                key=f"qr_down_{ag['id']}",
                use_container_width=True
            )

# =================================================================================
# MÓDULO 3: RECEPÇÃO E APONTAMENTO (DESCARGA COMPLETA VIA PORTARIA)
# =================================================================================
with aba3:
    st.markdown('<div class="section-header-container">📱 Recepção Digital de Portaria</div>', unsafe_allow_html=True)
    col_scan, col_manual = st.columns([1.5, 2])
    
    with col_scan:
        st.subheader("Simulador de Scanner de Celular")
        codigo_scaneado = st.text_area("Cole aqui o texto lido pelo celular (do passaporte do carreteiro):", 
                                       placeholder="ID:100\nBALSA:SD II\nPLACA:JVV-7606...", height=100)
        
        if st.button("📥 PROCESSAR ENTRADA IMEDIATA", use_container_width=True):
            if codigo_scaneado:
                try:
                    linhas = codigo_scaneado.split("\n")
                    id_localizado = None
                    for linha in linhas:
                        if "ID:" in linha:
                            id_localizado = int(linha.split(":")[1].strip())
                            break
                    
                    if id_localizado is None:
                        id_localizado = int(codigo_scaneado.strip())
                        
                    idx_encontrado = next((i for i, item in enumerate(st.session_state.db_agendamentos) if item["id"] == id_localizado), None)
                    
                    if idx_encontrado is not None:
                        ag_alvo = st.session_state.db_agendamentos[idx_encontrado]
                        if ag_alvo.get("chegada_efetiva") is None:
                            agora = datetime.now()
                            st.session_state.db_agendamentos[idx_encontrado]["chegada_efetiva"] = agora.strftime("%H:%M:%S")
                            st.session_state.db_agendamentos[idx_encontrado]["status_chegada"] = calcular_status_atraso(ag_alvo["janela"], agora)
                            st.success(f"✅ Entrada registrada para a Placa {ag_alvo['placa']} na balsa {ag_alvo['balsa']} às {agora.strftime('%H:%M:%S')}!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Este veículo já teve sua chegada registrada anteriormente.")
                    else:
                        st.error("❌ Código inválido ou agendamento não encontrado.")
                except Exception:
                    st.error("❌ Formato de QR Code não reconhecido.")

    with col_manual:
        st.subheader("Check-in de Segurança Rápido")
        veiculos_nao_recebidos = [ag for ag in st.session_state.db_agendamentos if ag.get("chegada_efetiva") is None]
        if veiculos_nao_recebidos:
            selecionado_manual = st.selectbox("Selecione o veículo para dar entrada:", 
                                              options=[f"ID: {v['id']} | Balsa: {v['balsa']} | Placa: {v['placa']} - Mot: {v['motorista']}" for v in veiculos_nao_recebidos])
            if st.button("⏱️ REGISTRAR CHEGADA AGORA", use_container_width=True):
                id_manual = int(selecionado_manual.split("ID: ")[1].split(" |")[0])
                idx_m = next((i for i, item in enumerate(st.session_state.db_agendamentos) if item["id"] == id_manual), None)
                agora = datetime.now()
                st.session_state.db_agendamentos[idx_m]["chegada_efetiva"] = agora.strftime("%H:%M:%S")
                st.session_state.db_agendamentos[idx_m]["status_chegada"] = calcular_status_atraso(st.session_state.db_agendamentos[idx_m]["janela"], agora)
                st.toast("Entrada manual efetuada!")
                st.rerun()
        else:
            st.info("Todos os caminhões agendados já se encontram no porto ou pátio.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Painel de Controle de Tempo e Atrasos (Histórico Completo)</div>', unsafe_allow_html=True)
    
    pesos_m3 = [0.8, 1.2, 1.5, 1.0, 1.2, 1.5, 1.0, 1.2, 1.2]
    c_m3 = st.columns(pesos_m3)
    c_m3[0].markdown('<div class="tabela-header">BALSA</div>', unsafe_allow_html=True)
    c_m3[1].markdown('<div class="tabela-header">ID</div>', unsafe_allow_html=True)
    c_m3[2].markdown('<div class="tabela-header">JANELA PROGRAMADA</div>', unsafe_allow_html=True)
    c_m3[3].markdown('<div class="tabela-header">PLACA</div>', unsafe_allow_html=True)
    c_m3[4].markdown('<div class="tabela-header">VEÍCULO</div>', unsafe_allow_html=True)
    c_m3[5].markdown('<div class="tabela-header">MOTORISTA</div>', unsafe_allow_html=True)
    c_m3[6].markdown('<div class="tabela-header">Nº NF</div>', unsafe_allow_html=True)
    c_m3[7].markdown('<div class="tabela-header">HORA REAL CHEGADA</div>', unsafe_allow_html=True)
    c_m3[8].markdown('<div class="tabela-header">STATUS OPERACIONAL</div>', unsafe_allow_html=True)
    
    for ag in st.session_state.db_agendamentos:
        l_m3 = st.columns(pesos_m3)
        l_m3[0].markdown(f'<div class="tabela-linha">{ag.get("balsa")}</div>', unsafe_allow_html=True)
        l_m3[1].markdown(f'<div class="tabela-linha">{ag.get("id")}</div>', unsafe_allow_html=True)
        l_m3[2].markdown(f'<div class="tabela-linha">{ag.get("janela")}</div>', unsafe_allow_html=True)
        l_m3[3].markdown(f'<div class="tabela-linha">{ag.get("placa")}</div>', unsafe_allow_html=True)
        l_m3[4].markdown(f'<div class="tabela-linha">{ag.get("veiculo")}</div>', unsafe_allow_html=True)
        l_m3[5].markdown(f'<div class="tabela-linha">{ag.get("motorista")}</div>', unsafe_allow_html=True)
        l_m3[6].markdown(f'<div class="tabela-linha">{ag.get("nf")}</div>', unsafe_allow_html=True)
        
        hora_c = ag.get("chegada_efetiva") if ag.get("chegada_efetiva") else "--:--:--"
        l_m3[7].markdown(f'<div class="tabela-linha" style="font-weight:bold; color:#1E3A8A;">{hora_c}</div>', unsafe_allow_html=True)
        
        status_c = ag.get("status_chegada") if ag.get("status_chegada") else "Aguardando"
        cor_status = "#334155" if "Aguardando" in status_c else ("#DC2626" if "Atrasado" in status_c else "#16A34A")
        l_m3[8].markdown(f'<div class="tabela-linha" style="color:{cor_status}; font-weight:bold;">{status_c}</div>', unsafe_allow_html=True)
