#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementação da tela de login para o Sistema de Manutenção.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

from .main_window import MainWindow

class LoginWindow(QMainWindow):
    """Classe para a janela de login."""
    
    def __init__(self, db):
        """Inicializa a janela de login."""
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        """Configura a interface de usuário."""
        self.setWindowTitle("Login - Sistema de Manutenção")
        self.setFixedSize(400, 200)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Formulário de login
        form_layout = QFormLayout()
        
        self.usuario_input = QLineEdit()
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Usuário:", self.usuario_input)
        form_layout.addRow("Senha:", self.senha_input)
        
        layout.addLayout(form_layout)
        
        # Botão de login
        login_btn = QPushButton("Entrar")
        login_btn.clicked.connect(self.tentar_login)
        layout.addWidget(login_btn)
        
        # Status da conexão com o banco
        status_label = QLabel("Banco de dados: Conectado" if self.db.conn else "Banco de dados: Erro")
        layout.addWidget(status_label)
        
        # Definir enter para tentar login
        self.senha_input.returnPressed.connect(login_btn.click)
    
    def tentar_login(self):
        """Tenta autenticar o usuário com as credenciais fornecidas."""
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()
        
        if not usuario or not senha:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos")
            return
        
        resultado = self.db.autenticar_usuario(usuario, senha)
        
        if resultado:
            usuario_id, nome, cargo = resultado
            self.main_window = MainWindow(self.db, usuario_id, nome, cargo)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha incorretos ou usuário inativo")