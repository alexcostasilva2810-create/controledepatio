import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==============================================================================
# DICIONÁRIO DE BALSAS BASEADO NA TABELA REAL (Capacidade m³ e CTS)
# ==============================================================================
BALSAS_CADASTRADAS = {
    "SD I": {"capacidade": 1040.4, "cts": 17},
    "SD II": {"capacidade": 1530.0, "cts": 25},
    "SD IV": {"capacidade": 2325.6, "cts": 38},
    "SD V": {"capacidade": 2325.6, "cts": 38},
    "SD VI": {"capacidade": 1407.6, "cts": 23},
    "SD VII": {"capacidade": 1468.8, "cts": 24},
    "SD VIII": {"capacidade": 1407.6, "cts": 23},
    "SD IX": {"capacidade": 1407.6, "cts": 23},
    "SD X": {"capacidade": 1407.6, "cts": 23},
    "SD XI": {"capacidade": 2325.6, "cts": 38},
    "SD XII": {"capacidade": 2325.6, "cts": 38},
    "SD XIII": {"capacidade": 2325.6, "cts": 38},
    "SD XIV": {"capacidade": 1468.8, "cts": 24},
    "SD XV": {"capacidade": 1407.6, "cts": 23},
    "SD XVI": {"capacidade": 1407.6, "cts": 23},
    "SD XVII": {"capacidade": 1468.8, "cts": 24},
    "SD XVIII": {"capacidade": 795.6, "cts": 13},
    "SD XX": {"capacidade": 2998.8, "cts": 49},
    "SD XXI": {"capacidade": 2998.8, "cts": 49},
    "SD XXII": {"capacidade": 2998.8, "cts": 49},
    "SD XXIII": {"capacidade": 2998.8, "cts": 49},
    "TWB 200": {"capacidade": 2142.0, "cts": 35}
}

HTML_DISPONIBILIDADE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Zion - Criação de Disponibilidade e Cotas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --primary: #0a2647; --secondary: #144272; --accent: #2c74b3; --gray: #f4f6f9; }
        body { font-family: 'Segoe UI', sans-serif; background-color: var(--gray); padding: 30px; }
        .card-header-zion { background-color: var(--primary); color: white; font-weight: bold; }
        .btn-primary-zion { background-color: var(--primary); color: white; border: none; }
        .btn-primary-zion:hover { background-color: var(--secondary); color: white; }
        .info-destaque { background-color: #e2e8f0; font-weight: bold; border-left: 4px solid var(--accent); }
        .janela-box { border: 1px solid #cbd5e1; padding: 10px; border-radius: 6px; background: #fff; text-align: center; }
    </style>
</head>
<body>

<div class="container-fluid max-width-1200">
    <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
        <div>
            <h2 class="fw-bold" style="color: var(--primary);">MÓDULO 1: CRIAÇÃO DE DISPONIBILIDADE</h2>
            <p class="text-muted m-0">Painel de Input de Ofertas, Escalas de Balsas e Definição de Janelas Horárias</p>
        </div>
        <span class="badge bg-dark p-2">MODO CONFIGURAÇÃO PRINCIPAL</span>
    </div>

    <div class="row g-4">
        <div class="col-lg-5">
            <div class="card shadow-sm border-0">
                <div class="card-header card-header-zion py-3">1. Dados da Embarcação & Período</div>
                <div class="card-body">
                    <form id="formDisponibilidade" onsubmit="processarDisponibilidade(event)">
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold text-uppercase small">Selecione a Balsa Ofertada</label>
                            <select class="form-select form-select-lg" id="balsa_nome" onchange="buscarDadosBalsa()" required>
                                <option value="">Escolha a Balsa...</option>
                                {% for balsa in lista_balsas %}
                                <option value="{{ balsa }}">{{ balsa }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label small text-muted">Capacidade Vinculada</label>
                                <input type="text" class="form-control info-destaque" id="balsa_cap" readonly placeholder="0.0 m³">
                            </div>
                            <div class="col-6">
                                <label class="form-label small text-muted">Total de CTS Exigidos</label>
                                <input type="text" class="form-control info-destaque text-primary" id="balsa_cts" readonly placeholder="0 CTS">
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold text-uppercase small">A partir de qual data?</label>
                            <input type="date" class="form-control" id="data_inicio" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold text-uppercase small">Quantidade de Janelas por dia</label>
                            <select class="form-select" id="qtd_janelas" onchange="gerarGradeJanelas()" required>
                                <option value="1">1 Janela diária</option>
                                <option value="2">2 Janelas diárias</option>
                                <option value="4">4 Janelas diárias</option>
                                <option value="6">6 Janelas diárias</option>
                                <option value="8">8 Janelas diárias</option>
                                <option value="12" selected>12 Janelas diárias (Recomendado - 2h em 2h)</option>
                            </select>
                        </div>

                        <hr>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary-zion btn-lg fw-bold">Gravar e Liberar para Clientes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="col-lg-7">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-dark text-white fw-bold py-3">
                    2. Distribuição das Janelas (Quantidade de CTS por Hora)
                </div>
                <div class="card-body">
                    <p class="small text-muted mb-3">
                        Distribua o montante de CTS nas janelas abaixo para definir o ritmo de descarga diário. O sistema monitora o saldo em tempo real.
                    </p>
                    
                    <div class="alert alert-warning d-flex justify-content-between align-items-center py-2 px-3 fw-bold">
                        <span>Total de CTS Alocado: <span id="cts_distribuidos">0</span></span>
                        <span>Meta da Balsa: <span id="cts_meta">0</span></span>
                    </div>

                    <div id="containerGradeJanelas" class="row g-3">
                        </div>

                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // Dicionário passado do Python para o Front-end
    const dadosBalsas = {{ dicionario_balsas | tojson }};

    function buscarDadosBalsa() {
        const balsaSel = document.getElementById('balsa_nome').value;
        if(balsaSel && dadosBalsas[balsaSel]) {
            document.getElementById('balsa_cap').value = dadosBalsas[balsaSel].capacidade + " m³";
            document.getElementById('balsa_cts').value = dadosBalsas[balsaSel].cts + " CTS";
            document.getElementById('cts_meta').innerText = dadosBalsas[balsaSel].cts;
            gerarGradeJanelas();
        } else {
            document.getElementById('balsa_cap').value = "";
            document.getElementById('balsa_cts').value = "";
            document.getElementById('cts_meta').innerText = "0";
        }
    }

    function gerarGradeJanelas() {
        const numJanelas = parseInt(document.getElementById('qtd_janelas').value) || 0;
        const container = document.getElementById('containerGradeJanelas');
        container.innerHTML = "";

        // Calcula dinamicamente o intervalo com base nas janelas selecionadas
        const intervaloHoras = 24 / numJanelas;

        for (let i = 0; i < numJanelas; i++) {
            const horaInicio = String(Math.floor(i * intervaloHoras)).padStart(2, '0');
            const horaFim = String(Math.floor((i + 1) * intervaloHoras)).padStart(2, '0');
            
            const div = document.createElement('div');
            div.className = "col-sm-4 col-md-3";
            div.innerHTML = `
                <div class="janela-box">
                    <label class="fw-bold small text-primary d-block mb-1">${horaInicio}:00 - ${horaFim}:00</label>
                    <input type="number" class="form-control form-control-sm text-center input-cts-janela" 
                           min="0" value="0" onchange="calcularTotalCtsInseridos()" onkeyup="calcularTotalCtsInseridos()">
                    <span class="text-muted extra-small" style="font-size: 10px;">Qtd CTS</span>
                </div>
            `;
            container.appendChild(div);
        }
        calcularTotalCtsInseridos();
    }

    function calcularTotalCtsInseridos() {
        let total = 0;
        document.querySelectorAll('.input-cts-janela').forEach(input => {
            total += parseInt(input.value) || 0;
        });
        
        const ctsMeta = parseInt(document.getElementById('cts_meta').innerText) || 0;
        const displayTotal = document.getElementById('cts_distribuidos');
        
        displayTotal.innerText = total;
        
        if(total === ctsMeta && ctsMeta > 0) {
            displayTotal.parentElement.className = "alert alert-success d-flex justify-content-between align-items-center py-2 px-3 fw-bold";
        } else if (total > ctsMeta) {
            displayTotal.parentElement.className = "alert alert-danger d-flex justify-content-between align-items-center py-2 px-3 fw-bold";
        } else {
            displayTotal.parentElement.className = "alert alert-warning d-flex justify-content-between align-items-center py-2 px-3 fw-bold";
        }
    }

    function processarDisponibilidade(e) {
        e.preventDefault();
        const balsa = document.getElementById('balsa_nome').value;
        const totalAlocado = parseInt(document.getElementById('cts_distribuidos').innerText);
        const meta = parseInt(document.getElementById('cts_meta').innerText);

        if(totalAlocado !== meta) {
            alert(`Atenção: Você alocou ${totalAlocado} CTS, mas a balsa ${balsa} exige exatamente ${meta} CTS para fechar a escala.`);
            return;
        }

        alert("Módulo 1 Pronto! Disponibilidade de Janelas e Cotas salva com sucesso no ecossistema.");
    }

    // Inicializa a grade ao carregar a página
    window.onload = function() {
        gerarGradeJanelas();
    };
</script>

</body>
</html>
"""

@app.route('/')
def modulo_disponibilidade():
    return render_template_string(
        HTML_DISPONIBILIDADE, 
        lista_balsas=sorted(BALSAS_CADASTRADAS.keys()),
        dicionario_balsas=BALSAS_CADASTRADAS
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
