import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

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
    <title>Zion Tecnologia - Gestão de Porto</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; padding: 25px; font-family: sans-serif; }
        .box-janela { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; text-align: center; }
        .input-cota { font-weight: bold; text-align: center; font-size: 18px; }
        .status-badge { padding: 12px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>

    <div class="container-fluid">
        <div class="bg-dark text-white p-3 rounded mb-4">
            <h3>⚓ SISTEMA DE PORTARIA & AGENDAMENTO LOGÍSTICO</h3>
            <p class="m-0 text-info">Módulo 1: Gestão de Disponibilidade (GD)</p>
        </div>

        <div class="row g-4">
            <div class="col-md-4">
                <div class="card shadow-sm">
                    <div class="card-header bg-secondary text-white fw-bold">Configuração da Oferta</div>
                    <div class="card-body">
                        <form id="formOferta" onsubmit="salvarOperacao(event)">
                            <input type="hidden" id="edit_index" value="-1">
                            
                            <div class="mb-3">
                                <label class="form-label fw-bold">Balsa / Embarcação</label>
                                <select class="form-select fw-bold" id="balsa_id" onchange="carregarMetricasBalsa()" required>
                                    <option value="">Selecione...</option>
                                    {% for balsa in lista_balsas %}
                                    <option value="{{ balsa }}">{{ balsa }}</option>
                                    {% endfor %}
                                </select>
                            </div>

                            <div class="row mb-3">
                                <div class="col-6">
                                    <label class="form-label small">Capacidade</label>
                                    <input type="text" class="form-control bg-light" id="cap_view" readonly>
                                </div>
                                <div class="col-6">
                                    <label class="form-label small">Meta (CTS)</label>
                                    <input type="text" class="form-control bg-light" id="cts_view" readonly>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col-6">
                                    <label class="form-label small">Data</label>
                                    <input type="date" class="form-control" id="data_op" required>
                                </div>
                                <div class="col-6">
                                    <label class="form-label small">Hora Início</label>
                                    <input type="time" class="form-control" id="hora_inicio" value="06:00" onchange="gerarGradeJanelas()" required>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label small">Quantidade de Janelas</label>
                                <select class="form-select" id="num_janelas" onchange="gerarGradeJanelas()" required>
                                    <option value="12">12 Janelas Operacionais</option>
                                    <option value="6">6 Janelas Operacionais</option>
                                    <option value="24">24 Janelas Operacionais</option>
                                </select>
                            </div>

                            <button type="submit" class="btn btn-success w-100 fw-bold" id="btn_submit">GRAVAR DISPONIBILIDADE</button>
                        </form>
                    </div>
                </div>
            </div>

            <div class="col-md-8">
                <div class="card shadow-sm">
                    <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between">
                        <span>Distribuição de Vagas por Janela</span>
                        <span id="meta_badge" class="badge bg-info text-dark">Aguardando balsa...</span>
                    </div>
                    <div class="card-body">
                        <div id="status_alocacao" class="status-badge alert-secondary">Configure os dados ao lado.</div>
                        <div class="row g-2" id="grade_container"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mt-4 shadow-sm">
            <div class="card-header bg-secondary text-white fw-bold">Painel de Ofertas Vigentes no Sistema</div>
            <div class="p-3">
                <div id="lista_ofertas_consolidada"></div>
            </div>
        </div>
    </div>

<script>
    const dataBalsas = {{ dicionario_balsas | tojson }};
    let metaNecessaria = 0;
    let dadosTemporariosEdicao = null;

    function carregarMetricasBalsa() {
        const balsa = document.getElementById('balsa_id').value;
        if(balsa && dataBalsas[balsa]) {
            metaNecessaria = dataBalsas[balsa].cts_meta;
            document.getElementById('cap_view').value = dataBalsas[balsa].capacidade;
            document.getElementById('cts_view').value = metaNecessaria + " CTS";
            document.getElementById('meta_badge').innerHTML = `META: ${metaNecessaria} CTS`;
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

            container.innerHTML += `
                <div class="col-md-3">
                    <div class="box-janela">
                        <span class="text-muted small">Janela #${i+1}</span>
                        <div class="fw-bold text-primary small" id="time_j_${i}">${hIni}:${mIni} às ${hFim}:${mFim}</div>
                        <input type="number" class="form-control input-cota mt-1" id="vaga_j_${i}" value="${valorSugerido}" min="0" oninput="validarSaldo()">
                    </div>
                </div>`;
        }
        validarSaldo();
    }

    function validarSaldo() {
        let alocado = 0;
        document.querySelectorAll('.input-cota').forEach(i => alocado += parseInt(i.value) || 0);
        const box = document.getElementById('status_alocacao');
        
        if (alocado === metaNecessaria) {
            box.className = "status-badge bg-success text-white";
            box.innerHTML = `✔ GRADE ALINHADA: ${alocado} de ${metaNecessaria} CTS distribuídos.`;
        } else {
            box.className = "status-badge bg-warning text-dark";
            box.innerHTML = `Diferença detectada: ${alocado} de ${metaNecessaria} CTS. Ajuste os blocos.`;
        }
    }

    function salvarOperacao(event) {
        event.preventDefault();
        let total = 0;
        let janelas = [];
        
        document.querySelectorAll('.input-cota').forEach((i, idx) => {
            let val = parseInt(i.value) || 0;
            total += val;
            janelas.push({
                janela_num: idx + 1,
                horario: document.getElementById(`time_j_${idx}`).innerText,
                vagas: val
            });
        });

        if(total !== metaNecessaria) {
            alert("A soma das janelas deve ser igual à meta!");
            return;
        }

        const dadosForm = {
            balsa: document.getElementById('balsa_id').value,
            data: document.getElementById('data_op').value,
            total_vagas: total,
            janelas_detalhe: janelas
        };

        fetch('/api/salvar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dadosForm)
        })
        .then(res => res.json())
        .then(data => {
            atualizarTabelaConsolidada(data);
            document.getElementById('formOferta').reset();
            document.getElementById('grade_container').innerHTML = "";
        });
    }

    // AQUI ESTÁ A CORREÇÃO SOLICITADA NO VÍDEO:
    // O container.innerHTML = "" limpa a tela antiga antes de desenhar a nova lista atualizada!
    function atualizarTabelaConsolidada(lista) {
        const container = document.getElementById('lista_ofertas_consolidada');
        if(!container) return;
        
        container.innerHTML = ""; // Limpa os dados antigos evitando a duplicação na tela!
        
        if(lista.length === 0) {
            container.innerHTML = '<div class="text-center text-muted">Nenhuma balsa ativa.</div>';
            return;
        }

        lista.forEach((item, idx) => {
            let linhas = "";
            item.janelas_detalhe.forEach(j => {
                linhas += `<tr><td>Janela #${j.janela_num}</td><td>${j.horario}</td><td><b>${j.vagas}</b></td></tr>`;
            });

            container.innerHTML += `
                <div class="card mb-3 border-dark">
                    <div class="card-header bg-light d-flex justify-content-between align-items-center">
                        <span><b>⚓ ${item.balsa}</b> - Data: ${item.data}</span>
                        <button class="btn btn-danger btn-sm" onclick="removerRegra(${idx})">Remover Balsa</button>
                    </div>
                    <table class="table table-sm m-0 table-bordered">
                        <thead><tr><th>Identificador</th><th>Horário</th><th>Vagas</th></tr></thead>
                        <tbody>${linhas}</tbody>
                    </table>
                </div>`;
        });
    }

    function removerRegra(index) {
        fetch(`/api/deletar/${index}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => atualizarTabelaConsolidada(data));
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE, lista_balsas=sorted(BALSAS_OPERACIONAIS.keys()), dicionario_balsas=BALSAS_OPERACIONAIS)

@app.route('/api/salvar', methods=['POST'])
def api_salvar():
    DISPONIBILIDADES_DB.append(request.json)
    return jsonify(DISPONIBILIDADES_DB)

@app.route('/api/deletar/<int:index>', methods=['DELETE'])
def api_deletar(index):
    if 0 <= index < len(DISPONIBILIDADES_DB):
        DISPONIBILIDADES_DB.pop(index)
    return jsonify(DISPONIBILIDADES_DB)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
