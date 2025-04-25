#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementação da tela de gerenciamento de usuários para o Sistema de Manutenção.
"""

import re
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QFormLayout, QLabel, QLineEdit, QComboBox, 
                            QPushButton, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt

class GerenciadorUsuarios(QDialog):
    """Classe para a janela de gerenciamento de usuários."""
    
    def __init__(self, db, usuario_id):
        """Inicializa a janela de gerenciamento de usuários."""
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.usuario_selecionado = None
        self.init_ui()
        self.carregar_usuarios()
    
    def init_ui(self):
        """Configura a interface de usuário."""
        self.setWindowTitle("Gerenciamento de Usuários")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Formulário para cadastro/edição
        form_group = QGroupBox("Cadastro de Usuário")
        form_layout = QFormLayout()
        
        self.nome_input = QLineEdit()
        self.usuario_input = QLineEdit()
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.cargo_combo = QComboBox()
        self.cargo_combo.addItems(["Usuário", "Administrador"])
        
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Usuário:", self.usuario_input)
        form_layout.addRow("Senha:", self.senha_input)
        form_layout.addRow("Cargo:", self.cargo_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.cadastrar_btn = QPushButton("Cadastrar")
        self.cadastrar_btn.clicked.connect(self.cadastrar_usuario)
        
        self.atualizar_btn = QPushButton("Atualizar")
        self.atualizar_btn.clicked.connect(self.atualizar_usuario)
        self.atualizar_btn.setEnabled(False)
        
        self.excluir_btn = QPushButton("Excluir")
        self.excluir_btn.clicked.connect(self.excluir_usuario)
        self.excluir_btn.setEnabled(False)
        
        self.limpar_btn = QPushButton("Limpar")
        self.limpar_btn.clicked.connect(self.limpar_formulario)
        
        btn_layout.addWidget(self.cadastrar_btn)
        btn_layout.addWidget(self.atualizar_btn)
        btn_layout.addWidget(self.excluir_btn)
        btn_layout.addWidget(self.limpar_btn)
        
        layout.addLayout(btn_layout)
        
        # Tabela de usuários
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Usuário", "Cargo", "Status"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.cellClicked.connect(self.selecionar_usuario)
        
        layout.addWidget(self.tabela)
    
    def carregar_usuarios(self):
        """Carrega a lista de usuários do banco de dados para a tabela."""
        usuarios = self.db.obter_usuarios()
        self.tabela.setRowCount(0)
        
        for row_idx, usuario in enumerate(usuarios):
            id_usuario, nome, username, cargo, ativo = usuario
            
            self.tabela.insertRow(row_idx)
            self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(id_usuario)))
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(username))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(cargo))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem("Ativo" if ativo else "Inativo"))
    
    def selecionar_usuario(self, row, column):
        """Seleciona um usuário da tabela para edição."""
        id_usuario = int(self.tabela.item(row, 0).text())
        nome = self.tabela.item(row, 1).text()
        usuario = self.tabela.item(row, 2).text()
        cargo = self.tabela.item(row, 3).text()
        status = self.tabela.item(row, 4).text()
        
        # Preencher formulário
        self.nome_input.setText(nome)
        self.usuario_input.setText(usuario)
        self.senha_input.setText("")  # Senha não é preenchida
        self.cargo_combo.setCurrentText(cargo)
        
        # Habilitar botões de edição/exclusão
        self.usuario_selecionado = id_usuario
        self.atualizar_btn.setEnabled(True)
        self.excluir_btn.setEnabled(status == "Ativo")
        self.cadastrar_btn.setEnabled(False)
    
    def validar_formulario(self, modo="cadastro"):
        """Valida os dados do formulário antes de prosseguir."""
        nome = self.nome_input.text()
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()
        
        if not nome or not usuario:
            QMessageBox.warning(self, "Erro", "Preencha os campos Nome e Usuário")
            return False
        
        if modo == "cadastro" and not senha:
            QMessageBox.warning(self, "Erro", "Digite uma senha")
            return False
        
        # Validar senha apenas se foi fornecida
        if senha:
            # Validar requisitos de senha: mínimo 5 caracteres, 1 caractere especial, 1 número
            if len(senha) < 5:
                QMessageBox.warning(self, "Erro", "A senha deve ter no mínimo 5 caracteres")
                return False
            
            tem_especial = re.search(r'[!@#$%^&*(),.?":{}|<>]', senha)
            tem_numero = re.search(r'\d', senha)
            
            if not tem_especial or not tem_numero:
                QMessageBox.warning(self, "Erro", "A senha deve conter pelo menos 1 caractere especial e 1 número")
                return False
        
        return True
    
    def cadastrar_usuario(self):
        """Cadastra um novo usuário no sistema."""
        if not self.validar_formulario():
            return
        
        nome = self.nome_input.text()
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()
        cargo = self.cargo_combo.currentText()
        
        sucesso, mensagem = self.db.adicionar_usuario(nome, usuario, senha, cargo)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.limpar_formulario()
            self.carregar_usuarios()
            # Registrar log
            self.db.registrar_log(self.usuario_id, "Criação", f"Criou usuário {usuario}")
        else:
            QMessageBox.warning(self, "Erro", mensagem)
    
    def atualizar_usuario(self):
        """Atualiza os dados de um usuário existente."""
        if not self.usuario_selecionado:
            return
        
        if not self.validar_formulario(modo="atualizar"):
            return
        
        nome = self.nome_input.text()
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()
        cargo = self.cargo_combo.currentText()
        
        sucesso, mensagem = self.db.atualizar_usuario(
            self.usuario_selecionado, nome, usuario, senha, cargo
        )
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.limpar_formulario()
            self.carregar_usuarios()
            # Registrar log
            self.db.registrar_log(self.usuario_id, "Atualização", f"Atualizou usuário {usuario}")
        else:
            QMessageBox.warning(self, "Erro", mensagem)
    
    def excluir_usuario(self):
        """Desativa (não exclui) um usuário existente."""
        if not self.usuario_selecionado:
            return
        
        # Confirmar exclusão
        resposta = QMessageBox.question(
            self, "Confirmar Exclusão", 
            "Tem certeza que deseja excluir este usuário? Esta ação apenas marca o usuário como inativo.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            usuario = self.usuario_input.text()
            sucesso, mensagem = self.db.desativar_usuario(self.usuario_selecionado)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.limpar_formulario()
                self.carregar_usuarios()
                # Registrar log
                self.db.registrar_log(self.usuario_id, "Exclusão", f"Desativou usuário {usuario}")
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def limpar_formulario(self):
        """Limpa os campos do formulário e reseta o estado dos botões."""
        self.nome_input.clear()
        self.usuario_input.clear()
        self.senha_input.clear()
        self.cargo_combo.setCurrentIndex(0)
        
        self.usuario_selecionado = None
        self.atualizar_btn.setEnabled(False)
        self.excluir_btn.setEnabled(False)
        self.cadastrar_btn.setEnabled(True)