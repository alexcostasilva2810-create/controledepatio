import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
application = app  # Fornece compatibilidade adicional para servidores WSGI

# ==============================================================================
# BANCO DE DADOS OPERACIONAL (BALSAS, CAPACIDADES E CTS)
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
    "SD XVIII": {"capacidade": "795.6 m³", "cts_meta": 13},
    "SD XX": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXI": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "SD XXIII": {"capacidade": "2998.8 m³", "cts_meta": 49},
    "TWB 200": {"capacidade": "2142.0 m³", "cts_meta": 35}
}

DISPONIBILIDADES_DB = []

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Zion - Criação de Disponibilidade Master</title>
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
    </style>
</head>
<body>

    <div class="navbar-top d-flex justify-content-between align-items-center shadow-lg">
        <div>
            <h4 class="m-0 fw-bold"><i class="fa-solid fa-anchor me-2"></i>SISTEMA DE AGENDAMENTO LOGÍSTICO</h4>
            <small style="color: var(--accent);">Painel de Criação de Disponibilidade - Zion Tecnologia</small>
        </div>
        <span class="badge bg-light text-dark px-3 py-2 fw-bold">MÓDULO 1: DISPONIBILIDADE</span>
    </div>

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
        <div class="card-header card-header-custom text-white bg-secondary"><i class="fa-solid fa-list-check me-2"></i>Painel de Ofertas Vigentes no Sistema</div>
        <div class="p-3">
            <div id="lista_ofertas_consolidada">
                <div class="text-center text-muted py-3">Nenhuma regra cadastrada até o momento.</div>
            </div>
        </div>
    </div>

<script>
    const dataBalsas = {{ dicionario_balsas | tojson }};
    let metaNecessaria = 0;
    let dadosTemporariosEdicao = null;

    function initJanelasSelect() {
        const sel = document.getElementById('num_janelas');
        sel.innerHTML = "";
        for (let i = 6; i <= 24; i++) {
            let opt = document.createElement('option');
            opt.value = i;
            opt.innerHTML = `${i} Janelas Operacionais`;
            if(i === 12) opt.selected = true;
            sel.appendChild(opt);
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
        
        if(!metaNecessaria) return;

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
                        <td class="text-center fw-bold text-danger">${j.ocupadas}</td>
                        <td class="text-center fw-bold text-success bg-light">${j.disponiveis}</td>
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

    window.onload = function() {
        initJanelasSelect();
    };
</script>
</body>
</html>
"""

# ==============================================================================
# ENDPOINTS API REST
# ==============================================================================
@app.route('/')
def index():
    return render_template_string(
        HTML_INTERFACE, 
        lista_balsas=sorted(BALSAS_OPERACIONAIS.keys()), 
        dicionario_balsas=BALSAS_OPERACIONAIS
    )

@app.route('/api/salvar_disponibilidade', methods=['POST'])
def api_salvar():
    req = request.json
    index = int(req.get('index', -1))
    dados = req.get('dados')
    
    if index == -1:
        DISPONIBILIDADES_DB.append(dados)
    else:
        DISPONIBILIDADES_DB[index] = dados
        
    return jsonify(DISPONIBILIDADES_DB)

@app.route('/api/obter_registro/<int:index>', methods=['GET'])
def api_obter(index):
    if 0 <= index < len(DISPONIBILIDADES_DB):
        return jsonify(DISPONIBILIDADES_DB[index])
    return jsonify({}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
