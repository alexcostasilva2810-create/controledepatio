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

# BANCO DE DADOS TEMPORÁRIO EM MEMÓRIA PARA AS VAGAS PROGRAMADAS (Substituído ao plugar na planilha)
VAGAS_PROGRAMADAS_DB = []

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
        
        /* 1. CAPA INICIAL LOGÍSTICA */
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

        /* 2. TELA DE LOGIN */
        #containerLogin { display: none; width: 100%; height: 100vh; justify-content: center; align-items: center; background: #e2e8f0; }
        #telaLogin { width: 100%; max-width: 400px; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }
        #telaLogin h2 { color: var(--primary); margin-bottom: 25px; font-weight: 700; margin-top: 0; }
        .msg-sucesso { color: #2e7d32; font-weight: bold; margin: 15px 0; display: none; }
        
        /* 3. SISTEMA PRINCIPAL */
        #sistemaPrincipal { display: none; }
        .navbar-zion { background: var(--primary); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
        .navbar-zion .logo { font-size: 22px; font-weight: 800; letter-spacing: 1.5px; }
        .navbar-zion .subtitulo { font-size: 15px; font-weight: 400; opacity: 0.85; }
        .nav-right { display: flex; align-items: center; gap: 15px; }
        .user-info { font-size: 13px; background: rgba(255,255,255,0.1); padding: 6px 15px; border-radius: 20px; font-weight: 600; }
        
        .container-sistema { max-width: 1400px; margin: 25px auto; padding: 0 20px; }
        
        /* Abas de Navegação */
        .tabs { display: flex; margin-bottom: 25px; gap: 4px; }
        .tab-button { flex: 1; background: #cbd5e1; border: none; padding: 15px; font-size: 13px; font-weight: bold; color: #4a5568; cursor: pointer; border-radius: 6px 6px 0 0; transition: 0.2s; text-transform: uppercase; }
        .tab-button.active { background: white; color: var(--primary); border-bottom: 4px solid var(--accent); }
        
        .card-modulo { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: none; }
        .card-modulo.active { display: block; }

        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
        .form-group { display: flex; flex-direction: column; }
        .full-width { grid-column: span 2; }
        @media(max-width: 768px) { .full-width { grid-column: span 1; } }
        
        label { font-size: 11px; font-weight: 700; color: #4a5568; margin-bottom: 6px; text-transform: uppercase; }
        input[type="text"], input[type="password"] { text-transform: uppercase; }
        input, select { padding: 11px; border: 1.5px solid #cbd5e1; border-radius: 6px; font-size: 14px; background: #fafafa; }
        input:focus, select:focus { border-color: var(--accent); background: white; outline: none; }
        
        .btn-zion { padding: 14px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; transition: 0.2s; font-size: 13px; }
        .btn-submit { background-color: var(--success); color: white; width: 100%; margin-top: 15px; }
        .btn-primary-zion { background-color: var(--primary); color: white; }
        .btn-danger-zion { background-color: var(--danger); color: white; padding: 8px 18px; border-radius: 20px; font-size: 12px; border: none; }
        .btn-edit { background-color: #ed8936; color: white; padding: 6px 12px; font-size: 11px; border-radius: 4px; border:none; }
        .btn-save { background-color: #38a169; color: white; padding: 6px 12px; font-size: 11px; border-radius: 4px; display: none; border:none; }
        
        /* Elementos específicos da tela de Vagas do Vídeo */
        .card-counter-zion { border-left: 4px solid var(--primary); padding: 15px; background: white; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
        .counter-val { font-size: 24px; font-weight: bold; color: #0f172a; }
        
        .table-container { overflow-x: auto; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; min-width: 1300px; }
        th { background-color: var(--primary); color: white; padding: 12px 8px; font-weight: 600; text-transform: uppercase; }
        td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; }
        tr:nth-child(even) { background-color: #f8fafc; }
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
                    <div class="form-group full-width"><label>Upload XML / Documento da NF</label><input type="file" name="arquivo_nf" accept=".xml,.pdf"></div>
                    
                    <div class="full-width">
                        <button type="submit" class="btn-zion btn-submit">Salvar Registro Portaria</button>
                    </div>
                </form>
            </div>

            <div id="programacao_vagas" class="card-modulo">
                <h3 style="color: var(--primary); margin-top: 0; border-bottom: 2px solid var(--gray); padding-bottom: 10px;">Programação de Grades e Ofertas</h3>
                
                <div class="row">
                    <div class="col-md-8">
                        <form id="formVagas" onsubmit="salvarVagasProgramadas(event)" class="row g-3">
                            <div class="col-md-6">
                                <label>Localidade</label>
                                <select class="form-select" id="vaga_localidade" required>
                                    <option value="Grupo GDias - Transourada">Grupo GDias - Transourada</option>
                                    <option value="ETC Miritituba">ETC Miritituba</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label>Vigência do Pátio</label>
                                <select class="form-select" id="vaga_vigencia" required>
                                    <option value="02/06/2026 - 02/07/2026">02/06/2026 até 02/07/2026</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label>Janela Horária</label>
                                <select class="form-select" id="vaga_janela" required>
                                    <option value="00:00 - 22:00">00:00 às 22:00</option>
                                    <option value="06:00 - 18:00">06:00 às 18:00</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label>Nº de Vagas Ofertadas</label>
                                <input type="number" class="form-control" id="vaga_quantidade" placeholder="Ex: 10" required>
                            </div>
                            <div class="col-md-4">
                                <label>Volume Programado (kg)</label>
                                <input type="number" class="form-control" id="vaga_volume" placeholder="Ex: 45000" required>
                            </div>
                            <div class="col-md-6">
                                <label>Cliente Destinatário</label>
                                <input type="text" class="form-control" id="vaga_cliente" placeholder="Nome do cliente" required>
                            </div>
                            <div class="col-md-6">
                                <label>Produto</label>
                                <input type="text" class="form-control" id="vaga_produto" placeholder="Ex: ANIDRO / S10" required>
                            </div>
                            <div class="col-12 text-end">
                                <button type="submit" class="btn-zion btn-submit" style="background-color: var(--accent); width: auto;">Disponibilizar Vagas</button>
                            </div>
                        </form>
                    </div>

                    <div class="col-md-4">
                        <div class="card-counter-zion">
                            <div class="text-muted small fw-bold text-uppercase">Total de Vagas Ofertadas</div>
                            <div class="counter-val" id="count_vagas">0</div>
                            <div class="text-xs text-secondary">Vagas no período ativo</div>
                        </div>
