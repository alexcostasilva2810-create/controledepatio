import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# BANCO DE DADOS REAL DAS BALSAS (Mantendo a referência de m³ e teto máximo de CTS)
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
    <title>Zion - Controle de Pátio Dinâmico</title>
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
                <div class="card-header card-header-custom py-3">⚓ Parâmetros de Oferta da Balsa</div>
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
                                <label class="form-label small text-muted">Capacidade Máxima (Meta)</label>
                                <input type="text" class="form-control bg-light fw-bold text-primary" id="cts_display" readonly placeholder="0 CTS">
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label fw-bold text-secondary small">DATA DE VIGÊNCIA</label>
                                <input type="date" class="form-control" id="data_vigencia" required>
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-bold text-secondary small">HORA DO 1º AGENDAMENTO</label>
                                <input type="time" class="form-control" id="hora_inicio_operacao" value="08:00" onchange="recalcularJanelasHorarias()" required>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold text-secondary small">INTERVALO ENTRE AGENDAMENTOS</label>
                            <select class="form-select fw-bold text-primary" id="frequencia_horas" onchange="recalcularJanelasHorarias()" required>
                                <option value="1">A cada 1 hora (Janelas cheias)</option>
                                <option value="2" selected>A cada 2 horas</option>
                                <option value="3">A cada 3 horas</option>
                                <option value="4">A cada 4 horas</option>
                            </select>
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
                    <span>⏱️ Definição de Vagas por Janela Operacional</span>
                    <span class="badge bg-secondary" id="balsa_titulo_grade">Nenhuma balsa selecionada</span>
                </div>
                <div class="card-body">
                    <p class="small text-muted mb-3">
                        Defina a quantidade de vagas livres para o cliente em cada horário. O sistema validará se o total não extrapola a capacidade máxima da balsa.
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
                        <th>Início Operação</th>
                        <th>Frequência</th>
                        <th>Capacidade M³</th>
                        <th>Total Vagas Alocadas</th>
                    </tr>
                </thead>
                <tbody id="tabela_ofertas">
                    <tr>
                        <td colspan="6" class="text-center text-muted py-3">Nenhuma regra de disponibilidade cadastrada até o momento.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

<script>
    const bancoBalsas = {{ dicionario_balsas | tojson }};
    let metaMaxxima = 0;

    function recalcularJanelasHorarias() {
        const horaInput = document.getElementById('hora_inicio_operacao').value || "00:00";
        const freqHoras = parseInt(document.getElementById('frequencia_horas').value) || 2;
        const container = document.getElementById('grid_janelas_container');
        
        let [horas, minutos] = horaInput.split(':').map(Number);
        container.innerHTML = "";

        // Calcula quantas janelas cabem no dia com base na frequência escolhida
        let totalJanelasNoDia = Math.floor(24 / freqHoras);

        for (let i = 0; i < totalJanelasNoDia; i++) {
            let hInicio = String(horas).padStart(2, '0');
            let mInicio = String(minutos).padStart(2, '0');
            
            horas = (horas + freqHoras) % 24;
            
            let hFim = String(horas).padStart(2, '0');
            let mFim = String(minutos).padStart(2, '0');

            let faixaFormatada = `${hInicio}:${mInicio} - ${hFim}:${mFim}`;
            let estaDesabilitado = document.getElementById('balsa_selecionada').value ? "" : "disabled";

            container.innerHTML += `
                <div class="col-sm-4 col-md-3">
                    <div class="box-janela">
                        <span class="d-block small text-muted fw-bold mb-1">Janela #${i + 1}</span>
                        <span class="d-block extra-small text-dark mb-2" style="font-size:11px; font-weight: 600;">${faixaFormatada}</span>
                        <input type="number" class="form-control form-control-sm input-cota" 
                               id="j_${i}" min="0" value="0" ${estaDesabilitado}
                               oninput="calcularConsumoCotas()">
                    </div>
                </div>`;
        }
        calcularConsumoCotas();
    }

    function atualizarDadosMetricas() {
        const balsa = document.getElementById('balsa_selecionada').value;
        if(balsa && bancoBalsas[balsa]) {
            metaMaxxima = bancoBalsas[balsa].cts_meta;
            document.getElementById('cap_display').value = bancoBalsas[balsa].capacidade;
            document.getElementById('cts_display').value = metaMaxxima + " CTS Máx";
            document.getElementById('balsa_titulo_grade').innerText = `${balsa} (Limite Máx: ${metaMaxxima} CTS)`;
            
            document.querySelectorAll('.input-cota').forEach(input => input.disabled = false);
            calcularConsumoCotas();
        } else {
            metaMaxxima = 0;
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
        if (metaMaxxima === 0) return;
        
        if (totalDigitado <= metaMaxxima) {
            statusBox.className = "status-badge bg-success text-white mb-3";
            statusBox.innerText = `✅ Liberado! Você distribuiu ${totalDigitado} de ${metaMaxxima} vagas totais suportadas pela balsa.`;
        } else {
            statusBox.className = "status-badge bg-danger text-white mb-3";
            statusBox.innerText = `⚠️ Atenção! O total de vagas digitadas (${totalDigitado} CTS) ultrapassa o limite estrutural da balsa (${metaMaxxima} CTS). Reduza as vagas.`;
        }
    }

    function salvarConfiguracaoGeral(e) {
        e.preventDefault();
        let totalDigitado = 0;
        document.querySelectorAll('.input-cota').forEach(input => {
            totalDigitado += parseInt(input.value) || 0;
        });

        if (totalDigitado > metaMaxxima) {
            alert(`Erro: O total de vagas (${totalDigitado}) não pode ser maior que o limite da balsa (${metaMaxxima}).`);
            return;
        }

        const dadosForm = {
            balsa: document.getElementById('balsa_selecionada').value,
            data: document.getElementById('data_vigencia').value,
            hora_inicio: document.getElementById('hora_inicio_operacao').value,
            frequencia: document.getElementById('frequencia_horas').value + "h",
            capacidade: document.getElementById('cap_display').value,
            total_vagas: totalDigitado
        };

        fetch('/api/salvar_disponibilidade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dadosForm)
        })
        .then(res => res.json())
        .then(data => {
            alert("Disponibilidade de janelas e vagas salva com sucesso!");
            atualizarTabelaOfertas(data);
            document.getElementById('formOferta').reset();
            atualizarDadosMetricas();
            recalcularJanelasHorarias();
        });
    }

    function atualizarTabelaOfertas(lista) {
        const tbody = document.getElementById('tabela_ofertas');
        if(!lista || lista.length === 0) return;
        tbody.innerHTML = "";
        lista.forEach(item => {
            tbody.innerHTML += `<tr>
                <td><b>${item.balsa}</b></td>
                <td>${item.data}</td>
                <td><span class="badge bg-dark">${item.hora_inicio}h</span></td>
                <td><span class="badge bg-info">A cada ${item.frequencia}</span></td>
                <td>${item.capacidade}</td>
                <td><span class="badge bg-success">${item.total_vagas} Vagas Criadas</span></td>
            </tr>`;
        });
    }

    window.onload = recalcularJanelasHorarias;
</script>
</body>
</html>
"""

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
