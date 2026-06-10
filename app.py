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
    "SD XVIII": {"capacidade": "795.6 m³", "cts_meta": 13},
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
                                    <button type="submit" class="btn btn-success btn-lg fw
