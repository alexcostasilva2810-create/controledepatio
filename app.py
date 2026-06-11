import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import os

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre no topo)
st.set_page_config(
    page_title="ZION TECNOLOGIA - LOGÍSTICA",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================================================================================
# DICIONÁRIO DE BALSAS OPERACIONAIS ORIGINAL PROTEGIDO
# =================================================================================
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

# =================================================================================
# CONTROLE DE ACESSO E USUÁRIOS
# =================================================================================
USUARIOS_CADASTRADOS = {
    "admin": "zion123",        
    "portaria": "patio2024",   
    "fs_cliente": "fs01"       
}

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

if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        caminho_imagem = "Gemini_Generated_Image_mz1weumz1weumz1w.png"
        
        if os.path.exists(caminho_imagem):
            st.image(caminho_imagem, use_container_width=True)
        else:
            caminho_alternativo = os.path.join(os.path.dirname(__file__), caminho_imagem)
            if os.path.exists(caminho_alternativo):
                st.image(caminho_alternativo, use_container_width=True)
            else:
                st.warning("⚠️ Imagem do cabeçalho não encontrada na raiz do projeto.")
            
        with st.container(border=True):
            user = st.text_input("Usuário / Funcionário")
            password = st.text_input("Senha de Acesso", type="password")
            if st.button("ACESSAR OPERAÇÃO", use_container_width=True):
                realizar_login(user, password)
    st.stop()

# =================================================================================
# ESTADOS DE SESSÃO E BANCO DE DADOS
# =================================================================================
if "grade_publicada" not in st.session_state:
    st.session_state.grade_publicada = {}

if "db_agendamentos" not in st.session_state:
    st.session_state.db_agendamentos = []

if "cotas_consumidas" not in st.session_state:
    st.session_state.cotas_consumidas = {}

if "modo_edicao_m1" not in st.session_state:
    st.session_state.modo_edicao_m1 = True

if "grade_trabalho" not in st.session_state:
    st.session_state.grade_trabalho = []

# ---------------------------------------------------------------------------------
# FUNÇÕES UTILITÁRIAS E QR CODE
# ---------------------------------------------------------------------------------
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
        dt_limite = datetime.combine(datetime.today(), hora_limite)
        dt_chegada = datetime.combine(datetime.today(), horario_chegada_dt.time())
        if dt_chegada > dt_limite:
            diferenca = dt_chegada - dt_limite
            return f"🚨 Atrasado ({diferenca.total_seconds() / 3600:.2f}h)"
        return "✅ No Prazo"
    except:
        return "⚠️ Erro no cálculo"

# ESTILIZAÇÃO VISUAL (CSS)
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; }
    .top-banner { background-color: #0B192C; color: white; text-align: center; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    .section-header-container { background-color: #343A40; color: white; padding: 8px 12px; border-radius: 4px 4px 0 0; font-size: 14px; font-weight: bold; margin-bottom: 12px; }
    .janela-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 12px; text-align: center; margin-bottom: 15px; }
    .tabela-header { background-color: #F1F3F5; font-weight: bold; padding: 8px; border-bottom: 2px solid #CED4DA; text-align: center; font-size: 11px; }
    .tabela-linha { padding: 6px; border-bottom: 1px solid #DEE2E6; text-align: center; font-size: 12px; display: flex; align-items: center; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="top-banner">
        <h2>ZION TECNOLOGIA - LOGÍSTICA INTEGRADA</h2>
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
# MÓDULO 1: INTELIGÊNCIA DE CÁLCULO E AJUSTE SIMÉTRICO AUTOMÁTICO
# =================================================================================
with aba1:
    col_config, col_dist = st.columns([1.2, 2])
    
    with col_config:
        st.markdown('<div class="section-header-container">⚙️ Gestão da Oferta</div>', unsafe_allow_html=True)
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("⚙️ EDITAR PARÂMETROS", use_container_width=True):
                st.session_state.modo_edicao_m1 = True
                st.rerun()
        with c_btn2:
            if st.button("💾 LOCK / SALVAR", use_container_width=True):
                if st.session_state.grade_trabalho:
                    st.session_state.grade_publicada = {
                        "balsa": st.session_state.get("m1_balsa", "SD IV"),
                        "data": st.session_state.get("m1_data", datetime.today()).strftime("%d/%m/%Y"),
                        "janelas": st.session_state.grade_trabalho
                    }
                    st.success("✅ Nova estrutura salva e publicada com sucesso!")

        st.markdown("---")
        
        balsa_sel = st.selectbox("Selecione a Embarcação", list(BALSAS_OPERACIONAIS.keys()), key="m1_balsa", disabled=not st.session_state.modo_edicao_m1)
        capacidade_nominal = BALSAS_OPERACIONAIS[balsa_sel]["capacidade"]
        cts_meta_original = BALSAS_OPERACIONAIS[balsa_sel]["cts_meta"]
        
        st.info(f"📊 **Capacidade Nominal:** {capacidade_nominal}")
        
        data_vigencia = st.date_input(
            "Data de Vigência", 
            datetime(2026, 6, 12), 
            key="m1_data", 
            format="DD/MM/YYYY",
            disabled=not st.session_state.modo_edicao_m1
        )
        
        st.markdown("**Período de Chegada na ETC:**")
        c_hora_ini, c_hora_fim = st.columns(2)
        with c_hora_ini: h_ini_str = st.selectbox("A partir de:", ["06:00", "07:00", "08:00", "09:00"], index=0, disabled=not st.session_state.modo_edicao_m1)
        with c_hora_fim: h_fim_str = st.selectbox("Até as:", ["14:00", "16:00", "18:00", "20:00", "22:00"], index=2, disabled=not st.session_state.modo_edicao_m1)
            
        intervalo_opcao = st.selectbox("Intervalo (Frequência):", ["1 hora", "2 horas"], index=0, disabled=not st.session_state.modo_edicao_m1)
        passo_horas = 1 if intervalo_opcao == "1 hora" else 2
        
        qtd_janelas_solicitadas = st.selectbox("Janelas Ofertadas:", [4, 6, 8, 12, 24], index=2, disabled=not st.session_state.modo_edicao_m1)
        exigencia_cts = st.number_input("Exigência (CTS)", min_value=1, value=int(cts_meta_original), key="m1_exigencia", disabled=not st.session_state.modo_edicao_m1)
        
        chave_verificacao = f"{balsa_sel}_{qtd_janelas_solicitadas}_{exigencia_cts}_{h_ini_str}_{h_fim_str}"
        if st.session_state.modo_edicao_m1 and st.session_state.get("ultima_chave_config") != chave_verificacao:
            lista_janelas_calculadas = []
            fmt = "%H:%M"
            dt_atual = datetime.strptime(h_ini_str, fmt)
            dt_maxima = datetime.strptime(h_fim_str, fmt)
            
            for i in range(qtd_janelas_solicitadas):
                dt_proxima = dt_atual + timedelta(hours=passo_horas)
                if dt_atual >= dt_maxima:
                    break
                str_janela = f"{dt_atual.strftime(fmt)} às {dt_proxima.strftime(fmt)}"
                lista_janelas_calculadas.append({"id": i + 1, "horario": str_janela})
                dt_atual = dt_proxima
                
            total_janelas_reais = len(lista_janelas_calculadas)
            vagas_por_janela_base = exigencia_cts // total_janelas_reais if total_janelas_reais > 0 else 0
            resto_vagas = exigencia_cts % total_janelas_reais if total_janelas_reais > 0 else 0
            
            nova_grade = []
            for idx, jan in enumerate(lista_janelas_calculadas):
                vagas_calculadas = vagas_por_janela_base + (1 if idx < resto_vagas else 0)
                nova_grade.append({"id": jan["id"], "horario": jan["horario"], "vagas_o": int(vagas_calculadas)})
            
            st.session_state.grade_trabalho = nova_grade
            st.session_state.ultima_chave_config = chave_verificacao

    with col_dist:
        st.markdown(f'<div class="section-header-container">⏱️ Distribuição de Vagas e Ajuste Dinâmico Autocompensável</div>', unsafe_allow_html=True)
        
        if st.session_state.grade_trabalho:
            total_janelas = len(st.session_state.grade_trabalho)
            cols_janelas = st.columns(4)
            
            for idx, jan in enumerate(st.session_state.grade_trabalho):
                col_id = idx % 4
                with cols_janelas[col_id]:
                    st.markdown(f'<div class="janela-card"><div style="font-size:11px;color:#718096;">JANELA #{jan["id"]}</div><div style="font-weight:bold;color:#007BFF;">{jan["horario"]}</div></div>', unsafe_allow_html=True)
                    
                    valor_atual = int(jan["vagas_o"])
                    novo_valor = st.number_input(
                        "Vagas", min_value=0, max_value=int(exigencia_cts), 
                        value=valor_atual, key=f"input_janela_{jan['id']}", 
                        label_visibility="collapsed", disabled=not st.session_state.modo_edicao_m1
                    )
                    
                    if novo_valor != valor_atual and st.session_state.modo_edicao_m1:
                        st.session_state.grade_trabalho[idx]["vagas_o"] = novo_valor
                        
                        soma_atual = sum(j["vagas_o"] for j in st.session_state.grade_trabalho)
                        diferenca = exigencia_cts - soma_atual
                        
                        indices_para_ajuste = [i for i in range(total_janelas) if i != idx]
                        
                        if indices_para_ajuste and diferenca != 0:
                            passo_compensacao = 1 if diferenca > 0 else -1
                            while diferenca != 0:
                                alterou_nesta_rodada = False
                                for i in indices_para_ajuste:
                                    if diferenca == 0:
                                        break
                                    if passo_compensacao == -1 and st.session_state.grade_trabalho[i]["vagas_o"] <= 0:
                                        continue
                                    st.session_state.grade_trabalho[i]["vagas_o"] += passo_compensacao
                                    diferenca -= passo_compensacao
                                    alterou_nesta_rodada = True
                                
                                if not alterou_nesta_rodada:
                                    break
                            st.rerun()

            soma_vagas_totais = sum(j["vagas_o"] for j in st.session_state.grade_trabalho)
            st.markdown("<br>", unsafe_allow_html=True)
            if soma_vagas_totais == exigencia_cts:
                st.success(f"🎯 **Sincronismo Perfeito:** Total Distribuído: **{soma_vagas_totais}** de **{exigencia_cts}** exigidos pelo CTS.")
            else:
                st.error(f"⚠️ **Aviso de Descompasso:** Total de vagas está em {soma_vagas_totais}, mas a exigência pede {exigencia_cts}. Ajuste as janelas manualmente.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Ofertas Ativas no Turno Corrente</div>', unsafe_allow_html=True)
    
    if st.session_state.grade_publicada:
        b_ativa = st.session_state.grade_publicada["balsa"]
        d_ativa = st.session_state.grade_publicada["data"]
        dados_tabela = []
        
        for j in st.session_state.grade_publicada["janelas"]:
            chave_consumo = f"{b_ativa}_{d_ativa}_{j['horario']}"
            consumidas = st.session_state.cotas_consumidas.get(chave_consumo, 0)
            disponiveis = j["vagas_o"] - consumidas
            dados_tabela.append({
                "Balsa": b_ativa, "Data": d_ativa, "Janela Horária": j["horario"],
                "Capacidade Máxima (Vagas)": j["vagas_o"], "Cotas Utilizadas": consumidas, "Disponibilidade Atual": disponiveis
            })
        st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma grade foi fixada/salva ainda. Defina os parâmetros e clique em 'LOCK / SALVAR'.")

# =================================================================================
# MÓDULO 2: PORTAL DE AGENDAMENTO COM VALIDAÇÃO DE DISPONIBILIDADE REAL
# =================================================================================
with aba2:
    col_cadastro, col_tabela_fs = st.columns([1.1, 2.5])
    
    with col_cadastro:
        st.markdown('<div class="section-header-container">📝 Novo Agendamento Logístico</div>', unsafe_allow_html=True)
        
        if not st.session_state.grade_publicada:
            st.warning("⚠️ Aguardando publicação da grade operacional no Módulo 1.")
        else:
            b_ativa = st.session_state.grade_publicada["balsa"]
            d_ativa = st.session_state.grade_publicada["data"]
            
            with st.form("form_novo_agendamento", clear_on_submit=True):
                st.text_input("Embarcação/Programação Vinculada", value=f"{b_ativa} ({d_ativa})", disabled=True)
                
                opcoes_seletor = []
                for j in st.session_state.grade_publicada["janelas"]:
                    chave_consumo = f"{b_ativa}_{d_ativa}_{j['horario']}"
                    consumidas = st.session_state.cotas_consumidas.get(chave_consumo, 0)
                    restantes = j["vagas_o"] - consumidas
                    status_txt = f"({restantes} vagas)" if restantes > 0 else "(ESGOTADA)"
                    opcoes_seletor.append(f"Janela #{j['id']} [{j['horario']}] {status_txt}")
                    
                janela_selecionada = st.selectbox("Escolha o Horário da Janela", opcoes_seletor)
                
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
                submetido = st.form_submit_button("🔒 CONFIRMAR AGENDAMENTO FS", use_container_width=True)
                
                if submetido:
                    id_janela_sel = int(janela_selecionada.split("#")[1].split(" ")[0])
                    janela_obj = next(j for j in st.session_state.grade_publicada["janelas"] if j["id"] == id_janela_sel)
                    janela_limpa = janela_obj["horario"]
                    
                    chave_consumo = f"{b_ativa}_{d_ativa}_{janela_limpa}"
                    consumidas = st.session_state.cotas_consumidas.get(chave_consumo, 0)
                    
                    if consumidas >= janela_obj["vagas_o"]:
                        st.error("❌ Erro: Esta janela horária esgotou a disponibilidade física!")
                    else:
                        st.session_state.cotas_consumidas[chave_consumo] = consumidas + 1
                        
                        novo_id = int(datetime.now().timestamp())
                        st.session_state.db_agendamentos.append({
                            "id": novo_id, "balsa": b_ativa, "data": d_ativa, "janela": janela_limpa,
                            "placa": placa_in, "veiculo": veiculo_in, "motorista": motorista_in,
                            "nf": nf_in, "volume": float(volume_in), "produto": produto_in,
                            "chegada_efetiva": None, "status_chegada": "Aguardando"
                        })
                        st.success("✅ Agendamento e vaga garantidos!")
                        st.rerun()

    with col_tabela_fs:
        st.markdown('<div class="section-header-container">📋 VEÍCULOS AGENDADOS (Passaporte do Carreteiro)</div>', unsafe_allow_html=True)
        pesos_colunas = [0.8, 1.0, 1.3, 1.0, 1.1, 1.5, 1.0, 1.4]
        
        c = st.columns(pesos_colunas)
        c[0].markdown('<div class="tabela-header">BALSA</div>', unsafe_allow_html=True)
        c[1].markdown('<div class="tabela-header">DATA</div>', unsafe_allow_html=True)
        c[2].markdown('<div class="tabela-header">HORÁRIO</div>', unsafe_allow_html=True)
        c[3].markdown('<div class="tabela-header">PLACA</div>', unsafe_allow_html=True)
        c[4].markdown('<div class="tabela-header">VEÍCULO</div>', unsafe_allow_html=True)
        c[5].markdown('<div class="tabela-header">MOTORISTA</div>', unsafe_allow_html=True)
        c[6].markdown('<div class="tabela-header">Nº NF</div>', unsafe_allow_html=True)
        c[7].markdown('<div class="tabela-header">PASSAPORTE</div>', unsafe_allow_html=True)
        
        for ag in st.session_state.db_agendamentos:
            l = st.columns(pesos_colunas)
            l[0].markdown(f'<div class="tabela-linha">{ag["balsa"]}</div>', unsafe_allow_html=True)
            l[1].markdown(f'<div class="tabela-linha">{ag["data"]}</div>', unsafe_allow_html=True)
            l[2].markdown(f'<div class="tabela-linha">{ag["janela"]}</div>', unsafe_allow_html=True)
            l[3].markdown(f'<div class="tabela-linha">{ag["placa"]}</div>', unsafe_allow_html=True)
            l[4].markdown(f'<div class="tabela-linha">{ag["veiculo"]}</div>', unsafe_allow_html=True)
            l[5].markdown(f'<div class="tabela-linha">{ag["motorista"]}</div>', unsafe_allow_html=True)
            l[6].markdown(f'<div class="tabela-linha">{ag["nf"]}</div>', unsafe_allow_html=True)
            
            texto_qr = obter_texto_qrcode(ag)
            bytes_qr = gerar_imagem_qrcode(texto_qr)
            l[7].download_button(
                label="📄 Imprimir Passe", data=bytes_qr, file_name=f"PASSE_{ag['placa']}.png",
                mime="image/png", key=f"qr_down_{ag['id']}", use_container_width=True
            )

# =================================================================================
# MÓDULO 3: RECEPÇÃO E APONTAMENTO (PORTARIA)
# =================================================================================
with aba3:
    st.markdown('<div class="section-header-container">📱 Recepção Digital de Portaria (Leitura de SmartPhone)</div>', unsafe_allow_html=True)
    col_scan, col_manual = st.columns([1.5, 2])
    
    with col_scan:
        st.subheader("Simulador de Scanner de Celular")
        codigo_scaneado = st.text_area("Cole aqui o texto lido pelo celular:", placeholder="ID:100\nBALSA:SD IV...", height=100)
        
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
                        
                    idx = next((i for i, item in enumerate(st.session_state.db_agendamentos) if item["id"] == id_localizado), None)
                    
                    if idx is not None:
                        ag_alvo = st.session_state.db_agendamentos[idx]
                        if ag_alvo["chegada_efetiva"] is None:
                            agora = datetime.now()
                            st.session_state.db_agendamentos[idx]["chegada_efetiva"] = agora.strftime("%H:%M:%S")
                            st.session_state.db_agendamentos[idx]["status_chegada"] = calcular_status_atraso(ag_alvo["janela"], agora)
                            st.success(f"✅ Entrada registrada para a Placa {ag_alvo['placa']}!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Este veículo já deu entrada.")
                    else:
                        st.error("❌ Código inválido ou agendamento não encontrado.")
                except:
                    st.error("❌ Formato inválido.")

    with col_manual:
        st.subheader("Check-in de Segurança Rápido")
        veiculos_nao_recebidos = [ag for ag in st.session_state.db_agendamentos if ag.get("chegada_efetiva") is None]
        
        if veiculos_nao_recebidos:
            selecionado_manual = st.selectbox("Selecione o veículo:", options=[f"ID: {v['id']} | Balsa: {v['balsa']} | Placa: {v['placa']}" for v in veiculos_nao_recebidos])
            if st.button("⏱️ REGISTRAR CHEGADA AGORA", use_container_width=True):
                id_manual = int(selecionado_manual.split("ID: ")[1].split(" |")[0])
                idx_m = next((i for i, item in enumerate(st.session_state.db_agendamentos) if item["id"] == id_manual), None)
                agora = datetime.now()
                st.session_state.db_agendamentos[idx_m]["chegada_efetiva"] = agora.strftime("%H:%M:%S")
                st.session_state.db_agendamentos[idx_m]["status_chegada"] = calcular_status_atraso(st.session_state.db_agendamentos[idx_m]["janela"], agora)
                st.rerun()
        else:
            st.info("Todos os caminhões agendados já se encontram no pátio.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header-container">📋 Painel de Controle de Tempo e Atrasos (Histórico de ETA/ETC)</div>', unsafe_allow_html=True)
    
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
        l_m3[0].markdown(f'<div class="tabela-linha">{ag["balsa"]}</div>', unsafe_allow_html=True)
        l_m3[1].markdown(f'<div class="tabela-linha">{ag["id"]}</div>', unsafe_allow_html=True)
        l_m3[2].markdown(f'<div class="tabela-linha">{ag["janela"]}</div>', unsafe_allow_html=True)
        l_m3[3].markdown(f'<div class="tabela-linha">{ag["placa"]}</div>', unsafe_allow_html=True)
        l_m3[4].markdown(f'<div class="tabela-linha">{ag["veiculo"]}</div>', unsafe_allow_html=True)
        l_m3[5].markdown(f'<div class="tabela-linha">{ag["motorista"]}</div>', unsafe_allow_html=True)
        l_m3[6].markdown(f'<div class="tabela-linha">{ag["nf"]}</div>', unsafe_allow_html=True)
        
        hora_c = ag.get("chegada_efetiva") if ag.get("chegada_efetiva") else "--:--:--"
        l_m3[7].markdown(f'<div class="tabela-linha" style="font-weight:bold; color:#1E3A8A;">{hora_c}</div>', unsafe_allow_html=True)
        
        status_c = ag.get("status_chegada") if ag.get("status_chegada") else "Aguardando"
        cor_status = "#334155" if "Aguardando" in status_c else ("#DC2626" if "Atrasado" in status_c else "#16A34A")
        l_m3[8].markdown(f'<div class="tabela-linha" style="color:{cor_status}; font-weight:bold;">{status_c}</div>', unsafe_allow_html=True)
