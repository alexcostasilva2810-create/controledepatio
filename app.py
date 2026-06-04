import os
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, send_file
import qrcode
import io
from fpdf import FPDF

app = Flask(__name__)

# SEU APP SCRIPT URL ATUALIZADO
URL_PLANILHA_GOOGLE = "https://script.google.com/macros/s/AKfycbxlzebvfA0GQcAyQ1Oc9IFC6XX9t4mR7cOLzj4jt8sX0B2YZoozCuTzlAnZHeL8aHjr/exec"

# ==========================================
# INTERFACE WEB RESTRUTURADA
# ==========================================
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Logística Integrada - Controle de Pátio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root { --primary: #0a2647; --secondary: #144272; --accent: #2c74b3; --success: #1b4d3e; }
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background-color: #f4f6f9; color: #333; }
        .navbar { background: var(--primary); padding: 20px; text-align: center; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
        .navbar h1 { margin: 0; font-size: 22px; letter-spacing: 1px; font-weight: 600; }
        .container { max-width: 1200px; margin: 25px auto; padding: 0 20px; }
        
        .tabs { display: flex; margin-bottom: 25px; gap: 4px; }
        .tab-button { flex: 1; background: #e2e8f0; border: none; padding: 15px; font-size: 15px; font-weight: bold; color: #4a5568; cursor: pointer; border-radius: 6px 6px 0 0; transition: 0.2s; }
        .tab-button.active { background: white; color: var(--primary); border-bottom: 4px solid var(--accent); }
        
        .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: none; }
        .card.active { display: block; }

        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
        .form-group { display: flex; flex-direction: column; }
        .full-width { grid-column: span 2; }
        @media(max-width: 768px) { .full-width { grid-column: span 1; } }
        
        label { font-size: 12px; font-weight: 700; color: #4a5568; margin-bottom: 6px; text-transform: uppercase; }
        input { padding: 11px; border: 1.5px solid #cbd5e1; border-radius: 6px; font-size: 14px; background: #fafafa; transition: 0.2s; }
        input:focus { border-color: var(--accent); background: white; outline: none; box-shadow: 0 0 0 3px rgba(44,116,179,0.15); }
        
        .btn { padding: 14px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; transition: 0.2s; font-size: 14px; }
        .btn-submit { background-color: var(--success); color: white; width: 100%; margin-top: 15px; font-size: 15px; }
        .btn-submit:hover { background-color: #12342a; }
        .btn-csv { background-color: var(--primary); color: white; }
        
        .filter-bar { background: #e2e8f0; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 15px; align-items: flex-end; flex-wrap: wrap; }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; min-width: 1100px; }
        th { background-color: var(--primary); color: white; padding: 12px 10px; font-weight: 600; }
        td { padding: 12px 10px; border-bottom: 1px solid #e2e8f0; }
        tr:nth-child(even) { background-color: #f8fafc; }
    </style>
</head>
<body>

    <div class="navbar">
        <h1>SISTEMA DE PORTARIA & AGENDAMENTO LOGÍSTICO</h1>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('cadastro')">📝 Novo Registro de Entrada</button>
            <button class="tab-button" onclick="switchTab('painel')">📊 Histórico de Fluxo & Relatórios</button>
        </div>

        <div id="cadastro" class="card active">
            <form action="/agendar" method="POST" class="form-grid">
                <div class="form-group"><label>Saída da Origem</label><input type="datetime-local" name="saida_origem" required></div>
                <div class="form-group"><label>Previsão de Chegada</label><input type="datetime-local" name="prev_chegada" required></div>
                <div class="form-group"><label>Chegada no Posto</label><input type="datetime-local" name="chegada_posto" required></div>
                <div class="form-group"><label>Nº Nota Fiscal</label><input type="text" name="num_nota" required placeholder="Ex: 374839"></div>
                <div class="form-group"><label>Placa do Veículo</label><input type="text" name="placa" required placeholder="Ex: EUK9C95"></div>
                <div class="form-group"><label>Número do Lacre</label><input type="text" name="lacre" required placeholder="Ex: 562374"></div>
                <div class="form-group full-width"><label>Nome do Motorista</label><input type="text" name="motorista" required></div>
                <div class="form-group"><label>Transportadora</label><input type="text" name="transportadora" required placeholder="Ex: AGROLOG"></div>
                <div class="form-group"><label>Cliente Destinatário</label><input type="text" name="cliente" required placeholder="Ex: ABBA MANAUS"></div>
                <div class="form-group"><label>Cidade de Destino</label><input type="text" name="destino" required placeholder="Ex: MANAUS"></div>
                <div class="form-group"><label>Contato do Motorista</label><input type="text" name="telefone" required placeholder="Ex: (66) 99600-1291"></div>
                <div class="form-group"><label>Produto</label><input type="text" name="produto" required placeholder="Ex: ANIDRO"></div>
                <div class="form-group"><label>Volume a 20º</label><input type="text" name="vol20" required placeholder="Ex: 61.534"></div>
                
                <div class="full-width">
                    <button type="submit" class="btn btn-submit">Validar Entrada & Emitir Ticket PDF</button>
                </div>
            </form>
        </div>

        <div id="painel" class="card">
            <div class="filter-bar">
                <div class="form-group"><label>Data Inicial:</label><input type="date" id="filtroDataInicio"></div>
                <div class="form-group"><label>Data Final:</label><input type="date" id="filtroDataFim"></div>
                <button class="btn btn-csv" onclick="baixarRelatorioPeriodo()">📥 Exportar Período (CSV)</button>
            </div>
            
            <div class="table-container">
                <table id="tabelaDados">
                    <thead>
                        <tr>
                            <th>SEQ</th><th>SAÍDA ORIGEM</th><th>PREV. CHEGADA</th><th>CHEGADA POSTO</th>
                            <th>T1-TRÂNSITO</th><th>Nº NOTA</th><th>PLACA</th><th>LACRE</th>
                            <th>MOTORISTA</th><th>TRANSPORTADORA</th><th>PRODUTO</th><th>VOL 20º</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for reg in registros %}
                        <tr data-date="{{ reg.chegada_posto }}">
                            <td style="font-weight: bold; color: #2c74b3;">#{{ "%04d" | format(reg.sequencial | int) }}</td>
                            <td>{{ reg.saida_origem }}</td>
                            <td>{{ reg.prev_chegada }}</td>
                            <td>{{ reg.chegada_posto }}</td>
                            <td style="font-weight: 600; color: #206a5d;">{{ reg.t1_transito }}</td>
                            <td>{{ reg.num_nota }}</td>
                            <td style="font-weight: 600;">{{ reg.placa }}</td>
                            <td>{{ reg.lacre }}</td>
                            <td>{{ reg.motorista }}</td>
                            <td>{{ reg.transportadora }}</td>
                            <td>{{ reg.produto }}</td>
                            <td>{{ reg.vol20 }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        function baixarRelatorioPeriodo() {
            let inicio = document.getElementById('filtroDataInicio').value;
            let fim = document.getElementById('filtroDataFim').value;
            let csv = "\\ufeffSEQUENCIA,SAIDA ORIGEM,PREV CHEGADA,CHEGADA POSTO,T1-TRANSITO,N NOTA,PLACA,LACRE,NOME MOTORISTA,TRANSPORTADORA,PRODUCTO,VOL 20\\n";
            let linhas = document.querySelectorAll("#tabelaDados tbody tr");
            let encontrou = false;

            linhas.forEach(tr => {
                let txtData = tr.getAttribute('data-date'); 
                if(!txtData) return;
                let partes = txtData.split(' ')[0].split('/');
                let dataFormatada = partes[2] + "-" + partes[1] + "-" + partes[0];

                let valido = true;
                if(inicio && dataFormatada < inicio) valido = false;
                if(fim && dataFormatada > fim) valido = false;

                if(valido) {
                    encontrou = true;
                    let cols = tr.querySelectorAll("td");
                    let dadosLinha = [];
                    cols.forEach(td => { dadosLinha.push('"' + td.innerText.replace(/"/g, '""') + '"'); });
                    csv += dadosLinha.join(",") + "\\n";
                }
            });

            if(!encontrou) { alert("Nenhum registro encontrado para o período!"); return; }
            let blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            let link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `relatorio_patio.csv`;
            link.click();
        }
    </script>
</body>
</html>
"""

def processar_e_calcular_dados(form):
    def formatar_data_br(data_html):
        try: return datetime.strptime(data_html, '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M')
        except: return data_html

    saida = form.get('saida_origem')
    chegada = form.get('chegada_posto')
    
    t1_transito = "00:00"
    try:
        dt_saida = datetime.strptime(saida, '%Y-%m-%dT%H:%M')
        dt_chegada = datetime.strptime(chegada, '%Y-%m-%dT%H:%M')
        diff = dt_chegada - dt_saida
        total_segundos = int(diff.total_seconds())
        if total_segundos > 0:
            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60
            t1_transito = f"{horas:02d}:{minutos:02d}"
    except: pass

    return {
        "saida_origem": formatar_data_br(saida),
        "prev_chegada": formatar_data_br(form.get('prev_chegada')),
        "chegada_posto": formatar_data_br(chegada),
        "t1_transito": t1_transito,
        "num_nota": form.get('num_nota').strip(),
        "placa": form.get('placa').upper().strip(),
        "lacre": form.get('lacre').strip(),
        "motorista": form.get('motorista').upper().strip(),
        "transportadora": form.get('transportadora').upper().strip(),
        "cliente": form.get('cliente').upper().strip(),
        "destino": form.get('destino').upper().strip(),
        "telefone": form.get('telefone').strip(),
        "produto": form.get('produto').upper().strip(),
        "vol20": form.get('vol20').strip()
    }

@app.route('/')
def index():
    try:
        r = requests.get(URL_PLANILHA_GOOGLE, timeout=10)
        registros = r.json() if r.status_code == 200 else []
        registros.reverse()
    except: registros = []
    return render_template_string(HTML_SISTEMA, registros=registros)

@app.route('/agendar', methods=['POST'])
def agendar():
    dados = processar_e_calcular_dados(request.form)
    seq_gerado = "1"
    try:
        resp = requests.post(URL_PLANILHA_GOOGLE, json=dados, timeout=12)
        if resp.status_code == 200: seq_gerado = resp.json().get('sequencial', '1')
    except: pass

    # GERANDO PDF REESTRUTURADO E SEGURO CONTRA CORTES
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Faixa Azul superior limpa
    pdf.set_fill_color(10, 38, 71)
    pdf.rect(0, 0, 210, 35, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(180, 10, "TICKET DE ENTRADA OPERACIONAL", 0, 1, 'C')
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(180, 5, "Módulo Automatizado de Logística de Pátio", 0, 1, 'C')
    
    pdf.ln(15)
    pdf.set_text_color(0, 0, 0)
    
    # Campo ID destacado
    pdf.set_fill_color(240, 244, 248)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(180, 9, f" SEQUENCIAL REGISTRO: #{int(seq_gerado):04d}", 0, 1, 'L', True)
    pdf.ln(3)

    def desenhar_item(campo, info):
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(50, 7, f" {campo}:", 'B', 0)
        pdf.set_font("Arial", '', 9)
        pdf.cell(130, 7, f" {info}", 'B', 1)

    desenhar_item("PLACA DO VEÍCULO", dados['placa'])
    desenhar_item("NOME DO MOTORISTA", dados['motorista'])
    desenhar_item("Nº NOTA FISCAL", dados['num_nota'])
    desenhar_item("NÚMERO DO LACRE", dados['lacre'])
    desenhar_item("TRANSPORTADORA", dados['transportadora'])
    desenhar_item("PRODUTO CARREGADO", dados['produto'])
    desenhar_item("VOLUME INFORMADO (20º)", dados['vol20'])
    desenhar_item("SAÍDA DA ORIGEM", dados['saida_origem'])
    desenhar_item("REGISTRO POSTO", dados['chegada_posto'])
    desenhar_item("TEMPO TOTAL TRÂNSITO", f"{dados['t1_transito']} Horas")
    
    pdf.ln(12)
    
    # Texto de instrução reposicionado para não trombar com o código
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(10, 38, 71)
    pdf.cell(180, 5, "APRESENTE O QR-CODE ABAIXO NO PORTÃO DA ETC", 0, 1, 'C')
    pdf.ln(4)

    # Geração do QR Code limpo
    qr_conteudo = f"ID:{seq_gerado}|PLC:{dados['placa']}|NF:{dados['num_nota']}"
    qr = qrcode.make(qr_conteudo)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)
    
    # Define a posição vertical fixa e segura para o QR Code no rodapé
    pdf.image(qr_buffer, x=80, y=145, w=50)
    
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)

    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name=f"Ticket_{seq_gerado}.pdf")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
