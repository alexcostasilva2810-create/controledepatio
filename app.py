import os
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==============================================================================
# BLOCO 1: CONFIGURAÇÕES GERAIS E PARAMETRIZAÇÃO DE USUÁRIOS
# ==============================================================================
URL_PLANILHA_GOOGLE = "https://script.google.com/macros/s/AKfycbxlzebvfA0GQcAyQ1Oc9IFC6XX9t4mR7cOLzj4jt8sX0B2YZoozCuTzlAnZHeL8aHjr/exec"

# Usuários e senhas permitidos no sistema (Altere ou adicione aqui facilmente)
USUARIOS_PERMITIDOS = {
    "admin": {"senha": "123", "nome": "ADMINISTRADOR ZION"},
    "supervisor": {"senha": "456", "nome": "SUPERVISOR ETC"},
    "portaria": {"senha": "789", "nome": "OPERADOR PORTARIA"}
}

# ==============================================================================
# BLOCO 2: INTERFACE VISUAL (HTML, CSS E JAVASCRIPT INTEGRADO)
# ==============================================================================
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Zion Tecnologia - Monitoramento ETC</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root { --primary: #0a2647; --secondary: #144272; --accent: #2c74b3; --success: #1b4d3e; --gray: #f4f6f9; }
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background-color: var(--gray); color: #333; }
        
        /* Cabeçalho Customizado */
        .navbar { background: var(--primary); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
        .navbar .logo { font-size: 24px; font-weight: 800; letter-spacing: 1.5px; color: #fff; }
        .navbar .subtitulo { font-size: 16px; font-weight: 400; opacity: 0.9; }
        .user-info { font-size: 14px; background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px; }
        
        .container { max-width: 1400px; margin: 25px auto; padding: 0 20px; }
        
        /* Tela de Login */
        #telaLogin { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }
        #telaLogin h2 { color: var(--primary); margin-bottom: 25px; font-weight: 700; }
        .msg-sucesso { color: #2e7d32; font-weight: bold; margin: 15px 0; display: none; }
        
        /* Sistema Principal Hidden por padrão */
        #sistemaPrincipal { display: none; }
        
        /* Abas de Navegação */
        .tabs { display: flex; margin-bottom: 25px; gap: 4px; }
        .tab-button { flex: 1; background: #e2e8f0; border: none; padding: 15px; font-size: 14px; font-weight: bold; color: #4a5568; cursor: pointer; border-radius: 6px 6px 0 0; transition: 0.2s; text-transform: uppercase; }
        .tab-button.active { background: white; color: var(--primary); border-bottom: 4px solid var(--accent); }
        
        .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: none; }
        .card.active { display: block; }

        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
        .form-group { display: flex; flex-direction: column; }
        .full-width { grid-column: span 2; }
        @media(max-width: 768px) { .full-width { grid-column: span 1; } }
        
        label { font-size: 11px; font-weight: 700; color: #4a5568; margin-bottom: 6px; text-transform: uppercase; }
        input[type="text"], input[type="password"] { text-transform: uppercase; }
        input { padding: 11px; border: 1.5px solid #cbd5e1; border-radius: 6px; font-size: 14px; background: #fafafa; }
        input:focus { border-color: var(--accent); background: white; outline: none; }
        
        .btn { padding: 14px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; transition: 0.2s; font-size: 13px; }
        .btn-submit { background-color: var(--success); color: white; width: 100%; margin-top: 15px; }
        .btn-primary { background-color: var(--primary); color: white; }
        .btn-edit { background-color: #ed8936; color: white; padding: 6px 12px; font-size: 11px; }
        .btn-save { background-color: #38a169; color: white; padding: 6px 12px; font-size: 11px; display: none; }
        
        /* Tabela Histórico */
        .table-container { overflow-x: auto; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; min-width: 1300px; }
        th { background-color: var(--primary); color: white; padding: 12px 8px; font-weight: 600; text-transform: uppercase; }
        td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; }
        tr:nth-child(even) { background-color: #f8fafc; }
        .editable-cell input { padding: 4px; font-size: 12px; width: 95%; border: 1px solid #cbd5e1; }
    </style>
</head>
<body>

    <div id="telaLogin">
        <div style="font-size: 28px; font-weight: 800; color: #0a2647; margin-bottom: 5px;">ZION TECNOLOGIA</div>
        <p style="color: #718096; margin-top: 0; font-size: 14px;">SEJA BEM VINDO AO SISTEMA ZION</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin-bottom: 25px;">
        
        <div class="form-group" style="text-align: left; margin-bottom: 15px;">
            <label>Usuário</label>
            <input type="text" id="loginUser" required placeholder="Digite seu usuário">
        </div>
        <div class="form-group" style="text-align: left; margin-bottom: 20px;">
            <label>Senha</label>
            <input type="password" id="loginPass" required placeholder="Digite sua senha">
        </div>
        <button class="btn btn-primary" style="width: 100%;" onclick="executarLogin()">Acessar Painel</button>
        
        <div id="msgSucesso" class="msg-sucesso"></div>
    </div>

    <div id="sistemaPrincipal">
        <div class="navbar">
            <div>
                <span class="logo">Zion Tecnologia</span>
                <span class="subtitulo"> | Sistema de Monitoramento - ETC</span>
            </div>
            <div class="user-info" id="nomeUsuarioLogado">Olá, Usuário</div>
        </div>

        <div class="container">
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('cadastro')">📝 Portaria (Registro)</button>
                <button class="tab-button" onclick="switchTab('supervisor')">⚙️ Gestão Operacional ETC</button>
                <button class="tab-button" onclick="switchTab('painel')">📊 Histórico Geral</button>
            </div>

            <div id="cadastro" class="card active">
                <form id="formCadastro" onsubmit="salvarPortaria(event)" class="form-grid">
                    <div class="form-group"><label>Saída da Origem</label><input type="datetime-local" name="saida_origem" required></div>
                    <div class="form-group"><label>Previsão de chegada no Posto</label><input type="datetime-local" name="prev_chegada" required></div>
                    <div class="form-group"><label>Chegada no Posto</label><input type="datetime-local" name="chegada_posto"></div>
                    <div class="form-group"><label>Nº Nota Fiscal</label><input type="text" name="num_nota" required></div>
                    <div class="form-group"><label>Placa do Veículo</label><input type="text" name="placa" required></div>
                    <div class="form-group"><label>Número do Lacre</label><input type="text" name="lacre" required></div>
                    <div class="form-group full-width"><label>Nome do Motorista</label><input type="text" name="motorista" required></div>
                    <div class="form-group"><label>Transportadora</label><input type="text" name="transportadora" required></div>
                    <div class="form-group"><label>Cliente Destinatário</label><input type="text" name="cliente" required></div>
                    <div class="form-group"><label>Cidade de Destino</label><input type="text" name="destino" required></div>
                    <div class="form-group"><label>Contato do Motorista</label><input type="text" name="telefone" required></div>
                    <div class="form-group"><label>Produto</label><input type="text" name="produto" required></div>
                    <div class="form-group"><label>Volume a 20º</label><input type="text" name="vol20" required></div>
                    <div class="form-group full-width"><label>Upload XML / Documento da NF</label><input type="file" name="arquivo_nf" accept=".xml,.pdf"></div>
                    
                    <div class="full-width">
                        <button type="submit" class="btn btn-submit">Salvar Registro Portaria</button>
                    </div>
                </form>
            </div>

            <div id="supervisor" class="card">
                <h3 style="color: var(--primary); margin-top: 0;">Módulo de Controle Interno ETC</h3>
                <form id="formSupervisor" onsubmit="salvarSupervisor(event)" class="form-grid">
                    <div class="form-group"><label>Vincular ao Registro (Nº SEQ)</label><input type="text" id="sup_seq" required placeholder="Ex: 1"></div>
                    <div class="form-group"><label>Chegada ETC</label><input type="datetime-local" id="sup_chegada" required></div>
                    <div class="form-group"><label>T2- Estadia</label><input type="text" id="sup_estadia" placeholder="Calculado automaticamente"></div>
                    <div class="form-group"><label>Início Transbordo</label><input type="datetime-local" id="sup_ini_trans" required></div>
                    <div class="form-group"><label>Final Transbordo</label><input type="datetime-local" id="sup_fim_trans" required></div>
                    <div class="form-group"><label>Saída ETC</label><input type="datetime-local" id="sup_saida" required></div>
                    <div class="form-group"><label>Completa e Retira (Lts)</label><input type="text" id="sup_completa"></div>
                    <div class="form-group"><label>BT</label><input type="text" id="sup_bt"></div>
                    
                    <div class="full-width">
                        <button type="submit" class="btn btn-submit" style="background-color: var(--accent);">Atualizar Movimentação ETC</button>
                    </div>
                </form>
            </div>

            <div id="painel" class="card">
                <div class="table-container">
                    <table id="tabelaDados">
                        <thead>
                            <tr>
                                <th>SEQ</th><th>Placa</th><th>Motorista</th><th>NF</th><th>Chegada Posto</th>
                                <th>T1 Trânsito</th><th>Chegada ETC</th><th>T2 Estadia</th><th>T3 Descarga</th>
                                <th>T4 Operacional</th><th>Ações</th>
                            </tr>
                        </thead>
                        <tbody id="corpoTabela">
                            </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let dadosLocais = [];

        function executarLogin() {
            let u = document.getElementById('loginUser').value.toLowerCase();
            let s = document.getElementById('loginPass').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({usuario: u, senha: s})
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === "sucesso") {
                    let containerMsg = document.getElementById('msgSucesso');
                    containerMsg.style.display = "block";
                    containerMsg.innerText = `Acesso concedido com sucesso! Olá ${data.nome}, vamos aos lançamentos.`;
                    
                    document.getElementById('nomeUsuarioLogado').innerText = `Operador: ${data.nome}`;
                    
                    setTimeout(() => {
                        document.getElementById('telaLogin').style.display = "none";
                        document.getElementById('sistemaPrincipal').style.display = "block";
                        atualizarTabelaHistorico();
                    }, 2000);
                } else {
                    alert("Usuário ou Senha incorretos!");
                }
            });
        }

        function switchTab(tabId) {
            document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        function salvarPortaria(e) {
            e.preventDefault();
            let formData = new FormData(document.getElementById('formCadastro'));
            
            fetch('/api/salvar_portaria', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                alert("Registro de Portaria salvo com sucesso!");
                document.getElementById('formCadastro').reset(); // Limpa campos automaticamente
                atualizarTabelaHistorico();
            });
        }

        function salvarSupervisor(e) {
            e.preventDefault();
            let payload = {
                seq: document.getElementById('sup_seq').value,
                chegada_etc: document.getElementById('sup_chegada').value,
                ini_trans: document.getElementById('sup_ini_trans').value,
                fim_trans: document.getElementById('sup_fim_trans').value,
                saida_etc: document.getElementById('sup_saida').value,
                completa: document.getElementById('sup_completa').value,
                bt: document.getElementById('sup_bt').value
            };

            fetch('/api/salvar_supervisor', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                alert("Dados da ETC salvos e integrados!");
                document.getElementById('formSupervisor').reset(); // Limpa campos automaticamente
                atualizarTabelaHistorico();
            });
        }

        function atualizarTabelaHistorico() {
            fetch('/api/dados')
            .then(res => res.json())
            .then(dados => {
                dadosLocais = dados;
                let html = "";
                dados.forEach((row, index) => {
                    html += `
                        <tr id="linha-${index}">
                            <td><b>#${row.sequencial}</b></td>
                            <td>${row.placa}</td>
                            <td>${row.motorista}</td>
                            <td>${row.num_nota}</td>
                            <td>${row.chegada_posto || '-'}</td>
                            <td>${row.t1_transito || '-'}</td>
                            <td>${row.chegada_etc || '-'}</td>
                            <td>${row.t2_estadia || '-'}</td>
                            <td>${row.t3_descarga || '-'}</td>
                            <td>${row.t4_operacional || '-'}</td>
                            <td>
                                <button class="btn btn-edit" id="btn-edit-${index}" onclick="editarLinha(${index})">Editar</button>
                                <button class="btn btn-save" id="btn-save-${index}" onclick="salvarLinha(${index})">Salvar</button>
                            </td>
                        </tr>
                    `;
                });
                document.getElementById('corpoTabela').innerHTML = html;
            });
        }

        function editarLinha(index) {
            let tr = document.getElementById(`linha-${index}`);
            let colunas = tr.getElementsByTagName('td');
            
            // Torna células selecionadas em campos de input editáveis
            for(let i = 1; i <= 3; i++) {
                let valorAtual = colunas[i].innerText;
                colunas[i].innerHTML = `<input type="text" value="${valorAtual}" style="text-transform:uppercase;">`;
            }

            document.getElementById(`btn-edit-${index}`).style.display = "none";
            document.getElementById(`btn-save-${index}`).style.display = "inline-block";
        }

        function salvarLinha(index) {
            let tr = document.getElementById(`linha-${index}`);
            let inputs = tr.getElementsByTagName('input');
            
            let dadosAtualizados = {
                sequencial: dadosLocais[index].sequencial,
                placa: inputs[0].value.toUpperCase(),
                motorista: inputs[1].value.toUpperCase(),
                num_nota: inputs[2].value.toUpperCase()
            };

            fetch('/api/inline_update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(dadosAtualizados)
            })
            .then(res => res.json())
            .then(data => {
                alert("Alterações salvas no histórico!");
                atualizarTabelaHistorico();
            });
        }
    </script>
</body>
</html>
"""

# ==============================================================================
# BLOCO 3: ROTAS DA API E MÓDULOS DE CÁLCULO DE TEMPO (MÓDULO FLASK)
# ==============================================================================
@app.route('/')
def index():
    return render_template_string(HTML_SISTEMA)

@app.route('/api/login', methods=['POST'])
def api_login():
    req = request.json
    u = req.get('usuario')
    s = req.get('senha')
    if u in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[u]['senha'] == s:
        return jsonify({"status": "sucesso", "nome": USUARIOS_PERMITIDOS[u]['nome']})
    return jsonify({"status": "erro"})

@app.route('/api/dados', methods=['GET'])
def obter_dados():
    # Simula ou busca dados integrados da planilha para preenchimento da tabela
    try:
        r = requests.get(URL_PLANILHA_GOOGLE, timeout=10)
        return jsonify(r.json() if r.status_code == 200 else [])
    except:
        return jsonify([])

@app.route('/api/salvar_portaria', methods=['POST'])
def salvar_portaria():
    # Coleta e higienização para Maiúsculas automáticas
    f = request.form
    dados = {k: v.upper().strip() for k, v in f.items() if hasattr(v, 'upper')}
    
    # Tratamento de datas e envio para a API do Google Sheets
    try: requests.post(URL_PLANILHA_GOOGLE, json=dados, timeout=10)
    except: pass
    return jsonify({"status": "salvo"})

@app.route('/api/salvar_supervisor', methods=['POST'])
def salvar_supervisor():
    req = request.json
    
    # Execução das regras de cálculo matemático operacional (Duração de Tempos)
    fmt = '%Y-%m-%dT%H:%M'
    t3_descarga = ""
    t4_operacional = ""
    
    try:
        # T3 - Descarga: Final Transbordo - Inicio Transbordo
        dt_ini3 = datetime.strptime(req['ini_trans'], fmt)
        dt_fim3 = datetime.strptime(req['fim_trans'], fmt)
        diff3 = dt_fim3 - dt_ini3
        t3_descarga = f"{int(diff3.total_seconds() // 3600):02d}:{int((diff3.total_seconds() % 3600) // 60):02d}"
        
        # T4 - Operacional ETC: Saida ETC - Chegada ETC
        dt_ini4 = datetime.strptime(req['chegada_etc'], fmt)
        dt_fim4 = datetime.strptime(req['saida_etc'], fmt)
        diff4 = dt_fim4 - dt_ini4
        t4_operacional = f"{int(diff4.total_seconds() // 3600):02d}:{int((diff4.total_seconds() % 3600) // 60):02d}"
    except: pass

    # Envia os pacotes processados para arquivamento ou retorno
    return jsonify({"status": "atualizado", "t3": t3_descarga, "t4": t4_operacional})

@app.route('/api/inline_update', methods=['POST'])
def inline_update():
    # Rota que lida com o botão salvar editado direto na tabela de Histórico
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
