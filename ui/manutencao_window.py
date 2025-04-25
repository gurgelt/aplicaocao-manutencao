#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementação da tela de manutenção para o Sistema de Manutenção.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QLineEdit, QComboBox, QPushButton, 
                           QTextEdit, QGroupBox, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from utils.helpers import colorir_tabela_por_status

class TelaManutencao(QWidget):
    """Classe para a tela de manutenção e diagnóstico."""
    
    def __init__(self, db, usuario_id):
        """Inicializa a tela de manutenção."""
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.solicitacao_atual = None
        self.init_ui()
        self.atualizar_tabela()
    
    def init_ui(self):
        """Configura a interface de usuário."""
        # Layout principal com divisor
        layout = QVBoxLayout(self)
        
        # Splitter para dividir formulário e tabela
        splitter = QSplitter(Qt.Vertical)
        
        # Grupo de formulário
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Título
        title_label = QLabel("Diagnóstico e Atualização")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        form_layout.addWidget(title_label)
        
        # Formulário de diagnóstico
        form_layout_h = QHBoxLayout()
        
        # Coluna esquerda - Dados básicos
        dados_group = QGroupBox("Dados da Solicitação")
        dados_layout = QFormLayout()
        
        self.id_label = QLabel("Não selecionado")
        self.os_label = QLabel("Não selecionado")
        self.codigo_motor_input = QLineEdit()
        self.nome_empresa_input = QLineEdit()
        self.nome_cliente_input = QLineEdit()
        self.modelo_motor_input = QLineEdit()
        
        dados_layout.addRow("ID da Solicitação:", self.id_label)
        dados_layout.addRow("Ordem de Serviço:", self.os_label)
        dados_layout.addRow("Código do Motor:", self.codigo_motor_input)
        dados_layout.addRow("Nome da Empresa:", self.nome_empresa_input)
        dados_layout.addRow("Nome do Cliente:", self.nome_cliente_input)
        dados_layout.addRow("Modelo do Motor:", self.modelo_motor_input)
        
        dados_group.setLayout(dados_layout)
        form_layout_h.addWidget(dados_group)
        
        # Coluna direita - Status e diagnostico
        status_group = QGroupBox("Status e Diagnóstico")
        status_layout = QFormLayout()
        
        self.defeitos_input = QTextEdit()
        self.defeitos_input.setPlaceholderText("Máximo 500 caracteres")
        self.defeitos_input.setMaximumHeight(100)
        
        self.prioridade_combo = QComboBox()
        self.prioridade_combo.addItems(["Baixa", "Normal", "Alta", "Urgente"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Pendente", "Em análise", "Orçamento aprovado", 
            "Em manutenção", "Concluído", "Cancelado"
        ])
        
        self.diagnostico_input = QTextEdit()
        self.diagnostico_input.setPlaceholderText("Máximo 1000 caracteres")
        
        status_layout.addRow("Defeitos:", self.defeitos_input)
        status_layout.addRow("Prioridade:", self.prioridade_combo)
        status_layout.addRow("Status:", self.status_combo)
        status_layout.addRow("Diagnóstico:", self.diagnostico_input)
        
        status_group.setLayout(status_layout)
        form_layout_h.addWidget(status_group)
        
        form_layout.addLayout(form_layout_h)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.atualizar_btn = QPushButton("Atualizar")
        self.atualizar_btn.clicked.connect(self.atualizar_solicitacao)
        self.atualizar_btn.setEnabled(False)
        
        self.limpar_btn = QPushButton("Novo")
        self.limpar_btn.clicked.connect(self.limpar_formulario)
        
        self.excluir_btn = QPushButton("Excluir")
        self.excluir_btn.clicked.connect(self.excluir_solicitacao)
        self.excluir_btn.setEnabled(False)
        
        btn_layout.addWidget(self.atualizar_btn)
        btn_layout.addWidget(self.limpar_btn)
        btn_layout.addWidget(self.excluir_btn)
        
        form_layout.addLayout(btn_layout)
        
        # Tabela de solicitações
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        table_label = QLabel("Solicitações Cadastradas")
        table_label.setAlignment(Qt.AlignCenter)
        table_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "OS", "Empresa", "Responsável", "Modelo", "Status", "Prioridade", "Data"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.doubleClicked.connect(self.carregar_solicitacao)
        
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.tabela)
        
        # Adicionar widgets ao splitter
        splitter.addWidget(form_widget)
        splitter.addWidget(table_widget)
        
        # Ajustar proporção do splitter
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        
        # Conectar eventos
        self.status_combo.currentTextChanged.connect(self.verificar_status)
    
    def verificar_status(self):
        """Alerta sobre o diagnóstico obrigatório quando o status for Concluído."""
        # Se o status for "Concluído", alertar sobre o diagnóstico obrigatório
        if self.status_combo.currentText() == "Concluído":
            self.diagnostico_input.setStyleSheet("background-color: #FFEEEE;")
            self.diagnostico_input.setPlaceholderText("OBRIGATÓRIO para status Concluído - Máximo 1000 caracteres")
        else:
            self.diagnostico_input.setStyleSheet("")
            self.diagnostico_input.setPlaceholderText("Máximo 1000 caracteres")
    
    def atualizar_tabela(self):
        """Atualiza a tabela de solicitações com dados do banco."""
        self.tabela.setRowCount(0)
        solicitacoes = self.db.obter_solicitacoes()
        
        for row_idx, sol in enumerate(solicitacoes):
            id_sol, os, nome_resp, nome_empresa, telefone, email, local, historico, \
            descricao, marca, modelo, condicao, data, codigo, prioridade, status, diagnostico = sol
            
            self.tabela.insertRow(row_idx)
            self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(id_sol)))
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(os))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(nome_empresa))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(nome_resp))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem(modelo))
            self.tabela.setItem(row_idx, 5, QTableWidgetItem(status))
            self.tabela.setItem(row_idx, 6, QTableWidgetItem(prioridade))
            self.tabela.setItem(row_idx, 7, QTableWidgetItem(data))
            
            # Colore cada linha conforme status e prioridade
            colorir_tabela_por_status(self.tabela, row_idx, status, prioridade)
        
        # Ajustar altura das linhas
        self.tabela.resizeRowsToContents()
    
    def atualizar_tabela_com_busca(self, termo):
        """Atualiza a tabela com resultados da busca."""
        self.tabela.setRowCount(0)
        solicitacoes = self.db.buscar_solicitacoes(termo)
        
        for row_idx, sol in enumerate(solicitacoes):
            id_sol, os, nome_resp, nome_empresa, telefone, email, local, historico, \
            descricao, marca, modelo, condicao, data, codigo, prioridade, status, diagnostico = sol
            
            self.tabela.insertRow(row_idx)
            self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(id_sol)))
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(os))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(nome_empresa))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(nome_resp))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem(modelo))
            self.tabela.setItem(row_idx, 5, QTableWidgetItem(status))
            self.tabela.setItem(row_idx, 6, QTableWidgetItem(prioridade))
            self.tabela.setItem(row_idx, 7, QTableWidgetItem(data))
            
            # Colore cada linha conforme status e prioridade
            colorir_tabela_por_status(self.tabela, row_idx, status, prioridade)
        
        # Ajustar altura das linhas
        self.tabela.resizeRowsToContents()
    
    def carregar_solicitacao(self, item):
        """Carrega os dados de uma solicitação no formulário."""
        row = item.row()
        id_solicitacao = int(self.tabela.item(row, 0).text())
        
        # Obter dados completos da solicitação
        solicitacao = self.db.obter_solicitacao_por_id(id_solicitacao)
        
        if solicitacao:
            id_sol, os, nome_resp, nome_empresa, telefone, email, local, historico, \
            descricao, marca, modelo, condicao, data, codigo, prioridade, status, diagnostico = solicitacao
            
            # Preencher formulário
            self.id_label.setText(str(id_sol))
            self.os_label.setText(os)
            self.codigo_motor_input.setText(codigo if codigo else "")
            self.nome_empresa_input.setText(nome_empresa)
            self.nome_cliente_input.setText(nome_resp)
            self.modelo_motor_input.setText(modelo)
            self.defeitos_input.setText(descricao)
            
            self.prioridade_combo.setCurrentText(prioridade)
            self.status_combo.setCurrentText(status)
            self.diagnostico_input.setText(diagnostico if diagnostico else "")
            
            # Atualizar estado
            self.solicitacao_atual = id_sol
            self.atualizar_btn.setEnabled(True)
            self.excluir_btn.setEnabled(True)
            
            # Verificar status para alerta no diagnóstico
            self.verificar_status()
    
    def validar_formulario(self):
        """Valida os dados do formulário antes de prosseguir."""
        # Verificar campos obrigatórios
        if not self.codigo_motor_input.text() or \
           not self.nome_empresa_input.text() or \
           not self.nome_cliente_input.text() or \
           not self.modelo_motor_input.text() or \
           not self.defeitos_input.toPlainText():
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios")
            return False
        
        # Validar tamanho dos campos
        if len(self.defeitos_input.toPlainText()) > 500:
            QMessageBox.warning(self, "Erro", "O campo de defeitos não pode ter mais de 500 caracteres")
            return False
        
        if len(self.diagnostico_input.toPlainText()) > 1000:
            QMessageBox.warning(self, "Erro", "O diagnóstico não pode ter mais de 1000 caracteres")
            return False
        
        # Validar diagnóstico obrigatório se status for Concluído
        if self.status_combo.currentText() == "Concluído" and not self.diagnostico_input.toPlainText():
            QMessageBox.warning(
                self, "Erro", 
                "É necessário incluir um diagnóstico quando o status for 'Concluído'"
            )
            return False
        
        return True
    
    def atualizar_solicitacao(self):
        """Atualiza uma solicitação existente."""
        if not self.solicitacao_atual:
            return
        
        if not self.validar_formulario():
            return
        
        dados = {
            'nome_responsavel': self.nome_cliente_input.text(),
            'nome_empresa': self.nome_empresa_input.text(),
            'modelo_motor': self.modelo_motor_input.text(),
            'descricao_problema': self.defeitos_input.toPlainText(),
            'codigo_motor': self.codigo_motor_input.text(),
            'prioridade': self.prioridade_combo.currentText(),
            'status': self.status_combo.currentText(),
            'diagnostico': self.diagnostico_input.toPlainText(),
            # Dados herdados da recepção que são necessários na atualização
            'telefone': '',  # Será preenchido com dados existentes
            'email': '',  # Será preenchido com dados existentes
            'local_recebimento': '',  # Será preenchido com dados existentes
            'historico_cliente': '',  # Será preenchido com dados existentes
            'marca_motor': '',  # Será preenchido com dados existentes
            'condicao_peca': ''  # Será preenchido com dados existentes
        }
        
        # Buscar dados complementares da solicitação
        solicitacao = self.db.obter_solicitacao_por_id(self.solicitacao_atual)
        
        if solicitacao:
            _, _, _, _, telefone, email, local, historico, _, marca, _, condicao, _, _, _, _, _ = solicitacao
            
            dados['telefone'] = telefone
            dados['email'] = email
            dados['local_recebimento'] = local
            dados['historico_cliente'] = historico
            dados['marca_motor'] = marca
            dados['condicao_peca'] = condicao
        
        sucesso, mensagem = self.db.atualizar_solicitacao(self.solicitacao_atual, dados, self.usuario_id)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.atualizar_tabela()
        else:
            QMessageBox.warning(self, "Erro", mensagem)
    
    def excluir_solicitacao(self):
        """Exclui uma solicitação após confirmação."""
        if not self.solicitacao_atual:
            return
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self, "Confirmar Exclusão", 
            "Tem certeza que deseja excluir esta solicitação? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            sucesso, mensagem = self.db.excluir_solicitacao(self.solicitacao_atual, self.usuario_id)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.limpar_formulario()
                self.atualizar_tabela()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def limpar_formulario(self):
        """Limpa os campos do formulário e reseta o estado dos botões."""
        # Limpar campos
        self.id_label.setText("Não selecionado")
        self.os_label.setText("Não selecionado")
        self.codigo_motor_input.clear()
        self.nome_empresa_input.clear()
        self.nome_cliente_input.clear()
        self.modelo_motor_input.clear()
        self.defeitos_input.clear()
        self.prioridade_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.diagnostico_input.clear()
        
        # Resetar estado
        self.solicitacao_atual = None
        self.atualizar_btn.setEnabled(False)
        self.excluir_btn.setEnabled(False)