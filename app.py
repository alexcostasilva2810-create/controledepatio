import os
import time
from flask import Flask, render_template_string, request, send_file
import qrcode
import io
from fpdf import FPDF

# ==========================================
# # CONFIGURAÇÃO #
# ==========================================

app = Flask(__name__)

HTML_FORMULARIO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Agendamento de Carretas - Combustível</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f7f6; }
        .container { max-width: 500px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); margin: 0 auto; }
        h2 { color: #1a3a5f; text-align: center; margin-bottom: 20px; }
        label { display: block; margin-top: 12px; font-weight: bold; color: #444; }
        input, select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        button { margin-top: 25px; width: 100%; padding: 12px; background-color: #0056b3; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #004085; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Controle de Agendamento</h2>
        <form action="/agendar" method="POST">
            <label for="motorista">Nome do Motorista:</label>
            <input type="text" id="motorista" name="motorista" required placeholder="Ex: ALVORO LIMA RIBEIRO">

            <label for="lacre">Número do Lacre:</label>
            <input type="text" id="lacre" name="lacre" required placeholder="Ex: 15">

            <label for="placa">Placa da Carreta:</label>
            <input type="text" id="placa" name="placa" required placeholder="ABC1D23">

            <label for="combustivel">Tipo de Combustível:</label>
            <select id="combustivel" name="combustivel">
                <option value="Diesel S10">Diesel S10</option>
                <option value="Diesel S500">Diesel S500</option>
                <option value="Gasolina Comum">Gasolina Comum</option>
                <option value="Etanol">Etanol</option>
            </select>

            <button type="submit">Gerar QR Code de Agendamento</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_FORMULARIO)


# ==========================================
# # CADASTRO DE MOTORISTA #
# ==========================================

@app.route('/agendar', methods=['POST'])
def agendar():
    motorista = request.form.get('motorista').upper().strip()
    lacre = request.form.get('lacre').strip()
    placa = request.form.get('placa').upper().strip()
    combustivel = request.form.get('combustivel')
    
    id_agendamento = f"AG-{int(time.time())}"
    dados_qr = f"ID:{id_agendamento}|MOT:{motorista}|LAC:{lacre}|PLC:{placa}|PROD:{combustivel}"

    # Criação do QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10, 
        border=4
    )
    qr.add_data(dados_qr)
    qr.make(fit=True)
    
    # Salva o QR Code na memória temporária
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Cria o documento PDF usando fpdf2
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(190, 10, text="COMPROVANTE DE AGENDAMENTO", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(190, 8, text=f"ID Agendamento: {id_agendamento}", ln=True)
    pdf.cell(190, 8, text=f"Motorista: {motorista}", ln=True)
    pdf.cell(190, 8, text=f"Lacre: {lacre}", ln=True)
    pdf.cell(190, 8, text=f"Placa: {placa}", ln=True)
    pdf.cell(190, 8, text=f"Combustivel: {combustivel}", ln=True)
    pdf.ln(15)
    
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(190, 8, text="APRESENTE O QR CODE ABAIXO NA TELA DO SEU CELULAR AO CHEGAR", ln=True, align='C')
    
    # Insere a imagem direto do buffer da memória
    pdf.image(img_buffer, x=65, y=90, w=80) 
    
    # Envia o PDF gerado diretamente para o download do cliente
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=f"agendamento_{id_agendamento}.pdf"
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
