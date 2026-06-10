import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# BANCO DE DADOS REAL DAS BALSAS (Mantendo as capacidades e CTS do seu padrão)
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
    <title>Zion - Controle de Pátio Avançado</title>
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
                                <label class="form-label small text-muted">Meta Total Necessária</label>
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

                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label fw-bold text-secondary small">INTERVALO (FREQ.)</label>
                                <select class="form-select" id="frequencia_horas" onchange="recalcularJanelasHorarias()" required>
                                    <option value="1">A cada 1 hora</option>
                                    <option value="2" selected>A cada 2 horas</option>
                                    <option value="3">A cada 3 horas</option>
                                    <option value="4">A cada 4 horas</option>
                                </select>
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-bold text-secondary small">QTD DE JANELAS</label>
                                <select class="form-select fw-bold text-danger" id="qtd_janelas_limite" onchange="recalcularJanelasHorarias()" required>
                                    <option value="4">4 Janelas</option>
                                    <option value="6">6 Janelas</option>
                                    <option value="8">8 Janelas</option>
                                    <option value="12" selected>12 Janelas</option>
                                    <option value="16">16 Janelas</option>
                                    <option value="24">24 Janelas</option>
                                </select>
                            </div>
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
                    <span>⏱️ Distribuição Inteligente de Vagas</span>
                    <span class="badge bg-secondary" id="balsa_titulo_grade">Nenhuma balsa selecionada</span>
                </div>
                <div class="card-body">
                    <p class="small text-muted mb-3">
                        As vagas foram calculadas e divididas igualmente entre as janelas abertas para atingir o teto operacional. Modifique os valores se achar necessário.
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
                        <th>Início</th>
                        <th>Configuração da Grade</th>
                        <th>Total Vagas Distribuídas</th>
                    </tr>
                </thead>
                <tbody id="tabela_ofertas">
                    <tr>
                        <td colspan="5" class="text-center text-muted py-3">Nenhuma regra cadastrada até o momento.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

<script>
    const bancoBalsas = {{ dicionario_balsas | tojson }};
    let metaAtual = 0;

    function recalcularJanelasHorarias() {
        const horaInput = document.getElementById('hora_inicio_operacao').value || "00:00";
        const freqHoras = parseInt(document.getElementById('frequencia_horas').value) || 2;
        const totalJanelasDesejadas = parseInt(document.getElementById('qtd_janelas_limite').value) || 12;
        const container = document.getElementById('grid_janelas_container');
        
        let [horas, minutos] = horaInput.split(':').map(Number);
        container.innerHTML = "";

        // CALCULO AUTOMÁTICO DE QUANTAS VAGAS DEVE TER POR JANELA COM BASE NA META DA BALSA
        let vagasSugeridasPorJanela = 0;
        let restoVagas = 0;
        if (metaAtual > 0) {
            vagasSugeridasPorJanela = Math.floor(metaAtual / totalJanelasDesejadas);
            restoVagas = metaAtual % totalJanelasDesejadas;
        }

        for (let i = 0; i < totalJanelasDesejadas; i++) {
            let hInicio = String(horas).padStart(2, '0');
            let mInicio = String(minutos).padStart(2, '0');
            
            horas = (horas + freqHoras) % 24;
            
            let hFim = String(horas).padStart(2, '0');
            let mFim = String(minutos).padStart(2, '0');

            let faixaFormatada = `${hInicio}:${mInicio} - ${hFim}:${mFim}`;
            let estaDesabilitado = document.getElementById('balsa_selecionada').value ? "" : "disabled";

            // Distribui o valor padrão calculado e soma o resto na primeira janela
            let valorPadraoJanela = vagasSugeridasPorJanela;
            if (i === 0) {
                valorPadraoJanela += restoVagas;
            }

            container.innerHTML += `
                <div class="col-sm-4 col-md-3">
                    <div class="box-janela">
                        <span class="d-block small text-muted fw-bold mb-1">Janela #${i + 1}</span>
                        <span class="d-block extra-small text-dark mb-2" style="font-size:11px; font-weight: 600;">${faixaFormatada}</span>
                        <input type="number" class="form-control form-control-sm input-cota" 
                               id="j_${i}" min="0" value="${estaDesabilitado ? 0 : valorPadraoJanela}" ${estaDesabilitado}
                               oninput="calcularConsumoCotas()">
                    </div>
                </div>`;
        }
        calcularConsumoCotas();
    }

    function atualizarDadosMetricas() {
        const balsa = document.getElementById('balsa_selecionada').value;
        if(balsa && bancoBalsas[balsa]) {
            metaAtual = bancoBalsas[balsa].cts_meta;
            document.getElementById('cap_display').value = bancoBalsas[balsa].capacidade;
            document.getElementById('cts_display').value = metaAtual + " CTS Obrigatórios";
            document.getElementById('balsa_titulo_grade').innerText = `${balsa} (Meta total da balsa: ${metaAtual} CTS)`;
            
            recalcularJanelasHorarias();
        } else {
            metaAtual = 0;
            document.getElementById('cap_display').value = "";
            document.getElementById('cts_display').value = "";
            document.getElementById('balsa_titulo_grade').innerText = "Nenhuma balsa selecionada";
            container.innerHTML = "";
            document.getElementById('status_container').className = "status-badge alert-secondary mb-3";
            document.getElementById('status_container').innerText = "Aguardando seleção da balsa...";
            recalcularJanelasHorarias();
        }
    }

    function calcularConsumoCotas() {
        let totalDigitado = 0;
        document.querySelectorAll('.input-cota').forEach(input => {
            totalDigitado += parseInt(input.value) || 0;
        });

        const statusBox = document.getElementById('status_container');
        if (metaAtual === 0) return;
        
        if (totalDigitado === metaAtual) {
            statusBox.className = "status-badge bg-success text-white mb-3";
            statusBox.innerText = `✅ Perfeito! Grade de vagas balanceada em exatamente ${totalDigitado} de ${metaAtual} CTS.`;
        } else if (totalDigitado > metaAtual) {
            statusBox.className = "status-badge bg-danger text-white mb-3";
            statusBox.innerText = `⚠️ Atenção! O somatório atual deu ${totalDigitado} CTS. Você ultrapassou a meta da balsa que é de ${metaAtual} CTS.`;
        } else {
            statusBox.className = "status-badge bg-warning text-dark mb-3";
            statusBox.innerText = `📊 Alocado: ${totalDigitado} de ${metaAtual} CTS. Faltam ${metaAtual - totalDigitado} CTS para completar a meta da balsa.`;
        }
    }

    function salvarConfiguracaoGeral(e) {
        e.preventDefault();
        let totalDigitado = 0;
        document.querySelectorAll('.input-cota').forEach(input => {
            totalDigitado += parseInt(input.value) || 0;
        });

        if (totalDigitado !== metaAtual) {
            alert(`Impossível salvar: A soma das janelas deu ${totalDigitado} CTS, mas a balsa selecionada exige exatamente ${metaAtual} CTS.`);
            return;
        }

        const dadosForm = {
            balsa: document.getElementById('balsa_selecionada').value,
            data: document.getElementById('data_vigencia').value,
            hora_inicio: document.getElementById('hora_inicio_operacao').value,
            config: document.getElementById('qtd_janelas_limite').value + " janelas de " + document.getElementById('frequencia_horas').value + "h",
            total_vagas: totalDigitado
        };

        fetch('/api/salvar_disponibilidade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dadosForm)
        })
        .then(res => res.json())
        .then(data => {
            alert("Módulo 1 Finalizado! Grade operacional implantada.");
            atualizarTabelaOfertas(data);
            document.getElementById('formOferta').reset();
            atualizarDadosMetricas();
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
                <td><span class="badge bg-info">${item.config}</span></td>
                <td><span class="badge bg-success">${item.total_vagas} CTS Alocados</span></td>
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
