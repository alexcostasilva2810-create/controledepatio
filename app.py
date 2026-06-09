import os
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==============================================================================
# BLOCO 1: CONFIGURAÇÕES GERAIS E PARAMETRIZAÇÃO DE USUÁRIOS
# ==============================================================================
URL_PLANILHA_GOOGLE = "https://script.google.com/macros/s/AKfycbxlzebvfA0GQcAyQ1Oc9IFC6XX9t4mR7cOLzj4jt8sX0B2YZoozCuTzlAnZHeL8aHjr/exec"

USUARIOS_PERMITIDOS = {
    "admin": {"senha": "123", "nome": "ADMINISTRADOR ZION"},
    "fs_portaria": {"senha": "789", "nome": "PORTARIA - OPERADOR FS"},
    "gd_supervisor": {"senha": "456", "nome": "SUPERVISOR ETC - GD"}
}

# BANCOS DE DADOS TEMPORÁRIOS EM MEMÓRIA
VAGAS_PROGRAMADAS_DB = []
PREVISOES_BALSA_DB = [
    # Dados fictícios iniciais para o FS testar o agendamento imediatamente
    {"balsa": "Balsa Zion I", "capacidade": "3.500 Toneladas", "inicio": "2026-06-01", "fim": "2026-06-15"},
    {"balsa": "Balsa GDias II", "capacidade": "5.000 Toneladas", "inicio": "2026-06-10", "fim": "2026-06-25"}
]
AGENDAMENTOS_CAMIOES_DB = []

# ==============================================================================
# BLOCO 2: INTERFACE VISUAL (HTML, CSS E SISTEMA DE TELAS INTEGRADO)
# ==============================================================================
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Zion Tecnologia - Monitoramento ETC</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { 
            --primary: #0a2647; 
            --secondary: #144272; 
            --accent: #2c74b3; 
            --success: #1b4d3e; 
            --danger: #9b2c2c;
            --gray: #f4f6f9; 
        }
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background-color: var(--gray); color: #333; overflow-x: hidden; }
        
        #capaInicial { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: linear-gradient(135px, rgba(10,38,71,0.95), rgba(20,66,114,0.85)), 
                        url('https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1920&q=80') center/cover no-repeat;
            display: flex; flex-direction: column; justify-content: center; align-items: center; 
            color: white; text-align: center; cursor: pointer; z-index: 999; transition: transform 0.6s ease-in-out;
        }
        #capaInicial h1 { font-size: 48px; font-weight: 800; margin: 0 0 10px 0; letter-spacing: 3px; text-shadow: 2px 2px 8px rgba(0,0,0,0.5); }
        #capaInicial p { font-size: 18px; max-width: 600px; margin: 0 0 30px 0; opacity: 0.9; font-weight: 300; }
        .pulse-btn { background: var(--accent); color: white; border: none; padding: 15px 35px; font-size: 16px; font-weight: bold; border-radius: 30px; text-transform: uppercase; cursor: pointer; box-shadow: 0 0 0 0 rgba(44,116,179,0.7); animation: pulse 2s infinite; }
        
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(44,116,179,0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(44,116,179,0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(44,116,179,0); }
        }

        #containerLogin { display: none; width: 100%; height: 100vh; justify-content: center; align-items: center; background: #e2e8f0; }
        #telaLogin { width: 100%; max-width: 400px; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }
        
        #sistemaPrincipal { display: none; }
        .navbar-zion { background: var(--primary); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
        .navbar-zion .logo { font-size: 22px; font-weight: 800; letter-spacing: 1.5px; }
        .navbar-zion .subtitulo { font-size: 15px; font-weight: 400; opacity: 0.85; }
        .nav-right { display: flex; align-items: center; gap: 15px; }
        .user-info { font-size: 13px; background: rgba(255,255,255,0.1); padding: 6px 15px; border-radius: 20px; font-weight: 600; }
        
        .container-sistema { max-width: 1400px; margin: 25px auto; padding: 0 20px; }
        
        .tabs { display: flex; margin-bottom: 25px; gap: 4px; overflow-x: auto; }
        .tab-button { flex: 1; background: #cbd5e1; border: none; padding: 15px; font-size: 13px; font-weight: bold; color: #4a5568; cursor: pointer; border-radius: 6px 6px 0 0; transition: 0.2s; text-transform: uppercase; white-space: nowrap; }
        .tab-button.active { background: white; color: var(--primary); border-bottom: 4px solid var(--accent); }
        
        .card-modulo { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: none; }
        .card-modulo.active { display: block; }

        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
        .form-group { display: flex; flex-direction: column; }
        .full-width { grid-column: span 2; }
        
        label { font-size: 11px; font-weight: 700; color: #4a5568; margin-bottom: 6px; text-transform: uppercase; }
        input[type="text"], input[type="password"] { text-transform: uppercase; }
        input, select { padding: 11px; border: 1.5px solid #cbd5e1; border-radius: 6px; font-size: 14px; background: #fafafa; }
        
        .btn-zion { padding: 14px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; transition: 0.2s; font-size: 13px; }
        .btn-submit { background-color: var(--success); color: white; width: 100%; margin-top: 15px; }
        .btn-primary-zion { background-color: var(--primary); color: white; }
        .btn-danger-zion { background-color: var(--danger); color: white; padding: 8px 18px; border-radius: 20px; font-size: 12px; border: none; }
        
        .card-counter-zion { border-left: 4px solid var(--primary); padding: 15px; background: white; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
        .counter-val { font-size: 24px; font-weight: bold; color: #0f172a; }
        
        .table-container { overflow-x: auto; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; min-width: 1100px; }
        th { background-color: var(--primary); color: white; padding: 12px 8px; font-weight: 600; text-transform: uppercase; }
        td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; }
    </style>
</head>
<body>

    <div id="capaInicial" onclick="entrarNoLogin()">
        <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 4px; color: var(--accent); font-weight: bold; margin-bottom: 10px;">Zion Logística Operacional</div>
        <h1>MONITORAMENTO DE PÁTIO & ETC</h1>
        <p>Controle integrado de portaria, fluxos de transbordo, indicadores de estadia de frotas e gerenciamento em tempo real.</p>
        <button class="pulse-btn">Iniciar Lançamentos</button>
    </div>

    <div id="containerLogin">
        <div id="telaLogin">
            <div style="font-size: 26px; font-weight: 800; color: #0a2647; margin-bottom: 5px;">SISTEMA ZION</div>
            <p style="color: #718096; margin-top: 0; font-size: 13px;">ACESSO RESTRITO POR PERFIL DE USUÁRIO</p>
            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin-bottom: 25px;">
            
            <div class="form-group" style="text-align: left; margin-bottom: 15px;">
                <label>Usuário</label>
                <input type="text" id="loginUser" required placeholder="Ex: FS_PORTARIA">
            </div>
            <div class="form-group" style="text-align: left; margin-bottom: 20px;">
                <label>Senha</label>
                <input type="password" id="loginPass" required placeholder="Digite sua senha">
            </div>
            <button class="btn-zion btn-primary-zion" style="width: 100%;" onclick="executarLogin()">Acessar Painel</button>
            <div id="msgSucesso" class="msg-sucesso"></div>
        </div>
    </div>

    <div id="sistemaPrincipal">
        <div class="navbar-zion">
            <div>
                <span class="logo">Zion Tecnologia</span>
                <span class="subtitulo"> | Sistema de Monitoramento - ETC</span>
            </div>
            <div class="nav-right">
                <div class="user-info" id="nomeUsuarioLogado">OLÁ, USUÁRIO</div>
                <button class="btn-danger-zion" onclick="deslogarSistema()">SAIR</button>
            </div>
        </div>

        <div class="container-sistema">
            <div class="tabs" id="barraAbas">
                <button class="tab-button" id="tab_portaria" onclick="switchTab('cadastro')">📝 Portaria (Registro)</button>
                <button class="tab-button" id="tab_previsao" onclick="switchTab('previsao_programacao')">🚢 Previsão de Programação</button>
                <button class="tab-button" id="tab_agendamento_fs" onclick="switchTab('agendamento_caminhoes')">🚛 Agendamento de Caminhões</button>
                <button class="tab-button" id="tab_vagas" onclick="switchTab('programacao_vagas')">📋 Programação de Vagas</button>
                <button class="tab-button" id="tab_etc" onclick="switchTab('supervisor')">⚙️ Gestão Operacional ETC</button>
                <button class="tab-button" id="tab_historico" onclick="switchTab('painel')">📊 Histórico Geral</button>
            </div>

            <div id="cadastro" class="card-modulo">
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
                    <div class="full-width"><button type="submit" class="btn-zion btn-submit">Salvar Registro Portaria</button></div>
                </form>
            </div>

            <div id="previsao_programacao" class="card-modulo">
                <h3 style="color: var(--primary); margin-top: 0; border-bottom: 2px solid var(--gray); padding-bottom: 10px;">Previsão de Programação - Janela de Balsas</h3>
                <div class="row">
                    <div class="col-md-8" id="containerFormPrevisao">
                        <form id="formPrevisaoBalsa" onsubmit="salvarPrevisaoBalsa(event)" class="row g-3">
                            <div class="col-md-6">
                                <label>Balsa Disponível</label>
                                <select class="form-select" id="prev_balsa_nome" onchange="atualizarCapacidadeBalsa()" required>
                                    <option value="">Selecione uma embarcação...</option>
                                    <option value="Balsa Zion I">Balsa Zion I</option>
                                    <option value="Balsa GDias II">Balsa GDias II</option>
                                    <option value="Balsa Transourada III">Balsa Transourada III</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label>Capacidade Alocada (Toneladas)</label>
                                <input type="text" class="form-control" id="prev_balsa_capacidade" readonly placeholder="Selecione a balsa">
                            </div>
                            <div class="col-md-6">
                                <label>Data Inicial Disponível</label>
                                <input type="date" class="form-control" id="prev_data_inicio" required>
                            </div>
                            <div class="col-md-6">
                                <label>Data Final Disponível</label>
                                <input type="date" class="form-control" id="prev_data_fim" required>
                            </div>
                            <div class="col-12 text-end">
                                <button type="submit" class="btn-zion btn-submit" style="background-color: var(--primary); width: auto;">Fixar Previsão de Escala (GD)</button>
                            </div>
                        </form>
                    </div>
                    <div class="col-md-4">
                        <div class="card-counter-zion" style="border-left-color: var(--accent);">
                            <div class="text-muted small fw-bold text-uppercase">Balsas Ativas na Escala</div>
                            <div class="counter-val" id="count_balsas_ativas">0</div>
                        </div>
                        <div id="alertaFS" class="alert alert-info small" style="display:none;">
                            <strong>Modo de Consulta (FS):</strong> Você pode visualizar as janelas acima para programar as frotas na próxima aba.
                        </div>
                    </div>
                </div>

                <div class="mt-4">
                    <h5>Grades de Escala e Datas Disponíveis</h5>
                    <div class="table-responsive">
                        <table class="table table-striped align-middle" style="min-width: 900px;">
                            <thead>
                                <tr>
                                    <th>Embarcação</th>
                                    <th>Capacidade Cadastrada</th>
                                    <th>Início Recebimento</th>
                                    <th>Término Recebimento</th>
                                    <th>Status do Pátio</th>
                                </tr>
                            </thead>
                            <tbody id="corpoTabelaPrevisoes"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="agendamento_caminhoes" class="card-modulo">
                <h3 style="color: var(--primary); margin-top: 0; border-bottom: 2px solid var(--gray); padding-bottom: 10px;">Agendamento de Caminhões (Fluxo FS)</h3>
                <div class="row">
                    <div class="col-md-9">
                        <form id="formAgendamentoCaminhao" onsubmit="salvarAgendamentoCaminhao(event)" class="row g-3">
                            <div class="col-md-6">
                                <label>Vincular à Janela de Balsa Disponível</label>
                                <select class="form-select" id="agenda_balsa_vinculo" onchange="exibirInfoBalsaSelecionada()" required>
                                    </select>
                            </div>
                            <div class="col-md-6">
                                <label>Data Escolhida para o Agendamento</label>
                                <input type="date" class="form-control" id="agenda_data" required>
                            </div>
                            
                            <div class="col-md-4">
                                <label>Placa do Caminhão</label>
                                <input type="text" class="form-control" id="agenda_placa" placeholder="ABC1D23" required>
                            </div>
                            <div class="col-md-8">
                                <label>Nome do Motorista</label>
                                <input type="text" class="form-control" id="agenda_motorista" required>
                            </div>
                            
                            <div class="col-md-4">
                                <label>Número da NF</label>
                                <input type="text" class="form-control" id="agenda_nf" required>
                            </div>
                            <div class="col-md-4">
                                <label>Volume da NF (kg ou Litros)</label>
                                <input type="number" class="form-control" id="agenda_volume" required>
                            </div>
                            <div class="col-md-4">
                                <label>Contato do Motorista</label>
                                <input type="text" class="form-control" id="agenda_contato" placeholder="(00) 00000-0000" required>
                            </div>
                            
                            <div class="col-12 text-end">
                                <button type="submit" class="btn-zion btn-submit" style="background-color: var(--success); width: auto;">Confirmar Agendamento no Pátio</button>
                            </div>
                        </form>
                    </div>
                </div>

                <div class="mt-4">
                    <h5>Caminhões Agendados para Transbordo</h5>
                    <div class="table-responsive">
                        <table class="table table-striped align-middle" style="min-width: 1000px;">
                            <thead>
                                <tr>
                                    <th>Data Programada</th>
                                    <th>Balsa Destino</th>
                                    <th>Placa</th>
                                    <th>Motorista</th>
                                    <th>Nº NF</th>
                                    <th>Volume</th>
                                    <th>Contato</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody id="corpoTabelaAgendamentos"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="programacao_vagas" class="card-modulo">
                <h3 style="color: var(--primary); margin-top: 0; border-bottom: 2px solid var(--gray); padding-bottom: 10px;">Programação de Grades e Ofertas</h3>
                <div class="row">
                    <div class="col-md-8">
                        <form id="formVagas" onsubmit="salvarVagasProgramadas(event)" class="row g-3">
                            <div class="col-md-6"><label>Localidade</label>
                                <select class="form-select" id="vaga_localidade" required>
                                    <option value="Grupo GDias - Transourada">Grupo GDias - Transourada</option>
                                    <option value="ETC Miritituba">ETC Miritituba</option>
                                </select>
                            </div>
                            <div class="col-md-6"><label>Vigência do Pátio</label>
                                <select class="form-select" id="vaga_vigencia" required>
                                    <option value="02/06/2026 - 02/07/2026">02/06/2026 até 02/07/2026</option>
                                </select>
                            </div>
                            <div class="col-md-4"><label>Janela Horária</label>
                                <select class="form-select" id="vaga_janela" required>
                                    <option value="00:00 - 22:00">00:00 às 22:00</option>
                                    <option value="06:00 - 18:00">06:00 às 18:00</option>
                                </select>
                            </div>
                            <div class="col-md-4"><label>Nº de Vagas Ofertadas</label><input type="number" class="form-control" id="vaga_quantidade" required></div>
                            <div class="col-md-4"><label>Volume Programado (kg)</label><input type="number" class="form-control" id="vaga_volume" required></div>
                            <div class="col-md-6"><label>Cliente Destinatário</label><input type="text" class="form-control" id="vaga_cliente" required></div>
                            <div class="col-md-6"><label>Produto</label><input type="text" class="form-control" id="vaga_produto" required></div>
                            <div class="col-12 text-end"><button type="submit" class="btn-zion btn-submit" style="background-color: var(--accent); width: auto;">Disponibilizar Vagas</button></div>
                        </form>
                    </div>
                    <div class="col-md-4">
                        <div class="card-counter-zion">
                            <div class="text-muted small fw-bold text-uppercase">Total de Vagas Ofertadas</div>
                            <div class="counter-val" id="count_vagas">0</div>
                        </div>
                    </div>
                </div>
                <div class="mt-4">
                    <h5>Relatório de Alocação de Vagas Ativas</h5>
                    <div class="table-responsive">
                        <table class="table table-striped align-middle" style="min-width: 1000px;">
                            <thead><tr><th>Vigência</th><th>Cliente</th><th>Produto</th><th>Vagas Disponíveis</th><th>Volume Max (kg)</th></tr></thead>
                            <tbody id="corpoTabelaVagas"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="supervisor" class="card-modulo">
                <h3 style="color: var(--primary); margin-top: 0; border-bottom: 2px solid var(--gray); padding-bottom: 10px;">Módulo de Controle Interno ETC</h3>
                <form id="formSupervisor" onsubmit="salvarSupervisor(event)" class="form-grid">
                    <div class="form-group"><label>Vincular ao Registro (Nº SEQ)</label><input type="text" id="sup_seq" required></div>
                    <div class="form-group"><label>Chegada ETC</label><input type="datetime-local" id="sup_chegada" required></div>
                    <div class="form-group"><label>T2- Estadia</label><input type="text" id="sup_estadia" placeholder="Calculado automaticamente"></div>
                    <div class="form-group"><label>Início Transbordo</label><input type="datetime-local" id="sup_ini_trans" required></div>
                    <div class="form-group"><label>Final Transbordo</label><input type="datetime-local" id="sup_fim_trans" required></div>
                    <div class="form-group"><label>Saída ETC</label><input type="datetime-local" id="sup_saida" required></div>
                    <div class="full-width"><button type="submit" class="btn-zion btn-submit" style="background-color: var(--accent);">Atualizar Movimentação ETC</button></div>
                </form>
            </div>

            <div id="painel" class="card-modulo">
                <div class="table-container">
                    <table id="tabelaDados">
                        <thead>
                            <tr>
                                <th>SEQ</th><th>Placa</th><th>Motorista</th><th>NF</th><th>Chegada Posto</th>
                                <th>T1 Trânsito</th><th>Chegada ETC</th><th>T2 Estadia</th><th>Ações</th>
                            </tr>
                        </thead>
                        <tbody id="corpoTabela"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let dadosLocais = [];
        let perfilUsuario = "";

        function entrarNoLogin() {
            document.getElementById('capaInicial').style.transform = "translateY(-100%)";
            document.getElementById('containerLogin').style.display = "flex";
        }

        function executarLogin() {
            let u = document.getElementById('loginUser').value.toLowerCase();
            let s = document.getElementById('loginPass').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({usuario: u, senate: s})
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === "sucesso") {
                    perfilUsuario = u;
                    document.getElementById('msgSucesso').style.display = "block";
                    document.getElementById('msgSucesso').innerText = `Acesso concedido! Olá ${data.nome}.`;
                    document.getElementById('nomeUsuarioLogado').innerText = `Operador: ${data.nome}`;
                    
                    configurarAbasPorIniciais(u);

                    setTimeout(() => {
                        document.getElementById('containerLogin').style.display = "none";
                        document.getElementById('sistemaPrincipal').style.display = "block";
                        atualizarTabelaHistorico();
                        atualizarGradeVagas();
                        atualizarTabelaPrevisoes();
                        atualizarTabelaAgendamentos();
                    }, 1500);
                } else {
                    alert("Usuário ou Senha incorretos!");
                }
            });
        }

        function configurarAbasPorIniciais(usuario) {
            // Resetar visibilidade padrão
            document.getElementById('tab_portaria').style.display = "block";
            document.getElementById('tab_previsao').style.display = "block";
            document.getElementById('tab_agendamento_fs').style.display = "block";
            document.getElementById('tab_vagas').style.display = "block";
            document.getElementById('tab_etc').style.display = "block";
            
            document.getElementById('containerFormPrevisao').style.display = "block";
            document.getElementById('alertaFS').style.display = "none";

            if (usuario.startsWith('fs')) {
                // FS enxerga portaria, a previsão (modo leitura) e o NOVO agendamento de caminhões
                document.getElementById('tab_etc').style.display = "none";
                document.getElementById('tab_vagas').style.display = "none";
                document.getElementById('containerFormPrevisao').style.display = "none"; // Oculta o form de cadastrar balsa
                document.getElementById('alertaFS').style.display = "block"; // Mostra dica de leitura
                switchTab('cadastro');
            } else if (usuario.startsWith('gd')) {
                // GD gerencia as previsões de balsa e vagas
                document.getElementById('tab_portaria').style.display = "none";
                document.getElementById('tab_agendamento_fs').style.display = "none";
                switchTab('previsao_programacao');
            } else {
                switchTab('cadastro');
            }
        }

        function switchTab(tabId) {
            document.querySelectorAll('.card-modulo').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            
            let cardElement = document.getElementById(tabId);
            if(cardElement) cardElement.classList.add('active');
            
            let botoes = document.getElementsByClassName('tab-button');
            for(let btn of botoes) {
                if(btn.getAttribute('onclick').includes(tabId)) {
                    btn.classList.add('active');
                }
            }
        }

        function atualizarCapacidadeBalsa() {
            let balsa = document.getElementById('prev_balsa_nome').value;
            let capMap = {
                "Balsa Zion I": "3.500 Toneladas",
                "Balsa GDias II": "5.000 Toneladas",
                "Balsa Transourada III": "4.200 Toneladas"
            };
            document.getElementById('prev_balsa_capacidade').value = capMap[balsa] || "";
        }

        function salvarPrevisaoBalsa(e) {
            e.preventDefault();
            let payload = {
                balsa: document.getElementById('prev_balsa_nome').value,
                capacidade: document.getElementById('prev_balsa_capacidade').value,
                inicio: document.getElementById('prev_data_inicio').value,
                fim: document.getElementById('prev_data_fim').value
            };

            fetch('/api/salvar_previsao', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(() => {
                alert("Previsão de balsa fixada pelo GD!");
                document.getElementById('formPrevisaoBalsa').reset();
                atualizarTabelaPrevisoes();
            });
        }

        function atualizarTabelaPrevisoes() {
            fetch('/api/obter_previsoes')
            .then(res => res.json())
            .then(dados => {
                let html = "";
                let selectVinculo = document.getElementById('agenda_balsa_vinculo');
                
                document.getElementById('count_balsas_ativas').innerText = dados.length;
                selectVinculo.innerHTML = '<option value="">Selecione uma janela ativa...</option>';
                
                if(dados.length === 0){
                    html = "<tr><td colspan='5' class='text-center text-muted'>Nenhuma balsa prevista na escala.</td></tr>";
                } else {
                    dados.forEach(d => {
                        let dataFormatadaIni = d.inicio.split('-').reverse().join('/');
                        let dataFormatadaFim = d.fim.split('-').reverse().join('/');
                        
                        html += `<tr>
                            <td><strong>${d.balsa}</strong></td>
                            <td>${d.capacidade}</td>
                            <td>${dataFormatadaIni}</td>
                            <td>${dataFormatadaFim}</td>
                            <td><span class="badge bg-success">Disponível para FS</span></td>
                        </tr>`;
                        
                        // Alimenta o select do módulo de agendamento do FS
                        let opt = document.createElement('option');
                        opt.value = d.balsa;
                        opt.text = `${d.balsa} (${dataFormatadaIni} até ${dataFormatadaFim})`;
                        opt.dataset.ini = d.inicio;
                        opt.dataset.fim = d.fim;
                        selectVinculo.add(opt);
                    });
                }
                document.getElementById('corpoTabelaPrevisoes').innerHTML = html;
            });
        }

        function exibirInfoBalsaSelecionada() {
            let select = document.getElementById('agenda_balsa_vinculo');
            let opt = select.options[select.selectedIndex];
            if(opt && opt.value !== "") {
                document.getElementById('agenda_data').min = opt.dataset.ini;
                document.getElementById('agenda_data').max = opt.dataset.fim;
            }
        }

        // LÓGICA DO NOVO MÓDULO DE AGENDAMENTO
        function salvarAgendamentoCaminhao(e) {
            e.preventDefault();
            let payload = {
                balsa: document.getElementById('agenda_balsa_vinculo').value,
                data: document.getElementById('agenda_data').value,
                placa: document.getElementById('agenda_placa').value.toUpperCase(),
                motorista: document.getElementById('agenda_motorista').value.toUpperCase(),
                nf: document.getElementById('agenda_nf').value,
                volume: document.getElementById('agenda_volume').value,
                contato: document.getElementById('agenda_contato').value
            };

            fetch('/api/salvar_agendamento_caminhao', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(() => {
                alert("Agendamento do caminhão concluído com sucesso!");
                document.getElementById('formAgendamentoCaminhao').reset();
                atualizarTabelaAgendamentos();
            });
        }

        function atualizarTabelaAgendamentos() {
            fetch('/api/obter_agendamentos_caminhoes')
            .then(res => res.json())
            .then(dados => {
                let html = "";
                dados.forEach(d => {
                    html += `<tr>
                        <td><b>${d.data.split('-').reverse().join('/')}</b></td>
                        <td>${d.balsa}</td>
                        <td><span class="badge bg-dark">${d.placa}</span></td>
                        <td>${d.motorista}</td>
                        <td>${d.nf}</td>
                        <td>${parseFloat(d.volume).toLocaleString('pt-BR')} unidades</td>
                        <td>${d.contato}</td>
                        <td><span class="badge bg-warning text-dark">Agendado</span></td>
                    </tr>`;
                });
                document.getElementById('corpoTabelaAgendamentos').innerHTML = html || "<tr><td colspan='8' class='text-center text-muted'>Nenhum caminhão agendado para esta grade.</td></tr>";
            });
        }

        function salvarPortaria(e) { e.preventDefault(); let formData = new FormData(document.getElementById('formCadastro')); fetch('/api/salvar_portaria', { method: 'POST', body: formData }).then(() => { alert("Portaria salva!"); document.getElementById('formCadastro').reset(); atualizarTabelaHistorico(); }); }
        function atualizarTabelaHistorico() { fetch('/api/dados').then(res => res.json()).then(dados => { let html = ""; dados.forEach(row => { html += `<tr><td><b>#${row.sequencial}</b></td><td>${row.placa}</td><td>${row.motorista}</td><td>${row.num_nota}</td><td>${row.chegada_posto || '-'}</td><td>${row.t1_transito || '-'}</td><td>${row.chegada_etc || '-'}</td><td>${row.t2_estadia || '-'}</td><td>-</td></tr>`; }); document.getElementById('corpoTabela').innerHTML = html; }); }
        function deslogarSistema() { perfilUsuario = ""; document.getElementById('sistemaPrincipal').style.display = "none"; document.getElementById('containerLogin').style.display = "none"; document.getElementById('capaInicial').style.transform = "translateY(0)"; }
        function salvarVagasProgramadas(e) { e.preventDefault(); }
        function atualizarGradeVagas() { }
    </script>
</body>
</html>
"""

# ==============================================================================
# BLOCO 3: ROTAS DA API (MÓDULO FLASK)
# ==============================================================================
@app.route('/')
def index():
    return render_template_string(HTML_SISTEMA)

@app.route('/api/login', methods=['POST'])
def api_login():
    req = request.json
    u = req.get('usuario', '').lower().strip()
    s = req.get('senha', '')
    if u in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[u]['senha'] == s:
        return jsonify({"status": "sucesso", "nome": USUARIOS_PERMITIDOS[u]['nome']})
    return jsonify({"status": "erro"})

@app.route('/api/dados', methods=['GET'])
def obter_dados():
    try:
        r = requests.get(URL_PLANILHA_GOOGLE, timeout=10)
        return jsonify(r.json() if r.status_code == 200 else [])
    except: return jsonify([])

@app.route('/api/salvar_portaria', methods=['POST'])
def salvar_portaria():
    try: requests.post(URL_PLANILHA_GOOGLE, json=request.form, timeout=10)
    except: pass
    return jsonify({"status": "salvo"})

@app.route('/api/salvar_previsao', methods=['POST'])
def salvar_previsao():
    PREVISOES_BALSA_DB.append(request.json)
    return jsonify({"status": "sucesso"})

@app.route('/api/obter_previsoes', methods=['GET'])
def obter_previsoes():
    return jsonify(PREVISOES_BALSA_DB)

# NOVAS ROTAS PARA OS AGENDAMENTOS EFETUADOS PELO FS
@app.route('/api/salvar_agendamento_caminhao', methods=['POST'])
def salvar_agendamento_caminhao():
    AGENDAMENTOS_CAMIOES_DB.append(request.json)
    return jsonify({"status": "sucesso"})

@app.route('/api/obter_agendamentos_caminhoes', methods=['GET'])
def obter_agendamentos_caminhoes():
    return jsonify(AGENDAMENTOS_CAMIOES_DB)

@app.route('/api/obter_vagas', methods=['GET'])
def obter_vagas(): return jsonify(VAGAS_PROGRAMADAS_DB)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
