#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementação da tela de recepção para o Sistema de Manutenção.
"""

import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QLineEdit, QComboBox, QPushButton, 
                           QTextEdit, QGroupBox, QFileDialog, QTableWidget, 
                           QTableWidgetItem, QHeaderView, QMessageBox, 
                           QScrollArea, QGridLayout, QSplitter, QDialog, 
                           QFrame, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from utils.helpers import validar_email

class TelaRecepcao(QWidget):
    """Classe para a tela de recepção e cadastro de solicitações."""
    
    def __init__(self, db, usuario_id):
        """Inicializa a tela de recepção."""
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.solicitacao_atual = None
        self.imagens = []  # Lista para armazenar QPixmap das imagens
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
        title_label = QLabel("Cadastro de Solicitações")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        form_layout.addWidget(title_label)
        
        # Formulário de cliente
        cliente_group = QGroupBox("Dados do Cliente")
        cliente_layout = QFormLayout()
        
        self.os_label = QLabel("Será gerado automaticamente")
        self.os_label.setStyleSheet("color: gray; font-style: italic;")
        
        self.nome_responsavel_input = QLineEdit()
        self.nome_empresa_input = QLineEdit()
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        self.local_recebimento = QComboBox()
        self.local_recebimento.addItems(["Recepção João Mafra", "Coleta no Cliente"])
        
        self.historico_cliente = QComboBox()
        self.historico_cliente.addItems(["Novo", "Recorrente", "Inativo"])
        
        cliente_layout.addRow("Ordem de Serviço:", self.os_label)
        cliente_layout.addRow("Nome do Responsável:", self.nome_responsavel_input)
        cliente_layout.addRow("Nome da Empresa:", self.nome_empresa_input)
        cliente_layout.addRow("Telefone:", self.telefone_input)
        cliente_layout.addRow("E-mail:", self.email_input)
        cliente_layout.addRow("Local de Recebimento:", self.local_recebimento)
        cliente_layout.addRow("Histórico do Cliente:", self.historico_cliente)
        
        cliente_group.setLayout(cliente_layout)
        form_layout.addWidget(cliente_group)
        
        # Formulário de produto
        produto_group = QGroupBox("Dados do Produto")
        produto_layout = QFormLayout()
        
        self.descricao_problema_input = QTextEdit()
        self.descricao_problema_input.setPlaceholderText("Máximo 500 caracteres")
        self.descricao_problema_input.setMaximumHeight(100)
        
        self.marca_motor_input = QLineEdit()
        self.modelo_motor_input = QLineEdit()
        
        self.condicao_peca = QComboBox()
        self.condicao_peca.addItems(["Ótimo", "Normal", "Péssimo"])
        
        produto_layout.addRow("Descrição do Problema:", self.descricao_problema_input)
        produto_layout.addRow("Marca do Motor:", self.marca_motor_input)
        produto_layout.addRow("Modelo do Motor:", self.modelo_motor_input)
        produto_layout.addRow("Condição da Peça:", self.condicao_peca)
        
        produto_group.setLayout(produto_layout)
        form_layout.addWidget(produto_group)
        
        # Área de imagens
        imagem_group = QGroupBox("Galeria de Imagens (máximo 10)")
        imagem_layout = QVBoxLayout()
        
        # Botões de gerenciamento de imagens
        img_btn_layout = QHBoxLayout()
        
        self.adicionar_img_btn = QPushButton("Adicionar Imagem")
        self.adicionar_img_btn.clicked.connect(self.adicionar_imagem)
        self.adicionar_img_btn.setEnabled(False)  # Desabilitado até salvar a solicitação
        
        self.remover_img_btn = QPushButton("Remover Imagem")
        self.remover_img_btn.clicked.connect(self.remover_imagem)
        self.remover_img_btn.setEnabled(False)
        
        img_btn_layout.addWidget(self.adicionar_img_btn)
        img_btn_layout.addWidget(self.remover_img_btn)
        
        imagem_layout.addLayout(img_btn_layout)
        
        # Grid para exibir as miniaturas
        self.imagem_grid = QGridLayout()
        
        # Scroll para as imagens
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.imagem_grid)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        imagem_layout.addWidget(scroll_area)
        imagem_group.setLayout(imagem_layout)
        form_layout.addWidget(imagem_group)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.cadastrar_btn = QPushButton("Cadastrar")
        self.cadastrar_btn.clicked.connect(self.cadastrar_solicitacao)
        
        self.atualizar_btn = QPushButton("Atualizar")
        self.atualizar_btn.clicked.connect(self.atualizar_solicitacao)
        self.atualizar_btn.setEnabled(False)
        
        self.limpar_btn = QPushButton("Novo")
        self.limpar_btn.clicked.connect(self.limpar_formulario)
        
        btn_layout.addWidget(self.cadastrar_btn)
        btn_layout.addWidget(self.atualizar_btn)
        btn_layout.addWidget(self.limpar_btn)
        
        form_layout.addLayout(btn_layout)
        
        # Tabela de solicitações
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        table_label = QLabel("Solicitações Cadastradas")
        table_label.setAlignment(Qt.AlignCenter)
        table_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "OS", "Empresa", "Responsável", "Modelo", "Condição", "Data"
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
            self.tabela.setItem(row_idx, 5, QTableWidgetItem(condicao))
            self.tabela.setItem(row_idx, 6, QTableWidgetItem(data))
        
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
            self.tabela.setItem(row_idx, 5, QTableWidgetItem(condicao))
            self.tabela.setItem(row_idx, 6, QTableWidgetItem(data))
        
        # Ajustar altura das linhas
        self.tabela.resizeRowsToContents()
    
    def validar_formulario(self):
        """Valida os dados do formulário antes de prosseguir."""
        # Verificar campos obrigatórios
        if not self.nome_responsavel_input.text() or \
           not self.nome_empresa_input.text() or \
           not self.telefone_input.text() or \
           not self.email_input.text() or \
           not self.descricao_problema_input.toPlainText() or \
           not self.marca_motor_input.text() or \
           not self.modelo_motor_input.text():
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios")
            return False
        
        # Validar tamanho da descrição
        if len(self.descricao_problema_input.toPlainText()) > 500:
            QMessageBox.warning(self, "Erro", "A descrição do problema não pode ter mais de 500 caracteres")
            return False
        
        # Validar formato de e-mail
        email = self.email_input.text()
        if not validar_email(email):
            QMessageBox.warning(self, "Erro", "Formato de e-mail inválido")
            return False
        
        return True
    
    def cadastrar_solicitacao(self):
        """Cadastra uma nova solicitação no sistema."""
        if not self.validar_formulario():
            return
        
        dados = {
            'nome_responsavel': self.nome_responsavel_input.text(),
            'nome_empresa': self.nome_empresa_input.text(),
            'telefone': self.telefone_input.text(),
            'email': self.email_input.text(),
            'local_recebimento': self.local_recebimento.currentText(),
            'historico_cliente': self.historico_cliente.currentText(),
            'descricao_problema': self.descricao_problema_input.toPlainText(),
            'marca_motor': self.marca_motor_input.text(),
            'modelo_motor': self.modelo_motor_input.text(),
            'condicao_peca': self.condicao_peca.currentText()
        }
        
        sucesso, solicitacao_id, ordem_servico = self.db.adicionar_solicitacao(dados, self.usuario_id)
        
        if sucesso:
            QMessageBox.information(
                self, "Sucesso", 
                f"Solicitação cadastrada com sucesso!\nOrdem de Serviço: {ordem_servico}"
            )
            self.solicitacao_atual = solicitacao_id
            self.os_label.setText(ordem_servico)
            self.os_label.setStyleSheet("color: black; font-weight: bold;")
            
            # Atualizar botões
            self.cadastrar_btn.setEnabled(False)
            self.atualizar_btn.setEnabled(True)
            self.adicionar_img_btn.setEnabled(True)
            
            # Atualizar tabela
            self.atualizar_tabela()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao cadastrar solicitação")
    
    def atualizar_solicitacao(self):
        """Atualiza uma solicitação existente."""
        if not self.solicitacao_atual:
            return
        
        if not self.validar_formulario():
            return
        
        dados = {
            'nome_responsavel': self.nome_responsavel_input.text(),
            'nome_empresa': self.nome_empresa_input.text(),
            'telefone': self.telefone_input.text(),
            'email': self.email_input.text(),
            'local_recebimento': self.local_recebimento.currentText(),
            'historico_cliente': self.historico_cliente.currentText(),
            'descricao_problema': self.descricao_problema_input.toPlainText(),
            'marca_motor': self.marca_motor_input.text(),
            'modelo_motor': self.modelo_motor_input.text(),
            'condicao_peca': self.condicao_peca.currentText()
        }
        
        sucesso, mensagem = self.db.atualizar_solicitacao(self.solicitacao_atual, dados, self.usuario_id)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.atualizar_tabela()
        else:
            QMessageBox.warning(self, "Erro", mensagem)
    
    def limpar_formulario(self):
        """Limpa os campos do formulário e reseta o estado dos botões."""
        self.nome_responsavel_input.clear()
        self.nome_empresa_input.clear()
        self.telefone_input.clear()
        self.email_input.clear()
        self.local_recebimento.setCurrentIndex(0)
        self.historico_cliente.setCurrentIndex(0)
        self.descricao_problema_input.clear()
        self.marca_motor_input.clear()
        self.modelo_motor_input.clear()
        self.condicao_peca.setCurrentIndex(0)
        
        self.os_label.setText("Será gerado automaticamente")
        self.os_label.setStyleSheet("color: gray; font-style: italic;")
        
        # Limpar imagens
        self.limpar_grid_imagens()
        
        # Resetar estado
        self.solicitacao_atual = None
        self.cadastrar_btn.setEnabled(True)
        self.atualizar_btn.setEnabled(False)
        self.adicionar_img_btn.setEnabled(False)
        self.remover_img_btn.setEnabled(False)
    
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
            self.nome_responsavel_input.setText(nome_resp)
            self.nome_empresa_input.setText(nome_empresa)
            self.telefone_input.setText(telefone)
            self.email_input.setText(email)
            self.local_recebimento.setCurrentText(local)
            self.historico_cliente.setCurrentText(historico)
            self.descricao_problema_input.setText(descricao)
            self.marca_motor_input.setText(marca)
            self.modelo_motor_input.setText(modelo)
            self.condicao_peca.setCurrentText(condicao)
            
            self.os_label.setText(os)
            self.os_label.setStyleSheet("color: black; font-weight: bold;")
            
            # Atualizar estado
            self.solicitacao_atual = id_sol
            self.cadastrar_btn.setEnabled(False)
            self.atualizar_btn.setEnabled(True)
            self.adicionar_img_btn.setEnabled(True)
            
            # Carregar imagens
            self.carregar_imagens()
    
    def adicionar_imagem(self):
        """Adiciona uma nova imagem à solicitação atual."""
        if not self.solicitacao_atual:
            QMessageBox.warning(self, "Erro", "Salve a solicitação antes de adicionar imagens")
            return
        
        # Verificar quantidade de imagens
        imagens = self.db.obter_imagens(self.solicitacao_atual)
        if len(imagens) >= 10:
            QMessageBox.warning(self, "Erro", "Limite de 10 imagens atingido")
            return
        
        # Abrir diálogo para seleção de arquivo
        caminho_imagem, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Imagem", "", "Imagens (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if not caminho_imagem:
            return
        
        try:
            # Ler arquivo de imagem
            with open(caminho_imagem, 'rb') as f:
                imagem_bytes = f.read()
            
            # Salvar no banco
            sucesso, mensagem = self.db.salvar_imagem(self.solicitacao_atual, imagem_bytes)
            
            if sucesso:
                self.carregar_imagens()
                QMessageBox.information(self, "Sucesso", mensagem)
            else:
                QMessageBox.warning(self, "Erro", mensagem)
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao processar imagem: {e}")
    
    def carregar_imagens(self):
        """Carrega as imagens da solicitação atual na grid."""
        if not self.solicitacao_atual:
            return
        
        # Limpar grid
        self.limpar_grid_imagens()
        
        # Obter imagens do banco
        imagens = self.db.obter_imagens(self.solicitacao_atual)
        
        # Criar miniaturas
        for idx, (imagem_id, imagem_bytes) in enumerate(imagens):
            # Converter de bytes para QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(imagem_bytes)
            
            # Criar miniatura
            miniatura = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Criar label para exibir a miniatura
            label = QLabel()
            label.setPixmap(miniatura)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(120, 120)
            label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label.setLineWidth(2)
            
            # Tag para armazenar o ID da imagem
            label.setProperty("imagem_id", imagem_id)
            
            # Configurar duplo clique para visualizar
            label.mouseDoubleClickEvent = lambda event, id=imagem_id: self.visualizar_imagem(id)
            
            # Adicionar ao grid
            row = idx // 5
            col = idx % 5
            self.imagem_grid.addWidget(label, row, col)
        
        # Habilitar botão de remover se houver imagens
        self.remover_img_btn.setEnabled(len(imagens) > 0)
    
    def limpar_grid_imagens(self):
        """Remove todos os widgets do grid de imagens."""
        # Remover todos os widgets do grid
        while self.imagem_grid.count():
            item = self.imagem_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def visualizar_imagem(self, imagem_id):
        """Abre uma janela para visualizar uma imagem em tamanho maior."""
        # Buscar imagem no banco
        imagens = self.db.obter_imagens(self.solicitacao_atual)
        
        imagem_bytes = None
        for id_img, bytes_img in imagens:
            if id_img == imagem_id:
                imagem_bytes = bytes_img
                break
        
        if not imagem_bytes:
            return
        
        # Criar uma janela de diálogo para exibir a imagem em tamanho maior
        dialog = QDialog(self)
        dialog.setWindowTitle("Visualizar Imagem")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Converter bytes para QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(imagem_bytes)
        
        # Criar um label para exibir a imagem
        label = QLabel()
        label.setPixmap(pixmap.scaled(
            dialog.width() - 20, dialog.height() - 20, 
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
        
        # Botão para fechar
        fechar_btn = QPushButton("Fechar")
        fechar_btn.clicked.connect(dialog.close)
        layout.addWidget(fechar_btn)
        
        dialog.exec_()
    
    def remover_imagem(self):
        """Remove uma imagem da solicitação atual."""
        if not self.solicitacao_atual:
            return
        
        # Abrir diálogo para escolher qual imagem remover diretamente
        # Não precisa verificar seleção prévia
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Imagem para Remover")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Selecione a imagem para remover:"))
        
        # Lista de imagens
        imagens = self.db.obter_imagens(self.solicitacao_atual)
        
        if not imagens:
            QMessageBox.warning(self, "Aviso", "Não há imagens para remover")
            return
        
        lista = QListWidget()
        
        for idx, (imagem_id, _) in enumerate(imagens):
            item = QListWidgetItem(f"Imagem {idx+1}")
            item.setData(Qt.UserRole, imagem_id)
            lista.addItem(item)
        
        layout.addWidget(lista)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        remover_btn = QPushButton("Remover")
        cancelar_btn = QPushButton("Cancelar")
        
        btn_layout.addWidget(remover_btn)
        btn_layout.addWidget(cancelar_btn)
        
        layout.addLayout(btn_layout)
        
        # Conectar sinais
        remover_btn.clicked.connect(lambda: self.confirmar_remocao(lista) or dialog.accept())
        cancelar_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def confirmar_remocao(self, lista):
        """Confirma e executa a remoção de uma imagem."""
        item_selecionado = lista.currentItem()
        if not item_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione uma imagem para remover")
            return False
        
        imagem_id = item_selecionado.data(Qt.UserRole)
        
        # Confirmar remoção
        resposta = QMessageBox.question(
            self, "Confirmar Remoção", 
            "Tem certeza que deseja remover esta imagem?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            sucesso, mensagem = self.db.excluir_imagem(imagem_id)
            
            if sucesso:
                self.carregar_imagens()  # Atualizar grid
                QMessageBox.information(self, "Sucesso", mensagem)
                return True
            else:
                QMessageBox.warning(self, "Erro", mensagem)
        
        return False