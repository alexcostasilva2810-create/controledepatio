import os
import time
import requests
from flask import Flask, render_template_string, request, send_file
import qrcode
import io
from fpdf import FPDF

app = Flask(__name__)

# Link do seu Google Apps Script já configurado no lugar correto!
URL_PLANILHA_GOOGLE = "https://script.google.com/macros/s/AKfycbxlzebvfA0GQcAyQ1Oc9IFC6XX9t4mR7cOLzj4jt8sX0B2YZoozCuTzlAnZHeL8aHjr/exec"

# ==========================================
# # DESIGN DA INTERFACE INTERATIVA COMPLETA #
# ==========================================
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Controle de Pátio e Logística</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background-color: #f4f7f6; color: #333; }
        .navbar { background-color: #113f67; padding: 18px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .navbar h1 { color: white; margin: 0; font-size: 22px; text-transform: uppercase; letter-spacing: 1px; }
        .container { max-width: 1200px; margin: 25px auto; padding: 0 20px; }
        
        .tabs { display: flex; margin-bottom: 20px; border-bottom: 3px solid #113f67; }
        .tab-button { background: none; border: none; padding: 14px 28px; font-size: 15px; font-weight: bold; color: #666; cursor: pointer; transition: 0.3s; }
        .tab-button.active { color: #113f67; border-bottom: 4px solid #007bff; background-color: #e8f0fe; border-radius: 6px 6px 0 0; }
        .tab-content { display: none; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .tab-content.active { display: block; }

        /* Formulário em Grid de Duas Colunas */
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        @media(max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
        
        .form-group { display: flex; flex-direction: column; }
        label { margin-top: 5px; font-weight: bold; color: #444; font-size: 14px; }
        input, select { padding: 10px; margin-top: 6px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; font-size: 14px; background-color: #fafafa; }
        input:focus, select:focus { border-color: #007bff; background-color: #fff; outline: none; }
        
        .btn-submit { grid-column: 1 / -1; margin-top: 20px; padding: 14px; background-color: #28a745; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; text-transform: uppercase; }
        .btn-submit:hover { background-color: #218838; }

        /* Tabela Estilo Planilha */
        .table-responsive { overflow-x: auto; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; min-width: 1000px; }
        th { background-color: #113f67; color: white; padding: 10px; font-weight: 600; text-transform: uppercase; }
        td { padding: 10px; border-bottom: 1px solid #dee2e6; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f1f5f9; }
        .no-data { text-align: center; color: #888; padding: 40px; font-style: italic; font-size: 15px; }
    </style>
</head>
<body>

    <div class="navbar">
        <h1>Módulo Integrado de Portaria & Agendamentos</h1>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('cadastro')">📝 Formulário de Entrada</button>
            <button class="tab-button" onclick="switchTab('painel')">📊 Painel Histórico Geral</button>
        </div>

        <div id="cadastro" class="tab-content active">
            <h2 style="color: #113f67; margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px;">Preenchimento de Dados do Veículo</h2>
            <form action="/agendar" method="POST" class="form-grid">
                
                <div class="form-group">
                    <label for="placa">Placa do Veículo:</label>
                    <input type="text" id="placa" name="placa" required placeholder="Ex: EUK9C95">
                </div>

                <div class="form-group">
                    <label for="lacre">Número do Lacre:</label>
                    <input type="text" id="lacre" name="lacre" required placeholder="Ex: 562374">
                </div>

                <div class="form-group" style="grid-column: span 2;">
                    <label for="motorista">Nome Completo do Motorista:</label>
                    <input type="text" id="motorista" name="motorista" required placeholder="Ex: ALVORO LIMA RIBEIRO">
                </div>

                <div class="form-group">
                    <label for="transportadora">Transportadora / Agrolog:</label>
                    <input type="text" id="transportadora" name="transportadora" required placeholder="Ex: AGROLOG">
                </div>

                <div class="form-group">
                    <label for="cliente">Cliente Destinatário:</label>
                    <input type="text" id="cliente" name="cliente" required placeholder="Ex: ABBA MANAUS">
                </div>

                <div class="form-group">
                    <label for="destino">Cidade / Estado de Destino:</label>
                    <input type="text" id="destino" name="destino" required placeholder="Ex: MANAUS">
                </div>

                <div class="form-group">
                    <label for="telefone">Telefone do Motorista (Contato):</label>
                    <input type="text" id="telefone" name="telefone" required placeholder="Ex: (66) 99600-1234">
                </div>

                <div class="form-group">
                    <label for="produto">Produto / Combustível:</label>
                    <input type="text" id="produto" name="produto" required placeholder="Ex: ANIDRO / DIESEL">
                </div>

                <div class="form-group">
                    <label for="vol20">Volume a 20º:</label>
                    <input type="text" id="vol20" name="vol20" required placeholder="Ex: 61.534">
                </div>

                <button type="submit" class="btn-submit">Registrar Entrada & Emitir QR Code</button>
            </form>
        </div>

        <div id="painel" class="tab-content">
            <h2 style="color: #113f67; margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px;">Controle Geral de Carretas Cadastradas</h2>
            <p style="color: #555;">Visualização síncrona com a sua Planilha Google (do primeiro ao último agendamento):</p>
            
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Seq</th>
                            <th>Placa</th>
                            <th>Lacre</th>
                            <th>Nome Motorista</th>
                            <th>Transportadora</th>
                            <th>Cliente</th>
                            <th>Cidade Destino</th>
                            <th>Telefone Contato</th>
                            <th>Produto</th>
                            <th>Vol a 20º</th>
                            <th>Chegada ETC</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for reg in registros %}
                        <tr>
                            <td style="font-weight: bold; color: #007bff;">{{ reg.sequencial }}</td>
                            <td style="font-weight: 600;">{{ reg.placa }}</td>
                            <td>{{ reg.lacre }}</td>
                            <td>{{ reg.motorista }}</td>
                            <td>{{ reg.transportadora }}</td>
                            <td>{{ reg.cliente }}</td>
                            <td>{{ reg.destino }}</td>
                            <td>{{ reg.telefone }}</td>
                            <td>{{ reg.produto }}</td>
                            <td>{{ reg.vol20 }}</td>
                            <td style="color: #666;">{{ reg.chegada_etc }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="11" class="no-data">Nenhum registro localizado ou carregando dados da planilha...</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(button => button.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    registros = []
    try:
        resposta = requests.get(URL_PLANILHA_GOOGLE, timeout=12)
        if resposta.status_code == 200:
            registros = resposta.json()
            registros.reverse() # Traz os mais recentes para o topo do painel do site
    except Exception as e:
        print(f"Erro de conexão com Google Sheets: {e}")
        
    return render_template_string(HTML_SISTEMA, registros=registros)


@app.route('/agendar', methods=['POST'])
def agendar():
    placa = request.form.get('placa').upper().strip()
    lacre = request.form.get('lacre').strip()
    motorista = request.form.get('motorista').upper().strip()
    transportadora = request.form.get('transportadora').upper().strip()
    cliente = request.form.get('cliente').upper().strip()
    destino = request.form.get('destino').upper().strip()
    telefone = request.form.get('telefone').strip()
    produto = request.form.get('produto').upper().strip()
    vol20 = request.form.get('vol20').strip()
    
    data_hora = time.strftime('%d/%m/%Y %H:%M')

    dados_envio = {
        "placa": placa,
        "lacre": lacre,
        "motorista": motorista,
        "transportadora": transportadora,
        "cliente": cliente,
        "destino": destino,
        "telefone": telefone,
        "produto": produto,
        "vol20": vol20,
        "chegada_etc": data_hora
    }

    # 1. SALVA NA PLANILHA GOOGLE E RETORNA O SEQUENCIAL GERADO
    num_sequencial = "AG"
    try:
        resposta = requests.post(URL_PLANILHA_GOOGLE, json=dados_envio, timeout=12)
        if resposta.status_code == 200:
            num_sequencial = resposta.json().get("sequencial", "AG")
    except Exception as e:
        print(f"Erro ao salvar na Planilha Google: {e}")

    # 2. CRIA O QR CODE COM OS DADOS OPERACIONAIS
    conteudo_qr = f"SEQ:{num_sequencial}|PLC:{placa}|MOT:{motorista}|PROD:{produto}|LAC:{lacre}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(conteudo_qr)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # 3. CONSTRÓI O COMPROVANTE EM PDF PARA O MOTORISTA
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(190, 10, text="TICKET DE CADASTRO - CONTROLE DE PÁTIO", ln=True, align='C')
    pdf.ln(8)
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(190, 8, text=f"SEQUENCIAL AUTOMÁTICO: {num_sequencial}", ln=True)
    pdf.cell(190, 8, text=f"REGISTRO ENTRADA (ETC): {data_hora}", ln=True)
    pdf.cell(190, 8, text=f"PLACA DO VEÍCULO: {placa}", ln=True)
    pdf.cell(190, 8, text=f"NÚMERO DO LACRE: {lacre}", ln=True)
    pdf.cell(190, 8, text=f"MOTORISTA: {motorista}", ln=True)
    pdf.cell(190, 8, text=f"TRANSPORTADORA: {transportadora}", ln=True)
    pdf.cell(190, 8, text=f"CLIENTE: {cliente}", ln=True)
    pdf.cell(190, 8, text=f"DESTINO: {destino}", ln=True)
    pdf.cell(190, 8, text=f"CONTATO: {telefone}", ln=True)
    pdf.cell(190, 8, text=f"PRODUTO: {produto}", ln=True)
    pdf.cell(190, 8, text=f"VOLUME A 20º: {vol20}", ln=True)
    pdf.ln(12)
    
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(190, 6, text="APRESENTE ESTE QR CODE NA ENTRADA DO PÁTIO", ln=True, align='C')
    
    pdf.image(img_buffer, x=65, y=115, w=80) 
    
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=f"ticket_patio_{num_sequencial}.pdf"
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
