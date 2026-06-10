import streamlit as st

# Exemplo de dados recuperados do banco de dados/state
# (Certifique-se de que os nomes das colunas batem com o seu DataFrame original)
agendamentos = [
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
        "arquivo_bytes": b"..." # Conteúdo binário do PDF vindo do seu banco/storage
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
        "arquivo_bytes": b"..."
    }
]

st.markdown("### 📜 Comprovantes de Agendamento Emitidos")

# Iterando sobre cada agendamento para criar os blocos visuais idênticos ao solicitado
for idx, ag in enumerate(agendamentos):
    # Criamos um container com uma borda leve para simular o card da imagem
    with st.container(border=True):
        # Divisão de colunas: Dados à esquerda (9/10) e botões de ação à direita (1/10)
        col_dados, col_acoes = st.columns([9, 1.5])
        
        with col_dados:
            # Linha 1: Informações principais da viagem
            st.markdown(
                f"**BALSA:** {ag['balsa']} | **DATA:** {ag['data']} | **HORÁRIO:** {ag['janela']}"
            )
            # Linha 2: Informações do veículo e condutor
            st.markdown(
                f"**PLACA:** {ag['placa']} | **VEÍCULO:** {ag['veiculo']} | **MOTORISTA:** {ag['motorista']}"
            )
            # Linha 3: Detalhes da Carga e documento fiscal
            # Nota: Corrigido o erro de sintaxe de formatação que gerava o ValueError anterior
            st.markdown(
                f"**Nº NF:** {ag['nf']} | **VOLUME:** {ag['volume']:.2f} m³ | **PRODUTO:** {ag['produto']} | **ANEXO:** {ag['arquivo_nome']}"
            )
            
        with col_acoes:
            # Espaçamento para alinhar os botões verticalmente ao centro do card
            st.write("")
            
            # 1. Botão de Editar Registro
            if st.button("📝 Editar", key=f"edit_btn_{idx}", use_container_width=True):
                st.session_state[f"editando_{idx}"] = True
                # Insira aqui a sua lógica para abrir o formulário preenchido para edição
            
            # 2. Botão de Download Nativo da NF (Funciona perfeitamente em ambos os módulos)
            # Substitua 'ag['arquivo_bytes']' pela variável que armazena o arquivo PDF real do banco
            st.download_button(
                label="📄 PDF",
                data=ag.get("arquivo_bytes", b""), 
                file_name=ag["arquivo_name"],
                mime="application/pdf",
                key=f"download_nf_{idx}",
                use_container_width=True
            )
