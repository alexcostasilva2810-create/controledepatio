import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==============================================================================
# BANCO DE DADOS REAL DAS BALSAS E SEUS RESPECTIVOS CTS
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

# Armazenamento temporário das disponibilidades criadas (Simulando o Banco de Dados)
DISPONIBILIDADES_DB = []

# ==============================================================================
# INTERFACE DO USUÁRIO - CONTROLE GERENCIAL DE PÁTIO & COTAS
# ==============================================================================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Zion - Controle de Pátio e Cadastro de Cotas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; padding: 25px; }
        .navbar-top { background-color: #0f172a; color: white; padding: 15px 25px; border-radius: 8px; margin-bottom: 25px; }
        .card-custom { border: none; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); background: white; }
        .card-header-custom { background-color: #1e293b; color: white; font-weight: bold; border-radius: 8px 8px 0 0 !important; }
        .box-janela { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; text-align: center; transition: all 0.2s; }
        .box-janela:hover { border-color: #3b82f6; background: #eff6ff; }
        .input-cota { font-weight: bold; text-align: center; }
        .status-badge { font-size: 14px; font-weight: bold; padding: 10px; border-radius: 6px; display: block; text-align: center; }
    </style>
</head>
<body>

    <div class="navbar-top d-flex justify-content-between align-items-center">
        <div>
            <h4 class="m-0 fw-bold">SISTEMA DE PORTARIA & AGENDAMENTO LOGÍSTICO</h4>
            <small class="text-muted">Painel de Configuração Master - Zion Tecnologia</small>
        </div>
        <span class="badge bg-primary px-3 py-2">MÓDULO 1: GESTÃO DE DISPONIBILIDADE</span>
    </div>

    <div class="row g-4">
        <div class="col-lg-5">
            <div class="card card-custom mb-4">
                <div class="card-header card-header-custom py-3">⚓ Cadastro de Oferta de Balsa</div>
                <div class="card-body">
                    <form id="formOferta" onsubmit="salvarConfiguracaoGeral(event)">
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold text-secondary small">LOCALIDADE / EMBARCAÇÃO</label>
                            <select class="form-select form-select-lg" id="balsa_selecionada" onchange="atualizarDadosMetricas()" required>
                                <option value="">Selecione a Balsa Ofertada...</option>
                                {% for balsa in lista_balsas %}
                                <option value="{{ balsa }}">{{ balsa }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label small text-muted">Capacidade Volumétrica</label>
                                <input type="text" class="form-control bg-light fw-bold text-dark" id="cap_display" readonly placeholder="0.0 m³">
                            </div>
                            <div class="col-6">
                                <label class="form-label small text-muted">Exigência Física (Meta)</label>
                                <input type="text" class="form-control bg-light fw-bold text-primary" id="cts_display" readonly placeholder="0 CTS">
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold text-secondary small">VIGÊNCIA DA DISPONIBILIDADE (A PARTIR DE)</label>
                            <input type="date" class="form-control" id="data_vigencia" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold text-secondary small">DIVISÃO DE JANELAS DIÁRIAS</label>
                            <select class="form-select" id="grade_janelas" disabled>
                                <option value="12">12 Janelas diárias (Intervalos de 02:00h às 22:00h)</option>
                            </select>
                            <small class="text-muted">Padrão operacional travado em 12 blocos de atendimento.</small>
                        </div>

                        <div class="d-grid mt-4">
                            <button type="submit" class="btn btn-success btn-lg fw-bold text-uppercase">Gravar e Liberar Janelas</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="col-lg-7">
            <div class="card card-custom">
                <div class="card-header bg-dark text-white py-3 d-flex justify-content-between align-items-center">
                    <span>⏱️ Distribuição de Cargas Horárias (Cotas / CTS)</span>
                    <span class="badge bg-secondary" id="balsa_titulo_grade">Nenhuma balsa selecionada</span>
                </div>
                <div class="card-body">
                    <p class="small text-muted mb-3">
                        Informe abaixo a quantidade de <b>CTS</b> permitida para descarregar em cada faixa de horário. O total distribuído deve bater rigorosamente com a exigência da balsa.
                    </p>

                    <div id="status_container" class="status-badge alert-secondary mb-3">
                        Aguardando seleção da balsa...
                    </div>

                    <div class="row g-3" id="grid_janelas_container">
                        </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card card-custom mt-4">
        <div class="card-header card-header-custom py-3 text-white">📋 Painel de Ofertas Vigentes no Sistema</div>
        <div class="table-responsive">
            <table class="table table-striped align-middle m-0">
                <thead class="table-dark">
                    <tr>
                        <th>Balsa</th>
                        <th>Data Vigência</th>
                        <th>Capacidade</th>
                        <th>CTS Total</th>
                        <th>Status do Pátio</th>
                    </tr>
                </thead>
                <tbody id="tabela_ofertas">
                    <tr>
                        <td colspan="5" class="text-center text-muted py-3">Nenhuma regra de disponibilidade cadastrada até o momento.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

<script>
    const bancoBalsas = {{ dicionario_balsas | tojson }};
    let metaAtual = 0;

    // Definição estática das 12 janelas operacionais padrão (2h em 2h iniciando às 00:00)
    const faixasHorarias = [
        "00:00 - 02:00", "02:00 - 04:00", "04:00 - 06:00", "06:00 - 08:00",
        "08:00 - 10:00", "10:00 - 12:00", "12:00 - 14:00", "14:00 - 16:00",
        "16:00 - 18:00", "18:00 - 20:00", "20:00 - 22:00", "22:00 - 00:00"
    ];

    function renderizarGradeVazia() {
        const container = document.getElementById('grid_janelas_container');
        container.innerHTML = "";
        faixasHorarias.forEach((faixa, index) => {
            container.innerHTML += `
                <div class="col-sm-4 col-md-3">
                    <div class="box-janela">
                        <span class="d-block small text-muted fw-bold mb-1">Janela #${index + 1}</span>
                        <span class="d-block extra-small text-dark mb-2" style="font-size:11px;">${faixa}</span>
                        <input type="number" class="form-control form-control-sm input-cota" 
                               id="j_${index}" min="0" value="0" disabled
                               oninput="calcularConsumoCotas()">
                    </div>
                </div>`;
        });
    }

    function atualizarDadosMetricas() {
        const balsa = document.getElementById('balsa_selecionada').value;
        if(balsa && bancoBalsas[balsa]) {
            metaAtual = bancoBalsas[balsa].cts_meta;
            document.getElementById('cap_display').value = bancoBalsas[balsa].capacidade;
            document.getElementById('cts_display').value = metaAtual + " CTS";
            document.getElementById('balsa_titulo_grade').innerText = `${balsa} (Meta: ${metaAtual} CTS)`;
            
            // Habilita os inputs da grade
            document.querySelectorAll('.input-cota').forEach(input => input.disabled = false);
            calcularConsumoCotas();
        } else {
            metaAtual = 0;
            document.getElementById('cap_display').value = "";
            document.getElementById('cts_display').value = "";
            document.getElementById('balsa_titulo_grade').innerText = "Nenhuma balsa selecionada";
            document.querySelectorAll('.input-cota').forEach(input => { input.value = 0; input.disabled = true; });
            document.getElementById('status_container').className = "status-badge alert-secondary mb-3";
            document.getElementById('status_container').innerText = "Aguardando seleção da balsa...";
        }
    }

    function calcularConsumoCotas() {
        let totalDigitado = 0;
        document.querySelectorAll('.input-cota').forEach(input => {
            totalDigitado += parseInt(input.value) || 0;
        });

        const statusBox = document.getElementById('status_container');
        
        if (totalDigitado === metaAtual && metaAtual > 0) {
            statusBox.className = "status-badge bg-success text-white mb-3";
            statusBox.innerText = `✅ Perfeito! Distribuição igual à exigência da balsa (${totalDigitado} de ${metaAtual} CTS).`;
        } else if (totalDigitado > metaAtual) {
            statusBox.className = "status-badge bg-danger text-white mb-3";
            statusBox.innerText = `⚠️ Extrapolou! Você distribuiu ${totalDigitado} CTS, mas a balsa aceita apenas ${metaAtual}. Reduza os valores.`;
        } else {
            statusBox.className = "status-badge bg-warning text-dark mb-3";
            statusBox.innerText = `📊 Alocando: ${totalDigitado} de ${metaAtual} CTS digitados. Distribua o restante nas janelas livres.`;
        }
    }

    function salvarConfiguracaoGeral(e) {
        e.preventDefault();
        let totalDigitado = 0;
        document.querySelectorAll('.input-cota').forEach(input => {
            totalDigitado += parseInt(input.value) || 0;
        });

        if (totalDigitado !== metaAtual) {
            alert(`Erro na validação: Você inseriu ${totalDigitado} CTS no total, porém essa embarcação exige exatamente ${metaAtual} CTS.`);
            return;
        }

        const dadosForm = {
            balsa: document.getElementById('balsa_selecionada').value,
            data: document.getElementById('data_vigencia').value,
            capacidade: document.getElementById('cap_display').value,
            cts: metaAtual
        };

        fetch('/api/salvar_disponibilidade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dadosForm)
        })
        .then(res => res.json())
        .then(data => {
            alert("Disponibilidade e Grade de Cotas criadas com sucesso!");
            atualizarTabelaOfertas(data);
            document.getElementById('formOferta').reset();
            atualizarDadosMetricas();
        });
    }

    function atualizarTabelaOfertas(lista) {
        const tbody = document.getElementById('tabela_ofertas');
        if(!lista || lista.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-3">Nenhuma regra de disponibilidade cadastrada até o momento.</td></tr>`;
            return;
        }
        tbody.innerHTML = "";
        lista.forEach(item => {
            tbody.innerHTML += `<tr>
                <td><b>${item.balsa}</b></td>
                <td>${item.data}</td>
                <td>${item.capacidade}</td>
                <td><span class="badge bg-primary">${item.cts} CTS</span></td>
                <td><span class="badge bg-success">Janelas Livres para Clientes</span></td>
            </tr>`;
        });
    }

    window.onload = renderizarGradeVazia;
</script>
</body>
</html>
"""

# ==============================================================================
# PROCESSAMENTO DE DADOS (ENDPOINTS API)
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
    dados = request.json
    DISPONIBILIDADES_DB.append(dados)
    return jsonify(DISPONIBILIDADES_DB)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
