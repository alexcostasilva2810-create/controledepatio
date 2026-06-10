import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
application = app

# ==============================================================================
# BANCO DE DADOS EM MEMÓRIA
# ==============================================================================
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
    "SD XVIII": {"capacidade": "795.6 m³", "%" : "13", "cts_meta": 13},
    "SD XX": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXI": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXIII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "TWB 200": {"capacidade": "2142.0 m³", "cts_meta": 35}
}

DISPONIBILIDADES_DB = []
AGENDAMENTOS_DB = []

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Zion - Sistema de Agendamento Portuário</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root { --primary: #0f172a; --accent: #deff9a; }
        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, sans-serif; padding: 25px; }
        .navbar-top { background-color: var(--primary); color: white; padding: 15px 25px; border-radius: 8px; margin-bottom: 25px; border-bottom: 4px solid var(--accent); }
        .card-custom { border: none; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); background: white; overflow: hidden; }
        .card-header-custom { background-color: #1e293b; color: white; font-weight: bold; padding: 18px; border: none; }
        .box-janela { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; transition: all 0.3s; position: relative; }
        .box-janela:hover { border-color: #2c74b3; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        .input-cota { font-weight: 800; text-align: center; font-size: 18px; color: #1e293b; border: 2px solid #cbd5e1; }
        .status-badge { font-size: 15px; font-weight: 700; padding: 15px; border-radius: 8px; display: block; text-align: center; margin-bottom: 20px; }
        .label-custom { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 5px; display: block; }
        .badge-meta { background: var(--primary); color: var(--accent); padding: 5px 12px; border-radius: 20px; font-size: 12px; }
        .nav-pills .nav-link.active { background-color: #1e293b; color: #deff9a; font-weight: bold; }
        .btn-janela-fs { background: #f8fafc; border: 2px dashed #cbd5e1; width: 100%; text-align: left; padding: 15px; border-radius: 10px; transition: all 0.2s; }
        .btn-janela-fs:hover:not([disabled]) { border-color: #10b981; background: #f0fdf4; transform: scale(1.02); }
    </style>
</head>
<body>

    <div class="navbar-top d-flex justify-content-between align-items-center shadow-lg">
        <div>
            <h4 class="m-0 fw-bold"><i class="fa-solid fa-anchor me-2"></i>SISTEMA DE AGENDAMENTO LOGÍSTICO</h4>
            <small style="color: var(--accent);">Zion Tecnologia - Controle Integrado de Pátio e Ofertas</small>
        </div>
        <ul class="nav nav-pills" id="moduloTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active me-2 text-white" id="tab-gd" data-bs-toggle="tab" data-bs-target="#modulo-gd" type="button"><i class="fa-solid fa-sliders me-1"></i> MÓDULO 1: GESTÃO (GD)</button>
            </li>
            <li class="nav-item">
                <button class="nav-link text-white bg-dark" id="tab-fs" data-bs-toggle="tab" data-bs-target="#modulo-fs" type="button" onclick="carregarDisponibilidadesFS()"><i class="fa-solid fa-truck-ramp-box me-1"></i> MÓDULO 2: CLIENTE (FS)</button>
            </li>
        </ul>
    </div>

    <div class="tab-content" id="moduloTabsContent">
        
        <div class="tab-pane fade show active" id="modulo-gd" role="tabpanel">
            <div class="row g-4">
                <div class="col-lg-4">
                    <div class="card card-custom shadow">
                        <div class="card-header card-header-custom"><i class="fa-solid fa-sliders me-2"></i>Configuração da Oferta</div>
                        <div class="card-body p-4">
                            <form id="formOferta" onsubmit="salvarOperacao(event)">
                                <input type="hidden" id="edit_index" value="-1">
                                
                                <div class="mb-4">
                                    <label class="label-custom">Balsa / Embarcação Disponível</label>
                                    <select class="form-select form-select-lg fw-bold" id="balsa_id" onchange="carregarMetricasBalsa()" required>
                                        <option value="">Selecione...</option>
                                        {% for balsa in lista_balsas %}
                                        <option value="{{ balsa }}">{{ balsa }}</option>
                                        {% endfor %}
                                    </select>
                                </div>

                                <div class="row mb-4">
                                    <div class="col-6">
                                        <label class="label-custom">Capacidade (m³)</label>
                                        <input type="text" class="form-control bg-light fw-bold" id="cap_view" readonly>
                                    </div>
                                    <div class="col-6">
                                        <label class="label-custom">Exigência (CTS)</label>
                                        <input type="text" class="form-control bg-light fw-bold text-primary" id="cts_view" readonly>
                                    </div>
                                </div>

                                <div class="row mb-4">
                                    <div class="col-6">
                                        <label class="label-custom">Data da Operação</label>
                                        <input type="date" class="form-control fw-bold" id="data_op" required>
                                    </div>
                                    <div class="col-6">
                                        <label class="label-custom">Hora Início</label>
                                        <input type="time" class="form-control fw-bold" id="hora_inicio" value="06:00" onchange="gerarGradeJanelas()" required>
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <label class="label-custom text-danger">Quantidade de Janelas a Disponibilizar</label>
                                    <select class="form-select fw-bold border-danger" id="num_janelas" onchange="gerarGradeJanelas()" required>
                                    </select>
                                </div>

                                <div class="d-grid pt-2">
                                    <button type="submit" class="btn btn-success btn-lg fw-bold" id="btn_submit">
                                        <i class="fa-solid fa-floppy-disk me-2"></i>GRAVAR DISPONIBILIDADE
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                <div class="col-lg-8">
                    <div class="card card-custom shadow">
                        <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                            <span><i class="fa-solid fa-clock me-2"></i>Distribuição de Vagas por Janela</span>
                            <span id="meta_badge" class="badge-meta">Aguardando balsa...</span>
                        </div>
                        <div class="card-body p-4">
                            <div id="status_alocacao" class="status-badge alert-secondary">
                                Selecione os parâmetros ao lado para gerar a grade.
                            </div>
                            <div class="row g-3" id="grade_container"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card card-custom mt-4 shadow">
                <div class="card-header card-header-custom text-white bg-secondary"><i class="fa-solid fa-list-check me-2"></i>Painel de Ofertas Vigentes no Sistema (Visão GD)</div>
                <div class="p-3">
                    <div id="lista_ofertas_consolidada">
                        <div class="text-center text-muted py-3">Nenhuma regra cadastrada até o momento.</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="tab-pane fade" id="modulo-fs" role="tabpanel">
            <div class="row">
                <div class="col-12">
                    <div class="card card-custom shadow mb-4">
                        <div class="card-header bg-primary text-white"><i class="fa-solid fa-ship me-2"></i>1. Selecione a Embarcação Vinculada para Agendamento</div>
                        <div class="card-body p-4">
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="label-custom">Ofertas Master Ativas</label>
                                    <select class="form-select form-select-lg fw-bold border-primary" id="select_oferta_fs" onchange="renderizarPainelJanelasFS()">
                                        <option value="">Selecione uma balsa operacional ativa...</option>
                                    </select>
                                </div>
                                <div class="col-md-6 d-flex align-items-end">
                                    <div id="resumo_balsa_fs" class="w-100 p-2 border rounded bg-light fw-bold text-secondary text-center" style="display:none;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-lg-7">
                    <div class="card card-custom shadow">
                        <div class="card-header bg-dark text-white"><i class="fa-solid fa-clock-retro me-2"></i>2. Janelas de Atendimento Disponíveis</div>
                        <div class="card-body p-4">
                            <div class="row g-3" id="grade_janelas_fs_container">
                                <div class="text-center text-muted">Selecione uma oferta master acima para carregar os horários.</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-5">
                    <div class="card card-custom shadow" id="card_formulario_agendamento" style="display: none; border-top: 5px solid #10b981;">
                        <div class="card-header bg-light text-dark fw-bold d-flex justify-content-between align-items-center">
                            <span><i class="fa-solid fa-file-pen text-success me-2"></i>Formulário de Agendamento</span>
                            <span class="badge bg-success" id="badge_janela_selecionada"></span>
                        </div>
                        <div class="card-body p-4">
                            <form id="formEfetuarAgendamento" onsubmit="confirmarAgendamentoFS(event)">
                                <input type="hidden" id="fs_oferta_idx">
                                <input type="hidden" id="fs_janela_idx">
                                
                                <div class="row mb-3">
                                    <div class="col-6">
                                        <label class="label-custom">Placa do Cavalo</label>
                                        <input type="text" class="form-control fw-bold text-uppercase" id="fs_cavalo" placeholder="ABC1234" required>
                                    </div>
                                    <div class="col-6">
                                        <label class="label-custom">Placa da Carreta</label>
                                        <input type="text" class="form-control fw-bold text-uppercase" id="fs_placa" placeholder="XYZ5678" required>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label class="label-custom">Número da Nota Fiscal (NF)</label>
                                    <input type="number" class="form-control fw-bold" id="fs_nf" placeholder="00012345" required>
                                </div>

                                <div class="mb-3">
                                    <label class="label-custom">Volume da Carga (m³)</label>
                                    <input type="number" step="0.01" class="form-control fw-bold" id="fs_volume" placeholder="Ex: 45.50" required>
                                </div>

                                <div class="mb-3">
                                    <label class="label-custom">Nome Completo do Motorista</label>
                                    <input type="text" class="form-control fw-bold" id="fs_motorista" placeholder="Nome do Condutor" required>
                                </div>

                                <div class="mb-4">
                                    <label class="label-custom">Documento CNH</label>
                                    <input type="number" class="form-control fw-bold" id="fs_cnh" placeholder="Número do Registro CNH" required>
                                </div>

                                <div class="d-grid">
                                    <button type="submit" class="btn btn-success btn-lg fw-bold shadow">
                                        <i class="fa-solid fa-circle-check me-2"></i>CONFIRMAR AGENDAMENTO (FS)
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>

<script>
    const dataBalsas = {{ dicionario_balsas | tojson }};
    let metaNecessaria = 0;
    let dadosTemporariosEdicao = null;
    let bancoLocalOfertas = [];

    function initJanelasSelect() {
        const sel = document.getElementById('num_janelas');
        if(sel) {
            sel.innerHTML = "";
            for (let i = 6; i <= 24; i++) {
                let opt = document.createElement('option');
                opt.value = i;
                opt.innerHTML = `${i} Janelas Operacionais`;
                if(i === 12) opt.selected = true;
                sel.appendChild(opt);
            }
        }
    }

    function carregarMetricasBalsa() {
        const balsa = document.getElementById('balsa_id').value;
        if(balsa && dataBalsas[balsa]) {
            metaNecessaria = dataBalsas[balsa].cts_meta;
            document.getElementById('cap_view').value = dataBalsas[balsa].capacidade;
            document.getElementById('cts_view').value = metaNecessaria + " CTS";
            document.getElementById('meta_badge').innerHTML = `META TOTAL: ${metaNecessaria} CTS`;
            gerarGradeJanelas();
        }
    }

    function gerarGradeJanelas() {
        const container = document.getElementById('grade_container');
        const totalJanelas = parseInt(document.getElementById('num_janelas').value);
        const horaBase = document.getElementById('hora_inicio').value;
        
        if(!metaNecessaria || !container) return;

        container.innerHTML = "";
        let [h, m] = horaBase.split(':').map(Number);

        let baseVagas = Math.floor(metaNecessaria / totalJanelas);
        let sobra = metaNecessaria % totalJanelas;

        for (let i = 0; i < totalJanelas; i++) {
            let hIni = String(h).padStart(2, '0');
            let mIni = String(m).padStart(2, '0');
            h = (h + 1) % 24;
            let hFim = String(h).padStart(2, '0');
            let mFim = String(m).padStart(2, '0');

            let valorSugerido = baseVagas + (i === 0 ? sobra : 0);
            
            if (dadosTemporariosEdicao && dadosTemporariosEdicao[i] !== undefined) {
                valorSugerido = dadosTemporariosEdicao[i].vagas;
            }

            container.innerHTML += `
                <div class="col-md-3 col-sm-6">
                    <div class="box-janela">
                        <label class="label-custom">JANELA #${i+1}</label>
                        <div class="fw-bold mb-2 small" style="color:#2c74b3;" id="time_j_${i}">${hIni}:${mIni} às ${hFim}:${mFim}</div>
                        <input type="number" class="form-control input-cota" 
                               id="vaga_j_${i}" value="${valorSugerido}" min="0" 
                               oninput="validarSaldo()">
                    </div>
                </div>`;
        }
        dadosTemporariosEdicao = null;
        validarSaldo();
    }

    function validarSaldo() {
        let alocado = 0;
        document.querySelectorAll('.input-cota').forEach(input => {
            alocado += parseInt(input.value) || 0;
        });

        const box = document.getElementById('status_alocacao');
        if(!box) return;
        
        if (alocado === metaNecessaria) {
            box.className = "status-badge bg-success text-white";
            box.innerHTML = `<i class="fa-solid fa-check-circle me-2"></i>GRADE PERFEITA: ${alocado} de ${metaNecessaria} CTS distribuídos.`;
        } else if (alocado > metaNecessaria) {
            box.className = "status-badge bg-danger text-white";
            box.innerHTML = `<i class="fa-solid fa-triangle-exclamation me-2"></i>EXCESSO: Você alocou ${alocado} CTS, mas a balsa só suporta ${metaNecessaria}.`;
        } else {
            box.className = "status-badge bg-warning text-dark";
            box.innerHTML = `<i class="fa-solid fa-circle-info me-2"></i>PENDENTE: Falta distribuir ${metaNecessaria - alocado} CTS para fechar a meta.`;
        }
    }

    function formatarDataBR(dataISO) {
        if(!dataISO) return "";
        const [ano, mes, dia] = dataISO.split('-');
        return `${dia}/${mes}/${ano}`;
    }

    function salvarOperacao(event) {
        event.preventDefault();
        let total = 0;
        let estruturaJanelas = [];
        
        document.querySelectorAll('.input-cota').forEach((i, idx) => {
            let val = parseInt(i.value) || 0;
            total += val;
            let horarioText = document.getElementById(`time_j_${idx}`).innerText;
            estruturaJanelas.push({
                janela_num: idx + 1,
                horario: horarioText,
                vagas: val,
                ocupadas: 0,
                disponiveis: val
            });
        });

        if(total !== metaNecessaria) {
            alert("Atenção: A soma das vagas por janela deve ser exatamente igual à meta da balsa!");
            return;
        }

        const index = parseInt(document.getElementById('edit_index').value);
        const dadosForm = {
            balsa: document.getElementById('balsa_id').value,
            data: document.getElementById('data_op').value,
            hora_inicio: document.getElementById('hora_inicio').value,
            num_janelas: document.getElementById('num_janelas').value,
            total_vagas: total,
            janelas_detalhe: estruturaJanelas
        };

        fetch('/api/salvar_disponibilidade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ index: index, dados: dadosForm })
        })
        .then(res => res.json())
        .then(data => {
            alert("Gravação executada com sucesso!");
            bancoLocalOfertas = data;
            atualizarTabelaConsolidada(data);
            resetarFormularioCompleto();
        });
    }

    function resetarFormularioCompleto() {
        document.getElementById('formOferta').reset();
        document.getElementById('edit_index').value = "-1";
        document.getElementById('btn_submit').innerHTML = `<i class="fa-solid fa-floppy-disk me-2"></i>GRAVAR DISPONIBILIDADE`;
        metaNecessaria = 0;
        document.getElementById('meta_badge').innerHTML = "Aguardando balsa...";
        document.getElementById('grade_container').innerHTML = "";
        document.getElementById('status_alocacao').className = "status-badge alert-secondary";
        document.getElementById('status_alocacao').innerHTML = "Selecione os parâmetros ao lado para gerar a grade.";
        initJanelasSelect();
    }

    function editarRegistro(index) {
        fetch(`/api/obter_registro/${index}`)
        .then(res => res.json())
        .then(item => {
            document.getElementById('edit_index').value = index;
            document.getElementById('balsa_id').value = item.balsa;
            metaNecessaria = dataBalsas[item.balsa].cts_meta;
            
            document.getElementById('cap_view').value = dataBalsas[item.balsa].capacidade;
            document.getElementById('cts_view').value = metaNecessaria + " CTS";
            document.getElementById('meta_badge').innerHTML = `EDITANDO - META: ${metaNecessaria} CTS`;
            
            document.getElementById('data_op').value = item.data;
            document.getElementById('hora_inicio').value = item.hora_inicio;
            document.getElementById('num_janelas').value = item.num_janelas;
            
            dadosTemporariosEdicao = item.janelas_detalhe;
            document.getElementById('btn_submit').innerHTML = `<i class="fa-solid fa-floppy-disk me-2"></i>SALVAR ALTERAÇÕES`;
            
            gerarGradeJanelas();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    function atualizarTabelaConsolidada(lista) {
        const container = document.getElementById('lista_ofertas_consolidada');
        if(!container) return;
        if(!lista || lista.length === 0) {
            container.innerHTML = `<div class="text-center text-muted py-3">Nenhuma regra cadastrada até o momento.</div>`;
            return;
        }
        container.innerHTML = "";
        
        lista.forEach((item, idx) => {
            let linhasJanelasHtml = "";
            item.janelas_detalhe.forEach(j => {
                linhasJanelasHtml += `
                    <tr>
                        <td><span class="badge bg-secondary">Janela #${j.janela_num}</span></td>
                        <td><b class="text-primary">${j.horario}</b></td>
                        <td class="text-center fw-bold text-dark">${j.vagas}</td>
                        <td class="text-center fw-bold text-danger bg-light">${j.ocupadas}</td>
                        <td class="text-center fw-bold text-success">${j.disponiveis}</td>
                    </tr>`;
            });

            container.innerHTML += `
                <div class="card mb-3 border-secondary">
                    <div class="card-header bg-light d-flex justify-content-between align-items-center py-2">
                        <div>
                            <span class="fs-5 fw-bold text-dark me-3">⚓ ${item.balsa}</span>
                            <span class="badge bg-dark me-2"><i class="fa-solid fa-calendar-days me-1"></i> ${formatarDataBR(item.data)}</span>
                            <span class="badge bg-info text-dark"><i class="fa-solid fa-network-wired me-1"></i> ${item.num_janelas} Janelas Ativas</span>
                        </div>
                        <button class="btn btn-warning btn-sm fw-bold px-3" onclick="editarRegistro(${idx})">
                            <i class="fa-solid fa-pencil me-1"></i> Editar Master
                        </button>
                    </div>
                    <div class="p-2 bg-white">
                        <table class="table table-sm table-bordered m-0 align-middle">
                            <thead class="table-light text-secondary small text-uppercase">
                                <tr>
                                    <th>Identificador</th>
                                    <th>Horário de Atendimento</th>
                                    <th class="text-center" style="width:140px;">Vagas Ofertadas</th>
                                    <th class="text-center" style="width:140px;">Cotas Ocupadas</th>
                                    <th class="text-center" style="width:150px;">Vagas Disponíveis</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${linhasJanelasHtml}
                            </tbody>
                        </table>
                    </div>
                </div>`;
        });
    }

    // =========================================================================
    // LÓGICA EXCLUSIVA MÓDULO 2 (FS)
    // =========================================================================
    function carregarDisponibilidadesFS() {
        fetch('/api/listar_disponibilidades')
        .then(res => res.json())
        .then(data => {
            bancoLocalOfertas = data;
            const select = document.getElementById('select_oferta_fs');
            select.innerHTML = '<option value="">Selecione uma balsa operacional ativa...</option>';
            
            data.forEach((item, index) => {
                let opt = document.createElement('option');
                opt.value = index;
                opt.innerHTML = `⚓ ${item.balsa} — Data: ${formatarDataBR(item.data)} (${item.num_janelas} Janelas)`;
                select.appendChild(opt);
            });
            
            document.getElementById('grade_janelas_fs_container').innerHTML = '<div class="text-center text-muted">Selecione uma oferta master acima para carregar os horários.</div>';
            document.getElementById('card_formulario_agendamento').style.display = 'none';
            document.getElementById('resumo_balsa_fs').style.display = 'none';
        });
    }

    function renderizarPainelJanelasFS() {
        const idx = document.getElementById('select_oferta_fs').value;
        const container = document.getElementById('grade_janelas_fs_container');
        const resumo = document.getElementById('resumo_balsa_fs');
        
        if(idx === "") {
            container.innerHTML = '<div class="text-center text-muted">Selecione uma oferta master acima para carregar os horários.</div>';
            document.getElementById('card_formulario_agendamento').style.display = 'none';
            resumo.style.display = 'none';
            return;
        }

        const oferta = bancoLocalOfertas[idx];
        resumo.innerHTML = `Capacidade: ${dataBalsas[oferta.balsa].capacidade} | Exigência: ${oferta.total_vagas} CTS`;
        resumo.style.display = 'block';

        container.innerHTML = "";
        oferta.janelas_detalhe.forEach((j, jIdx) => {
            let isDisabled = j.disponiveis <= 0;
            container.innerHTML += `
                <div class="col-md-4">
                    <button class="btn-janela-fs position-relative shadow-sm" type="button" 
                            ${isDisabled ? 'disabled style="opacity:0.6; background:#e2e8f0;"' : ''} 
                            onclick="abrirFormularioAgendamento(${idx}, ${jIdx})">
                        <span class="position-absolute top-0 end-0 translate-middle badge rounded-pill ${isDisabled ? 'bg-danger' : 'bg-success'}" style="margin-top:12px; margin-right:15px;">
                            ${j.disponiveis} vagas restando
                        </span>
                        <div class="fw-bold text-dark mb-1">Janela #${j.janela_num}</div>
                        <div class="small fw-bold text-primary mb-2"><i class="fa-regular fa-clock me-1"></i> ${j.horario}</div>
                        <div class="text-muted" style="font-size:11px;">Ocupadas: <b class="text-danger">${j.ocupadas}</b></div>
                    </button>
                </div>`;
        });
    }

    function abrirFormularioAgendamento(ofertaIdx, janelaIdx) {
        const oferta = bancoLocalOfertas[ofertaIdx];
        const janela = oferta.janelas_detalhe[janelaIdx];

        document.getElementById('fs_oferta_idx').value = ofertaIdx;
        document.getElementById('fs_janela_idx').value = janelaIdx;
        document.getElementById('badge_janela_selecionada').innerText = `Janela #${janela.janela_num} (${janela.horario})`;
        
        document.getElementById('formEfetuarAgendamento').reset();
        document.getElementById('card_formulario_agendamento').style.display = 'block';
        
        document.getElementById('card_formulario_agendamento').scrollIntoView({ behavior: 'smooth' });
    }

    function confirmarAgendamentoFS(event) {
        event.preventDefault();
        
        const oIdx = document.getElementById('fs_oferta_idx').value;
        const jIdx = document.getElementById('fs_janela_idx').value;

        const dadosAgendamento = {
            oferta_index: oIdx,
            janela_index: jIdx,
            cavalo: document.getElementById('fs_cavalo').value.toUpperCase(),
            placa: document.getElementById('fs_placa').value.toUpperCase(),
            nf: document.getElementById('fs_nf').value,
            volume: document.getElementById('fs_volume').value,
            motorista: document.getElementById('fs_motorista').value,
            cnh: document.getElementById('fs_cnh').value
        };

        fetch('/api/efetuar_agendamento', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dadosAgendamento)
        })
        .then(res => {
            if(!res.ok) throw new Error("Sem vagas disponíveis!");
            return res.json();
        })
        .then(data => {
            alert("Agendamento efetuado e salvo no pátio com sucesso!");
            bancoLocalOfertas = data;
            
            // Atualiza os dois lados simultaneamente
            renderizarPainelJanelasFS();
            atualizarTabelaConsolidada(data);
            
            document.getElementById('card_formulario_agendamento').style.display = 'none';
        })
        .catch(err => alert(err.message));
    }

    window.onload = function() {
        initJanelasSelect();
        // Inicializa buscando do backend se já houver algo cadastrado
        fetch('/api/listar_disponibilidades')
        .then(res => res.json())
        .then(data => {
            bancoLocalOfertas = data;
            atualizarTabelaConsolidada(data);
        });
    };
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ==============================================================================
# CONTROLLERS E ROTAS DA API
# ==============================================================================
@app.route('/')
def index():
    return render_template_string(
        HTML_INTERFACE, 
        lista_balsas=sorted(BALSAS_OPERACIONAIS.keys()), 
        dicionario_balsas=BALSAS_OPERACIONAIS
    )

@app.route('/api/listar_disponibilidades', methods=['GET'])
def api_listar():
    return jsonify(DISPONIBILIDADES_DB)

@app.route('/api/salvar_disponibilidade', methods=['POST'])
def api_salvar():
    req = request.json
    index = int(req.get('index', -1))
    dados = req.get('dados')
    
    if index == -1:
        DISPONIBILIDADES_DB.append(dados)
    else:
        # Preserva os agendamentos já computados se for edição
        for i, jan_antiga in enumerate(DISPONIBILIDADES_DB[index]['janelas_detalhe']):
            if i < len(dados['janelas_detalhe']):
                dados['janelas_detalhe'][i]['ocupadas'] = jan_antiga.get('ocupadas', 0)
                dados['janelas_detalhe'][i]['disponiveis'] = dados['janelas_detalhe'][i]['vagas'] - jan_antiga.get('ocupadas', 0)
        DISPONIBILIDADES_DB[index] = dados
        
    return jsonify(DISPONIBILIDADES_DB)

@app.route('/api/obter_registro/<int:index>', methods=['GET'])
def api_obter(index):
    if 0 <= index < len(DISPONIBILIDADES_DB):
        return jsonify(DISPONIBILIDADES_DB[index])
    return jsonify({}), 404

@app.route('/api/efetuar_agendamento', methods=['POST'])
def api_agendar():
    req = request.json
    o_idx = int(req.get('oferta_index'))
    j_idx = int(req.get('janela_index'))
    
    oferta = DISPONIBILIDADES_DB[o_idx]
    janela = oferta['janelas_detalhe'][j_idx]
    
    if janela['disponiveis'] > 0:
        janela['ocupadas'] += 1
        janela['disponiveis'] -= 1
        
        AGENDAMENTOS_DB.append({
            "balsa": oferta['balsa'],
            "data": oferta['data'],
            "horario": janela['horario'],
            "cavalo": req.get('cavalo'),
            "placa": req.get('placa'),
            "nf": req.get('nf'),
            "volume": req.get('volume'),
            "motorista": req.get('motorista'),
            "cnh": req.get('cnh')
        })
        return jsonify(DISPONIBILIDADES_DB)
    else:
        return jsonify({"erro": "Janela sem vagas"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
